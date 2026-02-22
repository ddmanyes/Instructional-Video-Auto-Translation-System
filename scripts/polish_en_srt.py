"""
polish_en_srt.py
================
英文字幕優化腳本 – 針對 AI 翻譯後的英文字幕進行兩階段處理：

第一階段（規則清理）：
  - 移除句首贅詞 (Then, Just, So, Also, Well, Okay...)
  - 移除中英混雜的行（殘留中文字元）→ 以空字串標記，交給 AI 處理
  - 修正常見重複詞 (e.g. "Gallbladder gallbladder" → "Gallbladder")
  - 清理多餘空白

第二階段（AI 潤色）— 需要 Gemini CLI：
  - 批次送給 Gemini，以生理醫學教學語境重寫英文
  - 保留原始時間軸，不合併也不拆分字幕

用法:
    uv run python scripts/polish_en_srt.py --file "output/subtitles/110-Gastrointestinal system-I &II_corrected_en.srt"
    uv run python scripts/polish_en_srt.py --file "xxx_en.srt" --no-ai   # 只做規則清理
    uv run python scripts/polish_en_srt.py --file "xxx_en.srt" --suffix "_polished"
"""

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path

# ─── 設定 Python 搜尋路徑 ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── 規則常數 ─────────────────────────────────────────────────────────────────

