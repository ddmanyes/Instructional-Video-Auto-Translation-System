"""
merge_short_srt.py
==================
將過短的英文字幕合併成語意較完整的條目。

合併規則：
  1. 掃描相鄰字幕，若時間間隔 <= gap_ms (預設 300ms) 就視為連續語句。
  2. 持續向後合併，直到：
       - 合併後字數 >= min_words (預設 7)，或
       - 下一條間隔 > gap_ms，或
       - 合併後字數超過 max_words (預設 18)，或
       - 當前文字以句號 / 問號 / 驚嘆號結尾（句子自然終點）
  3. 合併的時間軸：取第一條的 start → 最後一條的 end。
  4. 合併文字：用空格連接（去除重複大寫首字母）。

用法：
  uv run python scripts/merge_short_srt.py \\
      --file "output/subtitles/xxx_polished_test.srt"

  # 調整間隔容忍度（毫秒）與目標字數
  uv run python scripts/merge_short_srt.py \\
      --file "output/subtitles/xxx.srt" --gap 500 --min-words 6 --max-words 20
"""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))


# ─── SRT 工具 ─────────────────────────────────────────────────────────────────

SRT_PAT = re.compile(
    r"(\d+)\r?\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\r?\n"
    r"(.*?)(?=\r?\n\r?\n|\Z)",
    re.DOTALL,
)

SENTENCE_END = re.compile(r"[.!?]\s*$")


def to_ms(ts: str) -> int:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3_600_000 + int(m) * 60_000 + int(s) * 1_000 + int(ms)


def from_ms(ms: int) -> str:
    h = ms // 3_600_000;  ms %= 3_600_000
    m = ms // 60_000;     ms %= 60_000
    s = ms // 1_000;      ms %= 1_000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(text: str) -> list[dict]:
    blocks = []
    for m in SRT_PAT.finditer(text):
        blocks.append({
            "start_ms": to_ms(m.group(2)),
            "end_ms":   to_ms(m.group(3)),
            "text":     m.group(4).strip(),
        })
    return blocks


def write_srt(blocks: list[dict], path: Path):
    with path.open("w", encoding="utf-8") as f:
        for i, b in enumerate(blocks, 1):
            f.write(
                f"{i}\n"
                f"{from_ms(b['start_ms'])} --> {from_ms(b['end_ms'])}\n"
                f"{b['text']}\n\n"
            )
    print(f"已寫入: {path}")


# ─── 合併邏輯 ─────────────────────────────────────────────────────────────────

def _join_texts(texts: list[str]) -> str:
    """將多段文字串接，處理大小寫與重複問題。"""
    if not texts:
        return ""
    result = texts[0]
    for t in texts[1:]:
        if not t:
            continue
        # 前一段若沒有以標點結尾，直接空格接續；否則首字母也大寫
        if result and result[-1] not in ".!?,;:":
            result = result.rstrip() + " " + t[0].lower() + t[1:]
        else:
            result = result.rstrip() + " " + t
    return result.strip()


def merge_blocks(
    blocks: list[dict],
    gap_ms: int = 300,
    min_words: int = 7,
    max_words: int = 18,
) -> list[dict]:
    """
    掃描並合併過短字幕。

    Returns:
        新的 blocks 列表（已合併）
    """
    if not blocks:
        return []

    merged = []
    i = 0

    while i < len(blocks):
        cur = blocks[i]
        group_texts  = [cur["text"]]
        group_start  = cur["start_ms"]
        group_end    = cur["end_ms"]

        while True:
            # 現有合併結果
            combined_text   = _join_texts(group_texts)
            combined_words  = len(combined_text.split())

            # 條件：已夠長 或 到句末 → 停止合併
            if combined_words >= min_words and SENTENCE_END.search(combined_text):
                break

            # 還不夠長，看下一條
            j = i + len(group_texts)
            if j >= len(blocks):
                break  # 沒有下一條了

            nxt = blocks[j]
            gap = nxt["start_ms"] - group_end

            # 間隔太大 → 停止合併
            if gap > gap_ms:
                break

            # 合併後會超過字數上限 → 停止（先輸出現有的）
            preview = _join_texts(group_texts + [nxt["text"]])
            if len(preview.split()) > max_words:
                break

            # 合併
            group_texts.append(nxt["text"])
            group_end = nxt["end_ms"]

        merged.append({
            "start_ms": group_start,
            "end_ms":   group_end,
            "text":     _join_texts(group_texts),
        })
        i += len(group_texts)

    return merged


# ─── 主程式 ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="合併過短的英文字幕條目",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", "-f", required=True, help="輸入 SRT 檔案")
    parser.add_argument(
        "--suffix", "-s", default="_merged",
        help="輸出檔案後綴（預設: _merged）",
    )
    parser.add_argument("--overwrite", action="store_true", help="覆蓋原始檔案")
    parser.add_argument(
        "--gap", type=int, default=300,
        help="相鄰字幕間隔容忍度（毫秒, 預設 300）",
    )
    parser.add_argument(
        "--min-words", type=int, default=7,
        help="合併目標最低字數（預設 7）",
    )
    parser.add_argument(
        "--max-words", type=int, default=18,
        help="合併後最高字數上限（預設 18）",
    )
    args = parser.parse_args()

    srt_path = Path(args.file)
    if not srt_path.exists():
        print(f"找不到檔案: {srt_path}")
        sys.exit(1)

    output_path = (
        srt_path if args.overwrite
        else srt_path.parent / f"{srt_path.stem}{args.suffix}{srt_path.suffix}"
    )

    if output_path.exists() and not args.overwrite:
        print(f"⏭️  輸出已存在，跳過: {output_path}")
        print("    如需重新生成，請加上 --overwrite 或刪除現有檔案。")
        sys.exit(0)

    print(f"讀取: {srt_path}")
    content = srt_path.read_text(encoding="utf-8")
    blocks = parse_srt(content)
    print(f"原始字幕數: {len(blocks)}")

    merged = merge_blocks(
        blocks,
        gap_ms=args.gap,
        min_words=args.min_words,
        max_words=args.max_words,
    )
    print(f"合併後字幕數: {len(merged)}")
    print(f"壓縮比: {len(blocks)/len(merged):.2f}x（減少 {len(blocks)-len(merged)} 條）")

    write_srt(merged, output_path)
    print(f"✅ 完成！輸出: {output_path}")


if __name__ == "__main__":
    main()
