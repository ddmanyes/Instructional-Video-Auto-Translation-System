"""
從影片中提取乾淨的參考音頻片段，用於聲音克隆
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

import argparse
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def extract_ref_audio(video_path: str, output_path: str = None,
                      start: float = 30.0, duration: float = 15.0):
    """
    從影片中提取乾淨的音頻片段作為聲音克隆的參考音頻。

    Args:
        video_path: 影片檔案路徑
        output_path: 輸出音頻路徑（預設：output/ref_audio/<檔名>.wav）
        start: 開始時間（秒），建議跳過片頭版權聲明
        duration: 擷取長度（秒），建議 10-30 秒
    """
    video_path = Path(video_path)
    if not video_path.exists():
        logger.error(f"❌ 找不到影片: {video_path}")
        return None

    if output_path is None:
        ref_dir = PROJECT_ROOT / "output" / "ref_audio"
        ref_dir.mkdir(parents=True, exist_ok=True)
        output_path = ref_dir / f"{video_path.stem}_ref.wav"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"🎙️  從影片提取參考音頻...")
    logger.info(f"   來源: {video_path.name}")
    logger.info(f"   時間: {start}s ~ {start + duration}s ({duration}s)")
    logger.info(f"   輸出: {output_path}")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-ss", str(start),
        "-t", str(duration),
        "-vn",                     # 不要影像
        "-acodec", "pcm_s16le",   # 標準 WAV 格式
        "-ar", "22050",            # Coqui XTTS 建議採樣率
        "-ac", "1",                # 單聲道
        "-af", "highpass=f=300,lowpass=f=5000,anlmdn",  # 降噪濾波
        str(output_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and output_path.exists():
            size_kb = output_path.stat().st_size // 1024
            logger.info(f"✅ 參考音頻提取成功！({size_kb} KB)")
            logger.info(f"   路徑: {output_path}")
            return str(output_path)
        else:
            logger.error(f"❌ FFmpeg 錯誤: {result.stderr[-500:]}")
            return None
    except FileNotFoundError:
        logger.error("❌ 找不到 ffmpeg，請確認 FFmpeg 已安裝並加入 PATH")
        return None


def main():
    parser = argparse.ArgumentParser(description="從影片提取參考音頻（用於聲音克隆）")
    parser.add_argument("--video", "-v", type=str, required=True, help="影片檔案路徑")
    parser.add_argument("--output", "-o", type=str, help="輸出音頻路徑")
    parser.add_argument("--start", "-s", type=float, default=30.0, help="開始時間（秒），預設 30")
    parser.add_argument("--duration", "-d", type=float, default=15.0, help="擷取長度（秒），預設 15")
    args = parser.parse_args()

    extract_ref_audio(args.video, args.output, args.start, args.duration)


if __name__ == "__main__":
    main()
