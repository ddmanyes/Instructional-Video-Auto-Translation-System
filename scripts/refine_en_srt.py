"""
refine_en_srt.py
================
英文字幕兩段式精修工具（polish + merge 合體版）

第一階段 — 規則清理 (polish)：
  · 移除句首贅詞 (Then / Just / So / Also / Well …)
  · 刪除中英混雜殘留中文（標記後由 AI 翻譯）
  · 修正「Pancreas our pancreas」等冗餘大小寫重複
  · 清理多餘空白

第二階段 — AI 潤色 (可選)：
  · 用 Gemini CLI 翻譯殘留中文並修飾奇怪語句
  · 預設只處理含中文的行（--ai-all 可全量處理）

第三階段 — 短句合併 (merge)：
  · 相鄰間隔 <= gap_ms 的碎片字幕合併成完整句子
  · 合併後字數 >= min_words 才停止
  · 不超過 max_words 上限
  · 時間軸：start 取最早，end 取最晚，差異 = 0 ms

用法:
    # 完整流程（預設：只 AI 修正含中文的行）
    uv run python scripts/refine_en_srt.py \\
        --file "output/subtitles/xxx_corrected_en.srt"

    # 跳過 AI（純規則 + 合併，最快）
    uv run python scripts/refine_en_srt.py \\
        --file "output/subtitles/xxx_corrected_en.srt" --no-ai

    # AI 全量潤色（最徹底，較慢）
    uv run python scripts/refine_en_srt.py \\
        --file "output/subtitles/xxx_corrected_en.srt" --ai-all

    # 自訂合併參數
    uv run python scripts/refine_en_srt.py \\
        --file "output/subtitles/xxx_corrected_en.srt" \\
        --gap 500 --min-words 5 --max-words 20

    # 直接覆蓋原始檔
    uv run python scripts/refine_en_srt.py \\
        --file "output/subtitles/xxx_corrected_en.srt" --overwrite
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# SRT 工具
# ══════════════════════════════════════════════════════════════════════════════

SRT_PAT = re.compile(
    r"(\d+)\r?\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\r?\n"
    r"(.*?)(?=\r?\n\r?\n|\Z)",
    re.DOTALL,
)
SENTENCE_END = re.compile(r"[.!?]\s*$")
CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


def _to_ms(ts: str) -> int:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3_600_000 + int(m) * 60_000 + int(s) * 1_000 + int(ms)


def _from_ms(ms: int) -> str:
    h = ms // 3_600_000; ms %= 3_600_000
    m = ms // 60_000;    ms %= 60_000
    s = ms // 1_000;     ms %= 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(text: str) -> list[dict]:
    return [
        {
            "start_ms": _to_ms(m.group(2)),
            "end_ms":   _to_ms(m.group(3)),
            "text":     m.group(4).strip(),
        }
        for m in SRT_PAT.finditer(text)
    ]


def write_srt(blocks: list[dict], path: Path) -> None:
    # 使用 str(path) 避免 Windows 含 & 符號路徑在 Path.open() 下的問題
    with open(str(path), "w", encoding="utf-8-sig", newline="\n") as f:
        for i, b in enumerate(blocks, 1):
            f.write(
                f"{i}\n"
                f"{_from_ms(b['start_ms'])} --> {_from_ms(b['end_ms'])}\n"
                f"{b['text']}\n\n"
            )


def _read_srt_file(path: Path) -> str:
    """自動偵測 BOM，相容 UTF-8 / UTF-8-BOM / UTF-16 的 SRT 檔案。"""
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-8", "cp950", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


# ══════════════════════════════════════════════════════════════════════════════
# 第一階段：規則清理 (polish)
# ══════════════════════════════════════════════════════════════════════════════

_FILLER_STARTERS = [
    r"Then\b[,\s]*",
    r"Just\b[,\s]*",
    r"So\b[,\s]*",
    r"Well\b[,\s]*",
    r"Okay\b[,\s]*",
    r"OK\b[,\s]*",
    r"Also\b[,\s]*",
    r"And also\b[,\s]*",
    r"After that\b[,\s]*",
    r"So then\b[,\s]*",
    r"Right\b[,\s]*",
    r"Now\b[,\s]*",
    r"Alright\b[,\s]*",
    r"Therefore\b[,\s]*",
]

_REDUNDANT_PAIRS = [
    (
        r"\b(Pancreas|Duodenum|Esophagus|Gallbladder|Rectum|Jejunum|Ileum|Stomach|Liver)\b"
        r"[\s,]+(our|this|the|is our|is the)\s+\1",
        lambda m: m.group(1),
        re.IGNORECASE,
    ),
    (
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+([a-z]+(?:\s+[a-z]+)*)\b",
        lambda m: m.group(1) if m.group(1).lower() == m.group(2).lower() else m.group(0),
        0,
    ),
]


def _strip_filler(text: str) -> str:
    lines = text.split("\n")
    out = []
    for line in lines:
        for pat in _FILLER_STARTERS:
            line = re.sub(r"^" + pat, "", line, flags=re.IGNORECASE).strip()
        if line:
            line = line[0].upper() + line[1:]
        out.append(line)
    return "\n".join(out)


def _strip_redundant(text: str) -> str:
    for pat, repl, flags in _REDUNDANT_PAIRS:
        text = re.sub(pat, repl, text, flags=flags if flags else 0)
    return text


def _is_mostly_chinese(text: str) -> bool:
    cjk_n = len(CJK.findall(text))
    alpha_n = len(re.findall(r"[a-zA-Z\u4e00-\u9fff]", text))
    return alpha_n > 0 and cjk_n / alpha_n > 0.4


def rule_clean(blocks: list[dict]) -> tuple[list[dict], list[int]]:
    """規則清理，回傳 (cleaned_blocks, chinese_flagged_indices)"""
    result = []
    flagged = []
    for i, b in enumerate(blocks):
        text = b["text"]
        if _is_mostly_chinese(text):
            flagged.append(i)
            result.append({**b, "_chinese": True})
            continue
        text = _strip_filler(text)
        text = _strip_redundant(text)
        text = re.sub(r" {2,}", " ", text).strip()
        result.append({**b, "text": text})
    return result, flagged


# ══════════════════════════════════════════════════════════════════════════════
# 第二階段：Gemini AI 潤色
# ══════════════════════════════════════════════════════════════════════════════

_AI_PROMPT = (
    "You are a professional medical subtitle editor for university-level physiology lectures.\n"
    "Polish these English subtitles. Each line is one subtitle entry.\n\n"
    "Rules:\n"
    "1. Remove filler words at sentence start: 'Then', 'Just', 'So', 'Also', 'Well', 'Okay'.\n"
    "2. Fix awkward literal translations. Rewrite naturally in academic English.\n"
    "3. If a line is in Chinese or mixed Chinese-English, TRANSLATE it to English.\n"
    "4. Preserve medical terms exactly (e.g. peristalsis, duodenum, portal vein).\n"
    "5. Do NOT merge or split entries — output SAME number of lines as input.\n"
    "6. Keep each subtitle concise and screen-readable.\n"
    "7. Output ONLY a JSON array of strings, no other text.\n"
    "8. JSON array length MUST equal input line count.\n"
)


def _parse_json_array(raw: str) -> list[str]:
    raw = raw.strip()
    # 先嘗試直接解析
    try:
        payload = json.loads(raw)
        if isinstance(payload, list):
            return [str(x) for x in payload]
        # Gemini 包了一層 dict（candidates）
        if isinstance(payload, dict):
            candidates = payload.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [{}])
                text = parts[0].get("text", "") if parts else ""
                inner = json.loads(text.strip())
                if isinstance(inner, list):
                    return [str(x) for x in inner]
    except Exception:
        pass
    # 在回應中搜尋 JSON 陣列
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(0))
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
    return []


def _call_gemini(
    lines: list[str],
    batch_size: int,
    timeout: int,
    command: str | None,
    command_args: list[str] | None,
    model: str | None,
) -> list[str]:
    base_cmd = [command or "pwsh"]
    if command_args:
        base_cmd.extend(command_args)
    elif command in (None, "pwsh", "powershell"):
        # fallback: 直接呼叫 gemini
        base_cmd = ["gemini"]

    outputs: list[str] = []
    for i in range(0, len(lines), batch_size):
        batch = lines[i : i + batch_size]
        cmd = list(base_cmd) + ["--output-format", "json", "--prompt", _AI_PROMPT]
        if model:
            cmd += ["--model", model]

        logger.info("  AI 批次 %d/%d (%d 條)…", i // batch_size + 1, (len(lines) - 1) // batch_size + 1, len(batch))
        try:
            r = subprocess.run(
                cmd,
                input="\n".join(batch),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
            )
            parsed = _parse_json_array(r.stdout or "")
            if len(parsed) == len(batch):
                outputs.extend(parsed)
            else:
                logger.warning("  AI 回傳行數不符（預期 %d，實際 %d），改用原文", len(batch), len(parsed))
                outputs.extend(batch)
        except Exception as e:
            logger.error("  Gemini 失敗: %s，改用原文", e)
            outputs.extend(batch)

    return outputs


def ai_polish(
    blocks: list[dict],
    only_flagged: bool,
    batch_size: int,
    timeout: int,
    command: str | None,
    command_args: list[str] | None,
    model: str | None,
) -> list[dict]:
    indices = [i for i, b in enumerate(blocks) if not only_flagged or b.get("_chinese")]
    if not indices:
        logger.info("  沒有需要 AI 潤色的條目，略過。")
        return blocks

    texts = [blocks[i]["text"] for i in indices]
    logger.info("送出 %d 條字幕給 Gemini…", len(texts))
    results = _call_gemini(texts, batch_size, timeout, command, command_args, model)

    out = list(blocks)
    for idx, new_text in zip(indices, results):
        out[idx] = {**out[idx], "text": new_text, "_chinese": False}
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 第三階段：短句合併 (merge)
# ══════════════════════════════════════════════════════════════════════════════

def _join(texts: list[str]) -> str:
    if not texts:
        return ""
    result = texts[0]
    for t in texts[1:]:
        if not t:
            continue
        if not result:
            result = t
            continue
        ends_sentence = result[-1] in ".!?"
        result = result.rstrip() + " " + (t if ends_sentence else t[0].lower() + t[1:] if t else t)
    return result.strip()


def merge_blocks(
    blocks: list[dict],
    gap_ms: int,
    min_words: int,
    max_words: int,
) -> list[dict]:
    merged: list[dict] = []
    i = 0
    while i < len(blocks):
        cur = blocks[i]
        grp_texts = [cur["text"]]
        grp_start = cur["start_ms"]
        grp_end   = cur["end_ms"]

        while True:
            combined = _join(grp_texts)
            words    = len(combined.split())
            # 夠長且到句末 → 停止
            if words >= min_words and SENTENCE_END.search(combined):
                break
            j = i + len(grp_texts)
            if j >= len(blocks):
                break
            nxt = blocks[j]
            if nxt["start_ms"] - grp_end > gap_ms:
                break
            preview = _join(grp_texts + [nxt["text"]])
            if len(preview.split()) > max_words:
                break
            grp_texts.append(nxt["text"])
            grp_end = nxt["end_ms"]

        merged.append({"start_ms": grp_start, "end_ms": grp_end, "text": _join(grp_texts)})
        i += len(grp_texts)
    return merged


# ══════════════════════════════════════════════════════════════════════════════
# 公開函式：供 main.py 直接呼叫
# ══════════════════════════════════════════════════════════════════════════════

def refine_srt(
    srt_path: str | Path,
    output_path: str | Path | None = None,
    suffix: str = "_refined",
    overwrite: bool = False,
    # AI 選項
    no_ai: bool = False,
    ai_all: bool = False,
    batch_size: int = 8,
    timeout: int = 180,
    model: str | None = None,
    command: str | None = None,
    command_args: list[str] | None = None,
    # 合併選項
    gap_ms: int = 300,
    min_words: int = 7,
    max_words: int = 18,
) -> str:
    """
    對英文 SRT 字幕進行三段式精修：規則清理 → AI 潤色 → 短句合併。

    Returns:
        輸出檔案的絕對路徑字串。
    """
    srt_path = Path(srt_path)

    if output_path:
        out_path = Path(output_path)
    elif overwrite:
        out_path = srt_path
    else:
        out_path = srt_path.parent / f"{srt_path.stem}{suffix}{srt_path.suffix}"

    if out_path.exists() and not overwrite:
        logger.info("⏭️  輸出已存在，跳過精修: %s", out_path.name)
        logger.info("    如需重新生成，請刪除現有檔案或加上 --overwrite。")
        return str(out_path)

    logger.info("── [精修] 讀取: %s", srt_path.name)
    blocks = parse_srt(_read_srt_file(srt_path))
    orig_count = len(blocks)
    logger.info("   原始字幕數: %d", orig_count)

    # ── 第一階段：規則清理
    logger.info("── [精修] 第一階段：規則清理…")
    blocks, flagged = rule_clean(blocks)
    logger.info("   規則清理完成，標記含中文: %d 條", len(flagged))

    # ── 第二階段：AI 潤色
    if not no_ai:
        logger.info("── [精修] 第二階段：AI 潤色…")
        blocks = ai_polish(
            blocks,
            only_flagged=(not ai_all),
            batch_size=batch_size,
            timeout=timeout,
            command=command or config.EN_PROOFREAD_CONFIG.get("command"),
            command_args=command_args or config.EN_PROOFREAD_CONFIG.get("command_args"),
            model=model or config.EN_PROOFREAD_CONFIG.get("model") or None,
        )
    else:
        logger.info("── [精修] 第二階段：略過 AI 潤色（--no-ai）")

    # ── 第三階段：短句合併
    logger.info("── [精修] 第三階段：短句合併（gap=%dms, min=%d字, max=%d字）…", gap_ms, min_words, max_words)
    # 移除內部標記欄位後再合併
    clean = [{k: v for k, v in b.items() if not k.startswith("_")} for b in blocks]
    merged = merge_blocks(clean, gap_ms=gap_ms, min_words=min_words, max_words=max_words)
    logger.info("   合併後字幕數: %d（壓縮 %.1fx）", len(merged), orig_count / len(merged))

    # ── 輸出
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_srt(merged, out_path)
    logger.info("✅ [精修] 完成: %s", out_path)
    return str(out_path)


# ══════════════════════════════════════════════════════════════════════════════
# CLI 入口
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="英文字幕三段式精修：規則清理 → AI 潤色 → 短句合併",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", "-f", required=True, help="輸入 SRT 檔案路徑")
    parser.add_argument("--suffix", "-s", default="_refined", help="輸出後綴（預設 _refined）")
    parser.add_argument("--overwrite", action="store_true", help="覆蓋原始檔案")
    parser.add_argument("--no-ai",   action="store_true", help="跳過 AI 潤色")
    parser.add_argument("--ai-all",  action="store_true", help="AI 處理所有行（非僅含中文行）")
    parser.add_argument("--batch-size", type=int, default=8,  help="AI 每批次條數（預設 8）")
    parser.add_argument("--timeout",    type=int, default=180, help="AI 呼叫超時秒數（預設 180）")
    parser.add_argument("--model",      type=str, default="",  help="Gemini 模型名稱")
    parser.add_argument("--gap",        type=int, default=300, help="合併間隔容忍(ms)（預設 300）")
    parser.add_argument("--min-words",  type=int, default=7,   help="合併目標最低字數（預設 7）")
    parser.add_argument("--max-words",  type=int, default=18,  help="合併後字數上限（預設 18）")
    args = parser.parse_args()

    refine_srt(
        srt_path=args.file,
        suffix=args.suffix,
        overwrite=args.overwrite,
        no_ai=args.no_ai,
        ai_all=args.ai_all,
        batch_size=args.batch_size,
        timeout=args.timeout,
        model=args.model or None,
        gap_ms=args.gap,
        min_words=args.min_words,
        max_words=args.max_words,
    )


if __name__ == "__main__":
    main()