# 句首刪除的贅詞（大小寫不敏感，以下會轉成 regex）
FILLER_STARTERS = [
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

# 贅詞在句中直接刪除（用 {word} 格式，會被 re.sub）
INLINE_FILLERS = [
    r"\bthis\s+(?=\w+\s+function\b)",   # "this endocrine function" → "endocrine function"
    r"\byour\b",                         # 口語 "your" 過多
]

# 常見大小寫混合冗餘（已在翻譯時夾雜英文原詞的情況）
# 例如 "This Stomach is right here in our stomach." → "The stomach is located here."
# 以下的 pair 用 regex 匹配重複
REDUNDANT_PAIRS = [
    # 形如 "Pancreas our pancreas" / "Gallbladder the gallbladder"
    (
        r"\b(Pancreas|Duodenum|Esophagus|Gallbladder|Rectum|Jejunum|Ileum|Stomach|Liver)\b"
        r"[\s,]+(our|this|the|is our|is the)\s+\1",
        lambda m: m.group(1),
        re.IGNORECASE,
    ),
    # 形如 "Ascending Colon, ascending colon" → "Ascending Colon"
    (
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+([a-z]+(?:\s+[a-z]+)*)\b",
        lambda m: m.group(1) if m.group(1).lower() == m.group(2).lower() else m.group(0),
        0,
    ),
]

# 中文字元偵測
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


# ─── SRT 解析 / 輸出 ───────────────────────────────────────────────────────────

def parse_srt(text: str) -> list[dict]:
    """解析 SRT 字串，回傳 list of {index, start, end, text}"""
    pattern = re.compile(
        r"(\d+)\r?\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\r?\n(.*?)(?=\r?\n\r?\n|\Z)",
        re.DOTALL,
    )
    blocks = []
    for m in pattern.finditer(text):
        blocks.append(
            {
                "index": m.group(1),
                "start": m.group(2),
                "end": m.group(3),
                "text": m.group(4).strip(),
            }
        )
    return blocks


def write_srt(blocks: list[dict], output_path: Path):
    with output_path.open("w", encoding="utf-8") as f:
        for b in blocks:
            f.write(f"{b['index']}\n{b['start']} --> {b['end']}\n{b['text']}\n\n")
    logger.info(f"已寫入: {output_path}")


# ─── 第一階段：規則清理 ─────────────────────────────────────────────────────────

def _clean_filler_starters(text: str) -> str:
    """刪除句首贅詞（每行處理）"""
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line
        for pattern in FILLER_STARTERS:
            stripped = re.sub(r"^" + pattern, "", stripped, flags=re.IGNORECASE).strip()
        # 首字母大寫
        if stripped:
            stripped = stripped[0].upper() + stripped[1:]
        result.append(stripped)
    return "\n".join(result)


def _clean_redundant_pairs(text: str) -> str:
    for pat, repl, flags in REDUNDANT_PAIRS:
        text = re.sub(pat, repl, text, flags=flags if flags else 0)
    return text


def _is_chinese_only(text: str) -> bool:
    """若一段字幕幾乎都是中文字，回傳 True"""
    cjk_count = len(CJK_PATTERN.findall(text))
    total_alpha = len(re.findall(r"[a-zA-Z\u4e00-\u9fff]", text))
    if total_alpha == 0:
        return False
    return cjk_count / total_alpha > 0.4


def rule_clean(blocks: list[dict]) -> tuple[list[dict], list[int]]:
    """
    對所有字幕做規則清理。
    回傳 (cleaned_blocks, chinese_indices)
    chinese_indices 是含有過多中文的字幕索引，供 AI 階段二修復。
    """
    cleaned = []
    chinese_indices = []

    for i, b in enumerate(blocks):
        text = b["text"]

        # 標記中英混雜
        if _is_chinese_only(text):
            chinese_indices.append(i)
            cleaned.append({**b, "text": text, "_flagged_chinese": True})
            continue

        # 清理贅詞
        text = _clean_filler_starters(text)
        text = _clean_redundant_pairs(text)

        # 清理多餘空白
        text = re.sub(r" {2,}", " ", text).strip()

        cleaned.append({**b, "text": text})

    if chinese_indices:
        logger.info(f"偵測到 {len(chinese_indices)} 條含中文的字幕，將交給 AI 翻譯修正。")

    return cleaned, chinese_indices


# ─── 第二階段：Gemini AI 潤色 ──────────────────────────────────────────────────

GEMINI_PROMPT = (
    "You are a professional medical subtitle editor for university-level physiology lectures.\n"
    "Your task is to POLISH a batch of English subtitles. Each subtitle is one entry.\n\n"
    "Rules:\n"
    "1. Remove unnecessary filler words at sentence start: 'Then', 'Just', 'So', 'Also', 'Well', 'Okay' etc.\n"
    "2. Fix awkward, overly literal translations from Chinese. Rewrite naturally in academic English.\n"
    "3. If a line is in Chinese or mixed Chinese-English, TRANSLATE it fully into English.\n"
    "4. Preserve medical terminology exactly (e.g. peristalsis, duodenum, portal vein).\n"
    "5. Do NOT merge or split entries — output must have the SAME number of lines as input.\n"
    "6. Keep each subtitle SHORT and readable (suitable for on-screen display).\n"
    "7. Do NOT add any commentary. Output ONLY a JSON array of strings.\n"
    "8. The JSON array length MUST equal the input line count.\n\n"
    "Input: one subtitle text per line\n"
    "Output: JSON array like [\"...\", \"...\"]"
)


def _call_gemini(
    lines: list[str],
    batch_size: int = 8,
    timeout: int = 180,
    command: str | None = None,
    command_args: list[str] | None = None,
    model: str | None = None,
) -> list[str]:
    """呼叫 Gemini CLI 批次處理，回傳與輸入等長的修訂後字串列表"""
    all_outputs = []

    gemini_cmd = [command or "npx"]
    if command_args:
        gemini_cmd.extend(command_args)
    elif not command:
        # fallback: default cross-platform npx command
        gemini_cmd.extend(["-y", "@google/generative-ai-cli"])

    for i in range(0, len(lines), batch_size):
        batch = lines[i : i + batch_size]
        stdin_text = "\n".join(batch)

        cmd = list(gemini_cmd)
        cmd.extend(["--output-format", "json", "--prompt", GEMINI_PROMPT])
        if model:
            cmd.extend(["--model", model])

        logger.info(f"  AI 校稿批次 {i // batch_size + 1}: 共 {len(batch)} 條...")
        try:
            result = subprocess.run(
                cmd,
                input=stdin_text,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr[:400])

            raw = result.stdout.strip()
            parsed = _parse_json_array(raw, len(batch))

            if parsed and len(parsed) == len(batch):
                all_outputs.extend(parsed)
            else:
                logger.warning(f"  AI 回傳行數不符（預期 {len(batch)}，實際 {len(parsed)}），改用原文")
                all_outputs.extend(batch)

        except Exception as e:
            logger.error(f"  Gemini 呼叫失敗: {e}，改用原文")
            all_outputs.extend(batch)

    return all_outputs


def _parse_json_array(raw: str, expected: int) -> list[str]:
    """從 Gemini 回傳的 JSON 中提取字串陣列"""
    try:
        # Gemini CLI 有時回傳外層包了一個 meta dict
        payload = json.loads(raw)
        if isinstance(payload, list):
            return [str(x) for x in payload]
        if isinstance(payload, dict):
            # 嘗試從 candidates 中提取
            candidates = payload.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                inner = json.loads(text.strip())
                if isinstance(inner, list):
                    return [str(x) for x in inner]
    except Exception:
        pass

    # fallback：嘗試在 raw 中尋找 JSON 陣列
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(0))
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass

    return []


