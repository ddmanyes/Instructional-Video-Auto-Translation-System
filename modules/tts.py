"""
TTS (Text-to-Speech) Module
支援兩種模式：
  1. Edge TTS (僅限 edge，免費，固定音色)
  2. Coqui XTTS-v2 (聲音克隆，支援跨語言：從中文說話者提取聲線生成英文語音)
"""

import os
import re
from pathlib import Path
import logging
import asyncio
import numpy as np
import librosa
import soundfile as sf
import edge_tts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSProcessor:
    def __init__(self, voice="en-US-JennyNeural", speed=1.0, use_xtts=False):
        """
        初始化 TTS 處理器

        Args:
            voice: Edge TTS 音色（use_xtts=False 時使用）
            speed: 語速調整倍率 (0.5-2.0)，Edge TTS 模式有效
            use_xtts: 是否使用 Coqui XTTS-v2 跨語言聲音克隆
        """
        self.voice = voice
        self.speed = speed
        self.use_xtts = use_xtts
        self._xtts_model = None  # 延遲載入

        # Edge TTS 速率計算
        rate_percent = int((speed - 1) * 100)
        self.rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"

        if use_xtts:
            logger.info("TTS 模式：Coqui XTTS-v2（跨語言聲音克隆）")
        else:
            logger.info(f"TTS 模式：Edge TTS，音色: {voice}, 語速: {speed}x")

    # ─── XTTS 相關 ────────────────────────────────────────────────────────────

    def _load_xtts(self):
        """延遲載入 XTTS-v2 模型（首次呼叫時才下載/載入），自動偵測 GPU"""
        if self._xtts_model is not None:
            return self._xtts_model

        try:
            from TTS.api import TTS as CoquiTTS
        except ImportError:
            raise RuntimeError(
                "Coqui TTS 未安裝。請執行：uv pip install 'TTS>=0.22.0'"
            )

        try:
            import torch
            torch.backends.cudnn.enabled = False
            use_gpu = torch.cuda.is_available()
        except ImportError:
            use_gpu = False

        device_name = f"GPU ({torch.cuda.get_device_name(0)})" if use_gpu else "CPU"
        logger.info(f"🔄 正在載入 XTTS-v2 模型（運算裝置：{device_name}）...")
        logger.info("   首次使用需下載約 1.8GB 模型，請稍候...")

        self._xtts_model = CoquiTTS(
            "tts_models/multilingual/multi-dataset/xtts_v2",
            gpu=use_gpu
        )
        logger.info(f"✅ XTTS-v2 模型載入完成（{device_name}）")
        return self._xtts_model

    def _generate_xtts_audio(self, text: str, output_path: str, ref_audio: str) -> bool:
        """
        使用 XTTS-v2 克隆聲音生成英文語音

        Args:
            text: 英文字幕文字
            output_path: 輸出音頻路徑
            ref_audio: 中文參考音頻路徑（提取說話者聲線）

        Returns:
            bool: 是否成功
        """
        if not ref_audio or not Path(ref_audio).exists():
            logger.error(f"❌ 找不到參考音頻: {ref_audio}")
            return False

        try:
            model = self._load_xtts()
            model.tts_to_file(
                text=text,
                speaker_wav=ref_audio,
                language="en",   # 目標語言：英文
                file_path=output_path,
            )
            return Path(output_path).exists()

        except Exception as e:
            logger.error(f"❌ XTTS 生成失敗: {e}")
            return False

    # ─── Edge TTS 相關 ────────────────────────────────────────────────────────

    async def _async_generate_audio(self, text: str, output_path: str):
        """異步生成 Edge TTS 音頻"""
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
        await communicate.save(output_path)

    # ─── 統一入口 ──────────────────────────────────────────────────────────────

    def _generate_single_audio(self, text: str, output_path: str,
                                target_duration: float = None, ref_audio: str = None) -> bool:
        """
        生成單個音頻片段

        Args:
            text: 英文字幕文字
            output_path: 輸出音頻路徑
            target_duration: 目標時長（用於時間軸對齊，可選）
            ref_audio: 參考音頻（XTTS 模式必須提供）

        Returns:
            bool: 是否成功
        """
        try:
            if self.use_xtts:
                # XTTS-v2 跨語言聲音克隆
                if not ref_audio:
                    logger.warning("⚠️  XTTS 模式未提供參考音頻，改用 Edge TTS 備援")
                    asyncio.run(self._async_generate_audio(text, output_path))
                else:
                    if not self._generate_xtts_audio(text, output_path, ref_audio):
                        return False
            else:
                # Edge TTS（預設）
                asyncio.run(self._async_generate_audio(text, output_path))

            return os.path.exists(output_path)

        except Exception as e:
            logger.error(f"TTS 生成失敗: {e}")
            return False

    # ─── SRT 批次處理 ──────────────────────────────────────────────────────────

    def parse_srt(self, srt_path: str):
        """解析 SRT 字幕檔案"""
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = re.compile(
            r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)',
            re.DOTALL
        )

        subtitles = []
        for match in pattern.finditer(content):
            start = self._timestamp_to_seconds(match.group(2))
            end = self._timestamp_to_seconds(match.group(3))
            subtitles.append({
                'index': int(match.group(1)),
                'start': start,
                'end': end,
                'duration': end - start,
                'text': match.group(4).strip()
            })
        return subtitles

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """將 SRT 時間戳轉換為秒數"""
        h, m, s = timestamp.replace(',', '.').split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)

    def _recalculate_timestamps(self, audio_segments):
        """根據實際音頻長度重新計算時間戳"""
        if not audio_segments:
            return audio_segments
        recalculated = []
        current_time = 0.0
        for seg in audio_segments:
            new_seg = dict(seg)
            new_seg['start'] = current_time
            new_seg['end'] = current_time + seg['actual_duration']
            current_time = new_seg['end']
            recalculated.append(new_seg)
        logger.info(f"重新計算時間戳：總音頻長度 = {current_time:.2f}秒")
        return recalculated

    def generate_audio_from_srt(self, srt_path: str, output_dir: str = "output/audio",
                                 ref_audio: str = None, skip_existing: bool = True):
        """
        根據 SRT 字幕批次生成對應音頻

        Args:
            srt_path: 英文 SRT 路徑
            output_dir: 音頻輸出目錄
            ref_audio: 參考音頻（XTTS 模式下為說話者音頻）
            skip_existing: 跳過已存在的音頻

        Returns:
            audio_segments: 包含音頻路徑和時間資訊的列表
        """
        video_name = Path(srt_path).stem.replace('_en', '').replace('_corrected', '')
        os.makedirs(output_dir, exist_ok=True)

        mode = "XTTS-v2 (聲音克隆)" if self.use_xtts else "Edge TTS"
        logger.info(f"開始生成音頻 [{mode}]: {video_name}")

        subtitles = self.parse_srt(srt_path)
        audio_segments = []
        skipped_count = 0

        for i, sub in enumerate(subtitles):
            audio_file = os.path.join(output_dir, f"{video_name}_seg_{sub['index']:04d}.wav")

            # 檢查檔案是否存在且大小不為 0（防止斷電或中斷產生的損毀檔）
            if skip_existing and os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                skipped_count += 1
                actual_duration = librosa.get_duration(path=audio_file)
                audio_segments.append({
                    'index': sub['index'], 'start': sub['start'], 'end': sub['end'],
                    'target_duration': sub['duration'], 'actual_duration': actual_duration,
                    'audio_path': audio_file, 'text': sub['text']
                })
                continue

            import time
            import random
            max_retries = 5
            success = False
            for attempt in range(max_retries):
                success = self._generate_single_audio(
                    text=sub['text'],
                    output_path=audio_file,
                    target_duration=sub['duration'],
                    ref_audio=ref_audio
                )
                if success:
                    break
                wait_time = (2 ** attempt) + random.uniform(0.5, 2.0)
                logger.warning(f"⚠️ 生成失敗，等待 {wait_time:.1f} 秒後重試... ({attempt+1}/{max_retries})")
                time.sleep(wait_time)

            if success:
                actual_duration = librosa.get_duration(path=audio_file)
                audio_segments.append({
                    'index': sub['index'], 'start': sub['start'], 'end': sub['end'],
                    'target_duration': sub['duration'], 'actual_duration': actual_duration,
                    'audio_path': audio_file, 'text': sub['text']
                })
                logger.info(
                    f"[{i+1-skipped_count}/{len(subtitles)-skipped_count}] "
                    f"目標: {sub['duration']:.2f}s | 實際: {actual_duration:.2f}s"
                )
            else:
                logger.error(f"❌ 嚴重錯誤：連續 {max_retries} 次生成失敗，為避免無聲影片已中止: {sub['text'][:30]}...")
                raise RuntimeError("語音生成持續失敗（API 限制或網路錯誤），請切換 IP 或稍後再試！")
            
            # 加入較保守的隨機延遲避免 API 被限流 (2000+ 句需要更穩健)
            time.sleep(random.uniform(0.3, 0.8))

        if skipped_count > 0:
            logger.info(f"⏭️  跳過已存在: {skipped_count} 個片段")

        audio_segments = self._recalculate_timestamps(audio_segments)
        return audio_segments

    def _adjust_audio_speed(self, audio_path: str, target_duration: float):
        """調整音頻速度以符合目標時長"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            current_duration = len(y) / sr
            speed_ratio = current_duration / target_duration
            max_speed = 3.0
            if speed_ratio > max_speed:
                logger.warning(f"速度比 {speed_ratio:.2f}x 過高，限制為 {max_speed}x")
                speed_ratio = max_speed
                y_stretched = librosa.effects.time_stretch(y, rate=speed_ratio)
                silence_duration = target_duration - len(y_stretched) / sr
                if silence_duration > 0:
                    y_stretched = np.concatenate([y_stretched, np.zeros(int(silence_duration * sr))])
            else:
                y_stretched = librosa.effects.time_stretch(y, rate=speed_ratio)
            sf.write(audio_path, y_stretched, sr)
        except Exception as e:
            logger.error(f"音頻速度調整失敗: {e}")


if __name__ == "__main__":
    # 測試用例
    tts = TTSProcessor()
    segments = tts.generate_audio_from_srt("output/subtitles/test_en.srt")
    print(f"生成了 {len(segments)} 個音頻片段")
