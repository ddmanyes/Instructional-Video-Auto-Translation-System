import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path

# 添加專案根目錄到 sys.path
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

def run_command(cmd, description):
    print(f"\n[{description}]")
    print(f"執行指令: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ {description} 失敗！(Exit code: {result.returncode})")
        sys.exit(result.returncode)
    print(f"✅ {description} 完成！")

def clean_directory(dir_path, video_name):
    """刪除資料夾中與指定影片相關的中間檔案"""
    if not os.path.exists(dir_path):
        return
    deleted_count = 0
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.startswith(video_name):
                filepath = os.path.join(root, file)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"⚠️ 無法刪除檔案 {filepath}: {e}")
    print(f"🧹 已清除 {dir_path} 中 {deleted_count} 個中間檔案 ({video_name})")

def main():
    parser = argparse.ArgumentParser(description="一鍵完成：XTTS 生成 -> 語音精準對齊 -> 影片合成 -> 清理中間檔")
    parser.add_argument("--video", "-v", type=str, required=True, help="原始影片路徑 (如 video/Neurophysiology-1.mp4)")
    parser.add_argument("--srt", "-s", type=str, required=True, help="翻譯好的英文字幕路徑 (如 output/subtitles/Neurophysiology-1_en.srt)")
    parser.add_argument("--ref", "-r", type=str, required=True, help="XTTS 參考音訊路徑 (如 output/ref_audio/Neurophysiology-1_ref.wav)")
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    srt_path = Path(args.srt)
    ref_path = Path(args.ref)
    
    if not video_path.exists():
        print(f"❌ 找不到影片檔案: {video_path}")
        sys.exit(1)
    if not srt_path.exists():
        print(f"❌ 找不到字幕檔案: {srt_path}")
        sys.exit(1)
    if not ref_path.exists():
        print(f"❌ 找不到參考音訊: {ref_path}")
        sys.exit(1)
        
    # 決定各種名稱與路徑
    video_name = video_path.stem
    audio_dir = str(PROJECT_ROOT / "output" / "audio")
    aligned_dir = str(PROJECT_ROOT / "output" / "audio_aligned")
    final_audio = os.path.join(aligned_dir, f"{video_name}_final_synced.wav")
    final_video_dir = PROJECT_ROOT / "output" / "final_videos"
    final_video_dir.mkdir(parents=True, exist_ok=True)
    final_video = str(final_video_dir / f"{video_name}_EN.mp4")
    
    python_exe = sys.executable

    # 1. 執行 TTS 語音生成 (XTTS 模式)
    cmd_tts = [
        python_exe, str(PROJECT_ROOT / "scripts" / "generate_tts.py"),
        "--srt", str(srt_path),
        "--xtts",
        "--ref", str(ref_path),
        "--output-dir", audio_dir
    ]
    run_command(cmd_tts, "步驟 1: 生成 XTTS 語音片段")

    # 2. 執行語音精準對齊 (呼叫剛剛改好的 align_audio.py)
    cmd_align = [
        python_exe, str(PROJECT_ROOT / "scripts" / "align_audio.py"),
        "--srt", str(srt_path),
        "--video-name", video_name,
        "--audio-dir", audio_dir,
        "--output-dir", aligned_dir,
        "--final-output", final_audio
    ]
    run_command(cmd_align, "步驟 2: 處理時長並對齊音軌")

    # 3. 執行 FFmpeg 將影片與新音軌合併
    # 使用 -map 0:v:0 代表只拿原影片的第一條影片軌道（去掉原本的聲音）
    # 使用 -map 1:a:0 代表拿 final_audio_path 的聲音
    cmd_merge = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", final_audio,
        "-c:v", "copy",     # 直接拷貝影像，不需浪費算力重新編碼
        "-c:a", "aac",      # 音軌重新壓縮為 aac (mp4 標準)
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        final_video
    ]
    run_command(cmd_merge, "步驟 3: 將同步好的音軌合成至影片")

    # 4. 清單掃描，刪除中間檔案
    print("\n[步驟 4: 清理中間檔案 (原音頻與對齊暫存檔)]")
    clean_directory(audio_dir, video_name)
    clean_directory(aligned_dir, video_name)
    
    # 也可以考慮把 final_audio 也刪掉，因為已經合成到 mp4 裡了
    if os.path.exists(final_audio):
        os.remove(final_audio)
        print(f"🧹 已刪除最終長音軌: {final_audio}")
        
    print("==============================================")
    print("🎉 自動化 Pipeline 執行完畢！")
    print(f"🎥 最終產出影片位於: {final_video}")
    print("==============================================")

if __name__ == "__main__":
    main()
