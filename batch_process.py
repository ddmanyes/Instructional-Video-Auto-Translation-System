#!/usr/bin/env python3
"""批量處理多個視頻"""

import os
import subprocess
import sys
from pathlib import Path

def get_video_files():
    """獲取所有視頻檔案（去重）"""
    video_dir = Path("video")
    videos = {}
    
    # 按大小和基礎名稱去重
    for mp4_file in sorted(video_dir.glob("*.mp4")):
        size = mp4_file.stat().st_size
        base_name = mp4_file.stem.split('-')[0] if '-' in mp4_file.stem else mp4_file.stem

        if base_name not in videos:
            videos[base_name] = mp4_file
        else:
            existing = videos[base_name]
            if size > existing.stat().st_size:
                videos[base_name] = mp4_file
    
    return sorted(videos.values(), key=lambda x: str(x))

def process_videos():
    """批量處理視頻"""
    videos = get_video_files()
    print(f"找到 {len(videos)} 個獨立視頻")
    
    for i, video in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] 處理: {video.name}")
        print("=" * 60)
        
        # 檢查是否已處理
        output_video = Path("output/final_videos") / f"{video.stem}_EN.mp4"
        if output_video.exists():
            print(f"⏭️  已完成: {output_video}")
            continue
        
        # 運行主程序
        try:
            result = subprocess.run(
                ["uv", "run", "python", "main.py", "--video", str(video)],
                timeout=3600  # 60分鐘超時
            )
            
            if result.returncode == 0:
                print(f"✅ 完成: {video.name}")
            else:
                print(f"⚠️  失敗: {video.name}")
        
        except subprocess.TimeoutExpired:
            print(f"❌ 超時: {video.name}")

if __name__ == "__main__":
    process_videos()
