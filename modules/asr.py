"""
ASR (Automatic Speech Recognition) Module
使用 Faster-Whisper 進行語音轉文字，生成帶時間戳的 SRT 字幕
"""

import os
from faster_whisper import WhisperModel
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ASRProcessor:
    def __init__(self, model_size="large-v3", device="cuda", compute_type="float16"):
        """
        初始化 Whisper 模型
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large-v3)
            device: 運算裝置 (cuda, cpu)
            compute_type: 計算類型 (float16, int8)
        """
        logger.info(f"正在載入 Whisper 模型: {model_size}")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info("模型載入完成")
    
    def transcribe_video(self, video_path, language="zh", output_dir="output/subtitles"):
        """
        將影片轉錄為帶時間戳的 SRT 字幕
        
        Args:
            video_path: 影片路徑
            language: 語言代碼 (zh, en)
            output_dir: 輸出目錄
            
        Returns:
            srt_path: 生成的 SRT 檔案路徑
        """
        video_name = Path(video_path).stem
        os.makedirs(output_dir, exist_ok=True)
        srt_path = os.path.join(output_dir, f"{video_name}_zh.srt")
        
        logger.info(f"開始轉錄影片: {video_name}")
        
        # 使用 Whisper 進行轉錄
        segments, info = self.model.transcribe(
            video_path, 
            language=language,
            vad_filter=True,  # 啟用語音活動檢測
            word_timestamps=True
        )
        
        # 生成 SRT 格式
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self._format_timestamp(segment.start)
                end_time = self._format_timestamp(segment.end)
                text = segment.text.strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"轉錄完成，字幕已儲存至: {srt_path}")
        logger.info(f"偵測到的語言: {info.language}, 信心度: {info.language_probability:.2%}")
        
        return srt_path
    
    def _format_timestamp(self, seconds):
        """將秒數轉換為 SRT 時間格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


if __name__ == "__main__":
    # 測試用例
    asr = ASRProcessor(model_size="base", device="cpu")
    srt_file = asr.transcribe_video("video/test.mp4")
    print(f"生成的字幕檔案: {srt_file}")
