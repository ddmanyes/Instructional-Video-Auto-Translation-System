"""
merge_zh_srt.py
===============
翻譯前的中文字幕短句合併工具。

合併規則：
  1. 相鄰字幕時間間隔 <= gap_ms（預設 400ms）
  2. 目前累積的字元數 < min_chars（預設 8）時繼續往後合併
  3. 合併後不得超過 max_chars（預設 35）字元
  4. 遇到「.」「？」「！」「。」「？」「！」等句尾符號 → 強制斷句，不繼續合併

合理邏輯：
  中文贅詞（那、然後、所以…）在翻譯後才去除，這裡只處理「太短、語意不完整」的碎片。

用法：
    uv run python scripts/merge_zh_srt.py --file "output/subtitles/xxx_zh.srt"
    uv run python scripts/merge_zh_srt.py --file "..." --gap 500 --min-chars 10 --overwrite
"""

import argparse
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── SRT 解析 ────────────────────────────────────────────────────────────────

SRT_PATTERN = re.compile(
    r"(\d+)\r?\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\r?\n"
    r"(.*?)(?=\r?\n\r?\n|\Z)",
    re.DOTALL,
)

# 句尾強制斷句符號
SENTENCE_END = re.compile(r"[。？！.?!…]$")

# 中文字元計算（只計中文字，排除英文/數字佔位）
CJK = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


def ts_to_ms(ts: str) -> int:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


def ms_to_ts(ms: int) -> str:
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(text: str) -> list[dict]:
    blocks = []
    for m in SRT_PATTERN.finditer(text):
        blocks.append(
            {
                "index": int(m.group(1)),
                "start": m.group(2),
                "end": m.group(3),
                "start_ms": ts_to_ms(m.group(2)),
                "end_ms": ts_to_ms(m.group(3)),
                "text": m.group(4).strip(),
            }
        )
    return blocks


def write_srt(blocks: list[dict], path: Path):
    with path.open("w", encoding="utf-8") as f:
        for i, b in enumerate(blocks, 1):
            f.write(f"{i}\n{b['start']} --> {b['end']}\n{b['text']}\n\n")
    logger.info("✅ 已寫入: %s", path)


# ─── 合併邏輯 ─────────────────────────────────────────────────────────────────

def zh_char_count(text: str) -> int:
    """計算中文字元數（不含英文、空白、標點）"""
    return len(CJK.findall(text))


def merge_blocks(
    blocks: list[dict],
    gap_ms: int = 400,
    min_chars: int = 8,
    max_chars: int = 35,
) -> list[dict]:
    """
    將相鄰且過短的中文字幕合併為語意較完整的條目。
    """
    if not blocks:
        return []

    merged = []
    group_start = blocks[0].copy()
    group_texts = [blocks[0]["text"]]

    for curr in blocks[1:]:
        prev_end = group_start["end_ms"]  # 視窗最後 end
        # 取目前 group 最後一個 block 的 end
        if merged:
            # 重新計算 prev_end 為 group 中最後一條的 end
            pass
        # 實際上 group_start 的 end 在每次合併後都要更新
        gap = curr["start_ms"] - group_start["end_ms"]
        current_text = "".join(group_texts)
        current_char_count = zh_char_count(current_text)
        new_total_chars = zh_char_count(current_text + curr["text"])

        # 判斷是否繼續合併
        can_merge = (
            gap <= gap_ms                    # 間隔夠小
            and current_char_count < min_chars  # 目前太短
            and new_total_chars <= max_chars    # 合併後不超過上限
            and not SENTENCE_END.search(current_text)  # 上一段不是句尾
        )

        if can_merge:
            # 繼續堆疊，延長 end
            group_texts.append(curr["text"])
            group_start["end"] = curr["end"]
            group_start["end_ms"] = curr["end_ms"]
        else:
            # 輸出目前 group
            merged_text = "".join(group_texts)
            merged.append({
                **group_start,
                "text": merged_text,
            })
            # 以 curr 開新 group
            group_start = curr.copy()
            group_texts = [curr["text"]]

    # 最後一組
    merged.append({
        **group_start,
        "text": "".join(group_texts),
    })

    return merged


# ─── 主程式 ──────────────────────────────────────────────────────────────────

def merge_zh_srt(
    input_path: Path,
    output_path: Path | None = None,
    overwrite: bool = False,
    suffix: str = "_merged",
    gap_ms: int = 400,
    min_chars: int = 8,
    max_chars: int = 35,
) -> Path:
    """
    對外暴露的函式介面，供 main.py 直接 import 呼叫。
    回傳輸出檔路徑。
    """
    if output_path is None:
        if overwrite:
            output_path = input_path
        else:
            output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"

    if output_path.exists() and not overwrite:
        logger.info("⏭️  輸出已存在，跳過: %s", output_path)
        return output_path

    logger.info("── [中文短句合併] 讀取: %s", input_path)
    content = input_path.read_text(encoding="utf-8")
    blocks = parse_srt(content)
    if not blocks:
        logger.warning("  沒有解析到任何字幕，跳過。")
        return output_path

    orig_count = len(blocks)
    merged = merge_blocks(blocks, gap_ms=gap_ms, min_chars=min_chars, max_chars=max_chars)
    new_count = len(merged)

    logger.info(
        "── [中文短句合併] 完成: %d → %d 條（壓縮 %.1fx）",
        orig_count,
        new_count,
        orig_count / new_count if new_count else 1,
    )

    write_srt(merged, output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="翻譯前中文字幕短句合併工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", "-f", required=True, help="輸入的中文 SRT 路徑")
    parser.add_argument("--suffix", default="_merged", help="輸出後綴（預設 _merged）")
    parser.add_argument("--overwrite", action="store_true", help="覆蓋原始檔案")
    parser.add_argument("--gap", type=int, default=400, help="相鄰字幕容忍間隔 ms（預設 400）")
    parser.add_argument("--min-chars", type=int, default=8, help="合併目標最低字元數（預設 8）")
    parser.add_argument("--max-chars", type=int, default=35, help="合併後字元數上限（預設 35）")
    args = parser.parse_args()

    input_path = Path(args.file)
    if not input_path.exists():
        logger.error("找不到檔案: %s", input_path)
        sys.exit(1)

    merge_zh_srt(
        input_path=input_path,
        overwrite=args.overwrite,
        suffix=args.suffix,
        gap_ms=args.gap,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
    )


if __name__ == "__main__":
    main()
