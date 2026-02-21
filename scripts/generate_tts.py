"""
獨立 TTS 語音生成工具
用法：
  # Edge TTS（預設，免費固定音色）
  uv run python scripts/generate_tts.py --srt "output/subtitles/xxx_en.srt"

  # XTTS-v2 聲音克隆（使用說話者參考音頻）
  uv run python scripts/generate_tts.py --srt "..." --xtts --ref "output/ref_audio/xxx_ref.wav"
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

import argparse
import logging
import config
from modules.tts import TTSProcessor

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="TTS 語音生成工具")
    parser.add_argument("--srt", "-s", type=str, required=True,
                        help="英文 SRT 字幕檔案路徑")
    parser.add_argument("--output-dir", "-o", type=str,
                        help="音頻輸出目錄（預設：output/audio）")
    parser.add_argument("--xtts", action="store_true",
                        help="啟用 XTTS-v2 跨語言聲音克隆模式")
    parser.add_argument("--ref", "-r", type=str,
                        help="XTTS 參考音頻路徑（xtts 模式必填）")
    parser.add_argument("--voice", "-v", type=str,
                        default=config.TTS_CONFIG.get("voice", "en-US-GuyNeural"),
                        help="Edge TTS 音色（非 xtts 模式）")
    parser.add_argument("--speed", type=float,
                        default=config.TTS_CONFIG.get("speed", 1.3),
                        help="Edge TTS 語速（非 xtts 模式）")
    parser.add_argument("--no-skip", action="store_true",
                        help="強制重新生成（不跳過已存在的音頻）")
    args = parser.parse_args()

    srt_path = Path(args.srt)
    if not srt_path.exists():
        logger.error(f"❌ 找不到字幕檔案: {srt_path}")
        return

    # 決定輸出目錄
    output_dir = args.output_dir or str(config.AUDIO_DIR)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 決定參考音頻
    use_xtts = args.xtts or config.TTS_CONFIG.get("use_xtts", False)
    ref_audio = args.ref or config.TTS_CONFIG.get("ref_audio_path")

    if use_xtts:
        if not ref_audio:
            logger.error("❌ XTTS 模式需要提供 --ref 參考音頻路徑，或在 config.py 中設定 ref_audio_path")
            return
        if not Path(ref_audio).exists():
            logger.error(f"❌ 找不到參考音頻: {ref_audio}")
            return
        logger.info(f"🔊 模式：XTTS-v2 聲音克隆")
        logger.info(f"   參考音頻: {Path(ref_audio).name}")
    else:
        logger.info(f"🔊 模式：Edge TTS（{args.voice}, {args.speed}x）")

    logger.info(f"📄 字幕檔：{srt_path.name}")
    logger.info(f"📁 輸出目錄：{output_dir}")
    logger.info("─" * 50)

    # 初始化 TTS
    tts = TTSProcessor(
        voice=args.voice,
        speed=args.speed,
        use_xtts=use_xtts,
    )

    # 執行批次生成
    audio_segments = tts.generate_audio_from_srt(
        srt_path=str(srt_path),
        output_dir=output_dir,
        ref_audio=ref_audio if use_xtts else None,
        skip_existing=not args.no_skip,
    )

    logger.info("─" * 50)
    logger.info(f"✅ 完成！共生成 {len(audio_segments)} 個音頻片段")
    logger.info(f"   儲存於：{output_dir}")


if __name__ == "__main__":
    main()