def ai_polish(
    blocks: list[dict],
    batch_size: int = 8,
    timeout: int = 180,
    command: str | None = None,
    command_args: list[str] | None = None,
    model: str | None = None,
    only_flagged: bool = False,
) -> list[dict]:
    """
    用 Gemini 對字幕做 AI 潤色。
    only_flagged=True 時只處理帶 _flagged_chinese 標記的條目。
    """
    indices_to_polish = []
    texts_to_polish = []

    for i, b in enumerate(blocks):
        if only_flagged and not b.get("_flagged_chinese"):
            continue
        indices_to_polish.append(i)
        texts_to_polish.append(b["text"])

    if not texts_to_polish:
        logger.info("  沒有需要 AI 潤色的條目。")
        return blocks

    logger.info(f"送出 {len(texts_to_polish)} 條字幕給 Gemini AI 進行潤色...")
    results = _call_gemini(
        texts_to_polish,
        batch_size=batch_size,
        timeout=timeout,
        command=command,
        command_args=command_args,
        model=model,
    )

    polished = list(blocks)
    for idx, new_text in zip(indices_to_polish, results):
        polished[idx] = {**polished[idx], "text": new_text, "_flagged_chinese": False}

    return polished


# ─── 主程式 ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="英文字幕規則清理 + AI 潤色工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", "-f", required=True, help="輸入的英文 SRT 檔案路徑")
    parser.add_argument("--suffix", "-s", default="_polished", help="輸出檔案的後綴（預設: _polished）")
    parser.add_argument("--overwrite", action="store_true", help="直接覆蓋原始檔案")
    parser.add_argument("--no-ai", action="store_true", help="跳過 Gemini AI 潤色，只做規則清理")
    parser.add_argument("--ai-all", action="store_true", help="讓 AI 處理所有行（預設只處理含中文的行）")
    parser.add_argument("--batch-size", type=int, default=8, help="AI 每批次處理的字幕條數（預設 8）")
    parser.add_argument("--model", type=str, default="", help="Gemini 模型名稱（留空使用 CLI 預設）")
    parser.add_argument("--timeout", type=int, default=180, help="每批次 AI 呼叫的超時秒數（預設 180）")
    args = parser.parse_args()

    srt_path = Path(args.file)
    if not srt_path.exists():
        logger.error(f"找不到檔案: {srt_path}")
        sys.exit(1)

    # 決定輸出路徑
    if args.overwrite:
        output_path = srt_path
    else:
        output_path = srt_path.parent / f"{srt_path.stem}{args.suffix}{srt_path.suffix}"

    if output_path.exists() and not args.overwrite:
        logger.info(f"⏭️  輸出檔案已存在，跳過: {output_path}")
        logger.info("    若要重新生成，請加上 --overwrite 或刪除現有檔案。")
        sys.exit(0)

    # ── 讀取 ──
    logger.info(f"讀取: {srt_path}")
    content = srt_path.read_text(encoding="utf-8")
    blocks = parse_srt(content)
    logger.info(f"共解析 {len(blocks)} 條字幕")

    # ── 第一階段：規則清理 ──
    logger.info("── 第一階段：規則清理 ──")
    blocks, chinese_indices = rule_clean(blocks)
    logger.info(f"規則清理完成（{len(chinese_indices)} 條標記為含中文）")

    # ── 第二階段：AI 潤色 ──
    if not args.no_ai:
        logger.info("── 第二階段：Gemini AI 潤色 ──")
        # 讀取 config 的 Gemini 設定
        cmd = config.EN_PROOFREAD_CONFIG.get("command", "npx")
        cmd_args = config.EN_PROOFREAD_CONFIG.get("command_args", [])
        model = args.model or config.EN_PROOFREAD_CONFIG.get("model", "") or None

        blocks = ai_polish(
            blocks,
            batch_size=args.batch_size,
            timeout=args.timeout,
            command=cmd,
            command_args=cmd_args if cmd_args else None,
            model=model,
            only_flagged=(not args.ai_all),
        )
    else:
        logger.info("── 已跳過 AI 潤色（--no-ai）──")

    # 移除內部標記欄位
    clean_blocks = [{k: v for k, v in b.items() if not k.startswith("_")} for b in blocks]

    # ── 輸出 ──
    write_srt(clean_blocks, output_path)
    logger.info(f"✅ 完成！輸出: {output_path}")

    # 統計
    total = len(clean_blocks)
    logger.info(f"   共處理 {total} 條字幕")
    if chinese_indices:
        logger.info(f"   其中 {len(chinese_indices)} 條原含中文，已修正")


if __name__ == "__main__":
    main()
