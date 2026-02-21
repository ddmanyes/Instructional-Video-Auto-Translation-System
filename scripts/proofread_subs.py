import argparse
import sys
from pathlib import Path

# 將專案根目錄加入系統路徑
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

import config
import logging
from modules.subtitle_cleaner import SubtitleCleaner

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="英文字幕專用校稿工具")
    parser.add_argument("--file", "-f", type=str, help="指定要校稿的英文 SRT 檔案路徑")
    parser.add_argument("--model", "-m", type=str, help="指定使用的 Gemini 模型")
    args = parser.parse_args()

    cleaner = SubtitleCleaner()
    subtitle_dir = config.SUBTITLE_DIR

    # 取得提示詞
    en_prompt = getattr(config, "EN_PROOFREAD_PROMPT", (
        "You are a professional medical physiology editor.\n"
        "Refine the following English subtitles for academic accuracy and readability.\n"
        "Maintain a professional tone suitable for medical students.\n"
        "Requirements: JSON array output, preserve \\n, same line count as input."
    ))

    if args.file:
        srt_bits = [Path(args.file)]
    else:
        # 預設尋找資料夾中所有的英文檔
        srt_bits = list(subtitle_dir.glob("*_en.srt"))
        logger.info(f"找到 {len(srt_bits)} 個英文字幕檔待校稿")

    for srt_path in srt_bits:
        if not srt_path.exists():
            logger.error(f"❌ 找不到檔案: {srt_path}")
            continue
        
        logger.info(f"🔍 正在校稿: {srt_path.name}")
        
        # 呼叫校稿功能
        proofread_path = cleaner.proofread_srt_with_prompt(
            srt_path=srt_path,
            output_dir=str(subtitle_dir),
            suffix="_refined",
            overwrite=False,
            prompt=en_prompt,
            model=args.model or config.EN_PROOFREAD_CONFIG.get("model"),
            batch_size=config.EN_PROOFREAD_CONFIG.get("batch_size", 10),
            timeout=config.EN_PROOFREAD_CONFIG.get("timeout", 180),
            command=config.EN_PROOFREAD_CONFIG.get("command"),
            command_args=config.EN_PROOFREAD_CONFIG.get("command_args")
        )
        logger.info(f"✅ 校稿完成: {Path(proofread_path).name}\n")

if __name__ == "__main__":
    main()
