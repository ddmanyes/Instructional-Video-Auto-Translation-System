"""
Video Assembly Module
使用 MoviePy 或 FFmpeg 進行影音合成
"""

import os
from pathlib import Path
import logging
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
except ImportError:
    # MoviePy 2.x 的新導入方式
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips

try:
    from moviepy.audio.fx.all import speedx as audio_speedx
except Exception:
    try:
        from moviepy.audio.fx import all as afx
        audio_speedx = afx.speedx
    except Exception:
        audio_speedx = None
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAssembler:
    def __init__(self, method="moviepy"):
        """
        初始化影音合成器
        
        Args:
            method: 合成方法 ("moviepy" 或 "ffmpeg")
        """
        self.method = method
        logger.info(f"已初始化影音合成器: {method}")
    
    def assemble_video(self, video_path, audio_segments, srt_path=None, output_dir="output/final_videos"):
        """
        組合影片與音頻
        
        Args:
            video_path: 原始影片路徑
            audio_segments: 音頻片段列表（包含時間戳和檔案路徑）
            srt_path: 英文字幕路徑（可選）
            output_dir: 輸出目錄
            
        Returns:
            output_path: 輸出影片路徑
        """
        video_name = Path(video_path).stem
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video_name}_EN.mp4")
        
        logger.info(f"開始合成影片: {video_name}")
        
        # Debug: 輸出音頻段信息
        if audio_segments:
            first_seg = audio_segments[0]
            last_seg = audio_segments[-1]
            logger.debug(f"音頻段總數: {len(audio_segments)}")
            logger.debug(f"第1段: start={first_seg.get('start', 0):.2f}s, end={first_seg.get('end', 0):.2f}s")
            logger.debug(f"最後1段: start={last_seg.get('start', 0):.2f}s, end={last_seg.get('end', 0):.2f}s")
        
        if self.method == "moviepy":
            self._assemble_with_moviepy(video_path, audio_segments, output_path, srt_path)
        else:
            self._assemble_with_ffmpeg(video_path, audio_segments, output_path, srt_path)
        
        logger.info(f"影片合成完成: {output_path}")
        return output_path
    
    def _assemble_with_moviepy(self, video_path, audio_segments, output_path, srt_path=None):
        """使用 MoviePy 進行合成"""
        try:
            # 載入原始影片並移除原始音頻
            video = VideoFileClip(video_path)
            video_duration = video.duration
            
            # 重要：移除原始音頻軌道，只保留視頻
            video = video.without_audio()
            
            # 計算音頻總時長（基於actual_duration）
            total_audio_duration = sum(seg['actual_duration'] for seg in audio_segments)
            
            # 如果需要縮放，先調整音頻時間戳
            scale_factor = 1.0
            if total_audio_duration > video_duration:
                scale_factor = video_duration / total_audio_duration
                logger.info(f"音頻總時長 {total_audio_duration:.2f}s 超過影片時長 {video_duration:.2f}s")
                logger.info(f"應用縮放因子: {scale_factor:.4f}")
                audio_segments = self._scale_segments(audio_segments, scale_factor)
                if audio_speedx is None:
                    logger.warning("MoviePy 未提供 speedx，將改用裁切以避免重疊")
            
            # 如果有字幕，根據音頻時間戳更新字幕
            if srt_path:
                self._update_srt_from_segments(srt_path, audio_segments, scale_factor=scale_factor)
            
            # 創建空白音頻軌道
            audio_clips = []
            
            for segment in audio_segments:
                # 載入音頻片段
                audio_clip = AudioFileClip(segment['audio_path'])

                if scale_factor < 1.0:
                    if audio_speedx is not None:
                        audio_clip = audio_speedx(audio_clip, factor=1.0 / scale_factor)
                    else:
                        target_duration = segment.get('actual_duration', audio_clip.duration) * scale_factor
                        audio_clip = audio_clip.subclip(0, min(target_duration, audio_clip.duration))
                
                # 設置音頻開始時間（MoviePy 2.x 使用 with_start）
                audio_clip = audio_clip.with_start(segment['start'])
                audio_clips.append(audio_clip)
            
            # 合併所有音頻片段
            if audio_clips:
                final_audio = CompositeAudioClip(audio_clips)
                # MoviePy 2.x 使用 with_audio 替代 set_audio
                video = video.with_audio(final_audio)
            
            # 寫入輸出檔案
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=video.fps
            )
            
            # 如果有字幕，嵌入字幕
            if srt_path:
                self._embed_subtitles(output_path, srt_path)
            
            # 清理
            video.close()
            for clip in audio_clips:
                clip.close()
        
        except Exception as e:
            logger.error(f"MoviePy 合成失敗: {e}")
            raise
    
    def _scale_segments(self, audio_segments, scale_factor):
        """
        按比例縮放音頻段的時間戳
        
        Args:
            audio_segments: 音頻段列表
            scale_factor: 縮放因子
            
        Returns:
            縮放後的音頻段列表
        """
        scaled_segments = []
        for segment in audio_segments:
            scaled = dict(segment)
            scaled['start'] = segment['start'] * scale_factor
            scaled['end'] = segment['end'] * scale_factor
            scaled_segments.append(scaled)
        
        return scaled_segments
    
    def _update_srt_from_segments(self, srt_path, audio_segments, scale_factor=None):
        """
        根據縮放因子更新字幕檔案時間戳
        
        Args:
            srt_path: SRT 檔案路徑
            audio_segments: 包含start/end時間戳的音頻段列表（已縮放）
        """
        try:
            # 計算原始音頻總時長和縮放後的時長
            if not audio_segments:
                return
                
            with open(srt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if scale_factor is None:
                # 改用直接讀取音頻檔案並計算的方法
                from moviepy.audio.io.AudioFileClip import AudioFileClip

                total_actual_duration = 0.0
                for seg in audio_segments:
                    clip = AudioFileClip(seg['audio_path'])
                    try:
                        total_actual_duration += clip.duration
                    finally:
                        clip.close()

                # 從字幕提取最後的時間戳以估算原始時長
                last_subtitle_end = 0
                for line in lines:
                    if '-->' in line:
                        parts = line.split('-->')
                        if len(parts) == 2:
                            end_time_str = parts[1].strip()
                            last_subtitle_end = self._srt_time_to_seconds(end_time_str)

                if last_subtitle_end <= 0 or total_actual_duration <= 0:
                    return

                scale_factor = total_actual_duration / last_subtitle_end
            
            if abs(scale_factor - 1.0) < 0.001:  # 如果接近1，不需要縮放
                return
            
            logger.info(f"字幕縮放因子: {scale_factor:.4f} (字幕:{last_subtitle_end:.2f}s → 音頻:{total_actual_duration:.2f}s)")
            
            # 縮放所有時間戳
            updated_lines = []
            for line in lines:
                if '-->' in line:
                    parts = line.split('-->')
                    if len(parts) == 2:
                        start_str = parts[0].strip()
                        end_str = parts[1].strip()
                        
                        start_seconds = self._srt_time_to_seconds(start_str)
                        end_seconds = self._srt_time_to_seconds(end_str)
                        
                        new_start = start_seconds * scale_factor
                        new_end = end_seconds * scale_factor
                        
                        new_line = f"{self._seconds_to_srt_time(new_start)} --> {self._seconds_to_srt_time(new_end)}\n"
                        updated_lines.append(new_line)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # 寫回檔案
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            
            logger.info(f"✓ 字幕時間戳已更新 (縮放: {scale_factor:.4f})")
                
        except Exception as e:
            logger.error(f"更新字幕時間戳失敗: {e}", exc_info=True)
    
    @staticmethod
    def _srt_time_to_seconds(time_str):
        """將 SRT 時間格式轉換為秒"""
        # 格式: HH:MM:SS,mmm
        time_str = time_str.strip()
        parts = time_str.replace(',', '.').split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        return 0
    
    @staticmethod
    def _seconds_to_srt_time(seconds):
        """將秒轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        milliseconds = int((secs % 1) * 1000)
        secs = int(secs)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    
    def _assemble_with_ffmpeg(self, video_path, audio_segments, output_path, srt_path=None):
        """使用 FFmpeg 進行合成（更快，適合大型影片）"""
        try:
            # 步驟 1: 創建音頻時間軸檔案
            audio_timeline = "temp_audio_timeline.txt"
            with open(audio_timeline, 'w', encoding='utf-8') as f:
                for segment in audio_segments:
                    f.write(f"file '{segment['audio_path']}'\n")
            
            # 步驟 2: 合併音頻
            temp_audio = "temp_combined_audio.aac"
            cmd_audio = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", audio_timeline,
                "-c:a", "aac",
                "-b:a", "192k",
                temp_audio
            ]
            subprocess.run(cmd_audio, check=True, capture_output=True)
            
            # 步驟 3: 移除原始影片音軌
            temp_video = "temp_video_no_audio.mp4"
            cmd_remove_audio = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-an",  # 移除音頻
                "-c:v", "copy",
                temp_video
            ]
            subprocess.run(cmd_remove_audio, check=True, capture_output=True)
            
            # 步驟 4: 合併影片與新音軌
            cmd_merge = [
                "ffmpeg", "-y",
                "-i", temp_video,
                "-i", temp_audio,
                "-c:v", "copy",
                "-c:a", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0"
            ]
            
            cmd_merge.append(output_path)
            subprocess.run(cmd_merge, check=True, capture_output=True)

            # 僅複製字幕檔案供播放器載入
            if srt_path:
                self._embed_subtitles(output_path, srt_path)
            
            # 清理臨時檔案
            for temp_file in [audio_timeline, temp_audio, temp_video]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        except Exception as e:
            logger.error(f"FFmpeg 合成失敗: {e}")
            raise
    
    def _embed_subtitles(self, video_path, srt_path):
        """將字幕嵌入影片（硬字幕）"""
        try:
            # FFmpeg 在 Windows 上處理中文路徑時有問題
            # 改為使用替代方案：copy 字幕檔案到輸出目錄，供使用者透過播放器加載
            import shutil
            output_srt = video_path.replace('.mp4', '.srt')
            shutil.copy(str(srt_path), output_srt)
            logger.info(f"字幕已複製到 {output_srt}（可在播放器中加載）")
            
        except Exception as e:
            logger.warning(f"字幕處理失敗: {e}")


if __name__ == "__main__":
    # 測試用例
    assembler = VideoAssembler(method="moviepy")
    
    # 示例音頻片段
    segments = [
        {'start': 0, 'end': 5, 'audio_path': 'output/audio/seg_0001.wav'},
        {'start': 5, 'end': 10, 'audio_path': 'output/audio/seg_0002.wav'},
    ]
    
    assembler.assemble_video("video/test.mp4", segments)
