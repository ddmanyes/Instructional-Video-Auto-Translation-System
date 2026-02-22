"""
主程式 - 影片翻譯自動化處理
"""

import os
import sys
import shutil
import subprocess
import argparse
import logging
from pathlib import Path

# 確保能跨模組導入 scripts 底下的腳本
sys.path.append(str(Path(__file__).parent))
from scripts.align_audio import align_audio
from scripts.refine_en_srt import refine_srt

# 導入模組
from modules.asr import ASRProcessor
from modules.subtitle_cleaner import SubtitleCleaner
from modules.translator import SubtitleTranslator
from modules.tts import TTSProcessor
from modules.video_assembler import VideoAssembler
import config

# 設定日誌
logging.basicConfig(
    level=config.LOGGING_CONFIG["level"],
    format=config.LOGGING_CONFIG["format"],
    datefmt=config.LOGGING_CONFIG["datefmt"]
)
logger = logging.getLogger(__name__)


class VideoTranslationPipeline:
    """影片翻譯處理流程"""
    
    def __init__(self):
        """初始化所有處理器"""
        logger.info("="*60)
        logger.info("正在初始化影片翻譯流程...")
        logger.info("="*60)
        
        # 初始化各個模組
        self.asr = ASRProcessor(
            model_size=config.ASR_CONFIG["model_size"],
            device=config.ASR_CONFIG["device"],
            compute_type=config.ASR_CONFIG["compute_type"]
        )

        self.cleaner = None
        if config.CLEANER_CONFIG.get("enabled", False) or config.EN_PROOFREAD_CONFIG.get("enabled", False):
            self.cleaner = SubtitleCleaner(
                filler_words=config.CLEANER_CONFIG.get("filler_words"),
                repeat_phrases=config.CLEANER_CONFIG.get("repeat_phrases"),
                typo_map=config.CLEANER_CONFIG.get("typo_map"),
            )
        
        self.translator = SubtitleTranslator(
            api_provider=config.TRANSLATION_CONFIG["api_provider"],
            api_key=config.OPENAI_API_KEY if config.TRANSLATION_CONFIG["api_provider"] == "openai" 
                    else config.ANTHROPIC_API_KEY
        )
        
        self.tts = TTSProcessor(
            voice=config.TTS_CONFIG["voice"],
            speed=config.TTS_CONFIG["speed"],
            use_xtts=config.TTS_CONFIG.get("use_xtts", False)
        )
        
        self.assembler = VideoAssembler(
            method=config.VIDEO_ASSEMBLY_CONFIG["method"]
        )
        
        logger.info("所有模組初始化完成！\n")
    
    def process_single_video(self, video_path, ref_audio=None, subtitle_only=False):
        """
        處理單個影片
        
        Args:
            video_path: 影片路徑
            ref_audio: 參考音頻路徑（用於聲音克隆，可選）
            subtitle_only: 只生成字幕（跳過TTS和視頻合成）
        
        Returns:
            output_path: 中文字幕路徑（subtitle_only=True）或處理後的影片路徑
        """
        video_name = Path(video_path).stem
        logger.info(f"\n{'='*60}")
        logger.info(f"開始處理影片: {video_name}")
        if subtitle_only:
            logger.info("模式: 只輸出中文字幕")
        logger.info(f"{'='*60}\n")
        
        try:
            # 檢查輸出文件路徑
            zh_srt_path = config.SUBTITLE_DIR / f"{video_name}_zh.srt"
            en_srt_path = config.SUBTITLE_DIR / f"{video_name}_en.srt"
            zh_corrected_srt_path = config.SUBTITLE_DIR / f"{video_name}_zh_corrected.srt"
            
            # 優先檢查是否有人工手動校正的字幕檔
            source_srt_path = None
            if zh_corrected_srt_path.exists():
                logger.info("【步驟 1/1】偵測到手動校正字幕...")
                logger.info(f"✨ 找到手動校正檔: {zh_corrected_srt_path.name}，將跳過 ASR 語音辨識直接以此為基礎進行後續翻譯！\n")
                source_srt_path = str(zh_corrected_srt_path)
            else:
                # 步驟 1: 原本的 ASR - 語音轉文字 (斷點續傳)
                if zh_srt_path.exists():
                    logger.info("【步驟 1/1】語音轉文字 (ASR)...")
                    logger.info(f"⏭️  跳過：中文字幕已存在 {zh_srt_path}\n")
                    zh_srt_path = str(zh_srt_path)
                else:
                    logger.info("【步驟 1/1】語音轉文字 (ASR)...")
                    zh_srt_path = self.asr.transcribe_video(
                        video_path=video_path,
                        language=config.ASR_CONFIG["language"],
                        output_dir=str(config.SUBTITLE_DIR)
                    )
                    logger.info(f"✓ 中文字幕已生成: {zh_srt_path}\n")
                
                cleaned_srt_path = None
                proofread_srt_path = None
                if self.cleaner:
                    cleaned_srt_path = self.cleaner.clean_srt(
                        srt_path=zh_srt_path,
                        output_dir=str(config.SUBTITLE_DIR),
                        suffix=config.CLEANER_CONFIG.get("suffix", "_zh_clean"),
                        overwrite=config.CLEANER_CONFIG.get("overwrite_original", False),
                    )

                    if config.GEMINI_CONFIG.get("enabled", False):
                        proofread_srt_path = self.cleaner.proofread_srt(
                            srt_path=cleaned_srt_path,
                            output_dir=str(config.SUBTITLE_DIR),
                            suffix=config.GEMINI_CONFIG.get("suffix", "_zh_gemini"),
                            overwrite=config.GEMINI_CONFIG.get("overwrite_original", False),
                            model=config.GEMINI_CONFIG.get("model") or None,
                            batch_size=config.GEMINI_CONFIG.get("batch_size", 20),
                            timeout=config.GEMINI_CONFIG.get("timeout", 120),
                            command=config.GEMINI_CONFIG.get("command") or None,
                            command_args=config.GEMINI_CONFIG.get("command_args"),
                            max_length_ratio=config.GEMINI_CONFIG.get("max_length_ratio", 1.0),
                        )

                source_srt_path = proofread_srt_path or cleaned_srt_path or zh_srt_path

            # 如果只需要中文字幕，直接返回
            if subtitle_only:
                logger.info(f"{'='*60}")
                logger.info(f"✅ {video_name} 字幕生成完成！")
                logger.info(f"地點: {proofread_srt_path or cleaned_srt_path or zh_srt_path}")
                logger.info(f"{'='*60}\n")
                return str(proofread_srt_path or cleaned_srt_path or zh_srt_path)
            
            # 步驟 2: 翻譯 (斷點續傳)
            # 檢查是否已存在各種可能的英文字幕檔名 (標準、手動校正後產生的)
            potential_en_paths = [
                en_srt_path,
                config.SUBTITLE_DIR / f"{video_name}_corrected_en.srt",
                config.SUBTITLE_DIR / f"{video_name}_zh_corrected_en.srt"
            ]
            existing_en = next((p for p in potential_en_paths if p.exists()), None)

            if existing_en:
                logger.info("【步驟 2/4】翻譯字幕...")
                logger.info(f"⏭️  跳過：英文字幕已存在 {existing_en.name}\n")
                en_srt_path = str(existing_en)
            else:
                logger.info("【步驟 2/4】翻譯字幕...")
                en_srt_path = self.translator.translate_subtitles(
                    srt_path=source_srt_path,
                    target_lang=config.TRANSLATION_CONFIG["target_language"],
                    output_dir=str(config.SUBTITLE_DIR)
                )
                logger.info(f"✓ 英文字幕已生成: {en_srt_path}\n")

            if config.EN_PROOFREAD_CONFIG.get("enabled", False) and self.cleaner:
                en_prompt = (
                    "You are a professional subtitle proofreader specialized in physiology and anatomy.\n"
                    "Fix grammar and terminology without changing meaning.\n"
                    "Requirements:\n"
                    "1. One input line -> one output line\n"
                    "2. Output plain text only, no extra commentary\n"
                    "3. Do not merge or split lines\n"
                    "4. Keep length close to original; shorten if too long\n"
                    "5. Preserve \\n tokens (line breaks)\n"
                    "6. Output must be a JSON array of strings with the same length as input\n"
                )

                en_srt_path = self.cleaner.proofread_srt_with_prompt(
                    srt_path=en_srt_path,
                    output_dir=str(config.SUBTITLE_DIR),
                    suffix=config.EN_PROOFREAD_CONFIG.get("suffix", "_en_proofread"),
                    overwrite=config.EN_PROOFREAD_CONFIG.get("overwrite_original", False),
                    prompt=en_prompt,
                    model=config.EN_PROOFREAD_CONFIG.get("model") or None,
                    batch_size=config.EN_PROOFREAD_CONFIG.get("batch_size", 8),
                    timeout=config.EN_PROOFREAD_CONFIG.get("timeout", 180),
                    command=config.EN_PROOFREAD_CONFIG.get("command") or None,
                    command_args=config.EN_PROOFREAD_CONFIG.get("command_args"),
                    max_length_ratio=config.EN_PROOFREAD_CONFIG.get("max_length_ratio", 1.0),
                    only_flagged=config.EN_PROOFREAD_CONFIG.get("only_flagged", False),
                )
            
            # 步驟 2.5: 英文字幕三段式精修（規則清理 → AI 潤色 → 短句合併）
            if config.EN_REFINE_CONFIG.get("enabled", False):
                logger.info("【步驟 2.5/4】英文字幕精修（去贅詞 + AI 潤色 + 短句合併）...")
                cfg = config.EN_REFINE_CONFIG
                en_srt_path = refine_srt(
                    srt_path=en_srt_path,
                    suffix=cfg.get("suffix", "_refined"),
                    overwrite=cfg.get("overwrite_original", False),
                    no_ai=not cfg.get("ai_enabled", True),
                    ai_all=cfg.get("ai_all", False),
                    batch_size=cfg.get("batch_size", 8),
                    timeout=cfg.get("timeout", 180),
                    model=cfg.get("model") or None,
                    command=cfg.get("command") or None,
                    command_args=cfg.get("command_args"),
                    gap_ms=cfg.get("merge_gap_ms", 300),
                    min_words=cfg.get("merge_min_words", 7),
                    max_words=cfg.get("merge_max_words", 18),
                )
                logger.info(f"✓ 精修後字幕: {Path(en_srt_path).name}\n")

            # 步驟 3: TTS - 文字轉語音 (斷點續傳)
            logger.info("【步驟 3/4】生成英文語音 (TTS)...")
            audio_segments = self.tts.generate_audio_from_srt(
                srt_path=en_srt_path,
                output_dir=str(config.AUDIO_DIR),
                ref_audio=ref_audio or config.TTS_CONFIG.get("ref_audio_path"),
                skip_existing=True  # 跳過已存在的音頻
            )
            logger.info(f"✓ 已生成 {len(audio_segments)} 個音頻片段\n")
            
            # 步驟 4: 影音精準對齊與影片合成
            logger.info("【步驟 4/4】精準對齊與影片合成...")
            
            aligned_dir = os.path.join(config.FINAL_VIDEO_DIR, "temp_aligned")
            os.makedirs(aligned_dir, exist_ok=True)
            final_audio = os.path.join(aligned_dir, f"{video_name}_final_synced.wav")
            
            logger.info("   -> 進行音頻長度動態調整與組裝...")
            align_audio(
                srt_path=str(en_srt_path),
                base_dir=str(config.AUDIO_DIR),
                output_dir=aligned_dir,
                video_name=video_name,
                final_audio_path=final_audio
            )
            
            # 使用 FFmpeg 將原始影片的影像與新的對齊音軌合併
            logger.info("   -> 將對齊音軌縫合至原始影像...")
            output_video = str(config.FINAL_VIDEO_DIR / f"{video_name}_EN.mp4")
            cmd_merge = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", final_audio,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-map", "0:v:0",
                "-map", "1:a:0",
                output_video
            ]
            
            result = subprocess.run(cmd_merge, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                logger.error(f"❌ FFmpeg 合併失敗: {result.stderr.decode('utf-8', errors='ignore')}")
                logger.info("❌ 合成失敗，保留中間音訊檔與暫存以供後續重試及除錯...")
            else:
                logger.info(f"✓ 影片合成完成: {output_video}")
                # 清理暫存檔與無數的小段音頻片段
                logger.info("🧹 清理中間生成的音頻暫存檔...")
                for seg in audio_segments:
                    path = seg.get('audio_path')
                    if path and os.path.exists(path):
                        try:
                            # 為了保險起見，可以暫不刪除，或這裡的除外
                            os.remove(path)
                        except Exception: 
                            pass
                shutil.rmtree(aligned_dir, ignore_errors=True)
            
            logger.info(f"✓ 影片處理完成: {output_video}\n")
            
            logger.info(f"{'='*60}")
            logger.info(f"✅ {video_name} 處理成功！")
            logger.info(f"{'='*60}\n")
            
            return output_video
        
        except Exception as e:
            logger.error(f"❌ 處理失敗: {e}")
            raise
    
    def process_batch(self, video_dir=None, pattern="*.mp4", ref_audio=None, subtitle_only=False):
        """
        批次處理多個影片
        
        Args:
            video_dir: 影片目錄（預設使用 config 中的設定）
            pattern: 檔案匹配模式
            ref_audio: 參考音頻路徑（用於聲音克隆，可選）
            subtitle_only: 只生成字幕（跳過TTS和視頻合成）
        """
        video_dir = Path(video_dir or config.VIDEO_DIR)
        video_files = sorted(video_dir.glob(pattern))
        
        if not video_files:
            logger.warning(f"在 {video_dir} 中找不到符合 {pattern} 的影片")
            return
        
        logger.info(f"\n找到 {len(video_files)} 個影片待處理：")
        for i, video in enumerate(video_files, 1):
            logger.info(f"  {i}. {video.name}")
        logger.info("")
        
        # 處理每個影片
        results = []
        for i, video_path in enumerate(video_files, 1):
            logger.info(f"\n進度: [{i}/{len(video_files)}]")
            try:
                output = self.process_single_video(str(video_path), ref_audio=ref_audio, subtitle_only=subtitle_only)
                results.append({"video": video_path.name, "status": "成功", "output": output})
            except Exception as e:
                results.append({"video": video_path.name, "status": "失敗", "error": str(e)})
                logger.error(f"跳過此影片，繼續處理下一個...\n")
        
        # 輸出總結
        logger.info("\n" + "="*60)
        logger.info("批次處理完成！")
        logger.info("="*60)
        logger.info(f"總計: {len(results)} 個影片")
        logger.info(f"成功: {sum(1 for r in results if r['status'] == '成功')} 個")
        logger.info(f"失敗: {sum(1 for r in results if r['status'] == '失敗')} 個")
        logger.info("="*60 + "\n")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="影片翻譯自動化處理工具")
    parser.add_argument("--video", "-v", type=str, help="單個影片路徑")
    parser.add_argument("--batch", "-b", action="store_true", help="批次處理模式")
    parser.add_argument("--dir", "-d", type=str, help="影片目錄（批次模式）")
    parser.add_argument("--ref-audio", "-r", type=str, help="參考音頻路徑（用於聲音克隆）")
    parser.add_argument("--subtitle-only", "-so", action="store_true", help="只輸出中文字幕（跳過TTS和視頻合成）")
    parser.add_argument("--xtts", action="store_true", help="啟用 XTTS-v2 跨語言聲音克隆")
    gemini_group = parser.add_mutually_exclusive_group()
    gemini_group.add_argument("--gemini", action="store_true", help="啟用 Gemini 校稿")
    gemini_group.add_argument("--no-gemini", action="store_true", help="停用 Gemini 校稿")
    refine_group = parser.add_mutually_exclusive_group()
    refine_group.add_argument("--refine", action="store_true", help="啟用英文字幕三段式精修（去贅詞+AI潤色+短句合併）")
    refine_group.add_argument("--no-refine", action="store_true", help="停用英文字幕精修")
    
    args = parser.parse_args()

    if args.gemini:
        config.GEMINI_CONFIG["enabled"] = True
    elif args.no_gemini:
        config.GEMINI_CONFIG["enabled"] = False
    
    if args.refine:
        config.EN_REFINE_CONFIG["enabled"] = True
    elif args.no_refine:
        config.EN_REFINE_CONFIG["enabled"] = False

    if args.xtts:
        config.TTS_CONFIG["use_xtts"] = True
    
    # 創建輸出目錄
    for dir_path in [config.SUBTITLE_DIR, config.AUDIO_DIR, config.FINAL_VIDEO_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 初始化處理流程
    pipeline = VideoTranslationPipeline()
    
    # 執行處理
    if args.video:
        # 單個影片處理
        pipeline.process_single_video(args.video, ref_audio=args.ref_audio, subtitle_only=args.subtitle_only)
    elif args.batch:
        # 批次處理
        pipeline.process_batch(video_dir=args.dir, ref_audio=args.ref_audio, subtitle_only=args.subtitle_only)
    else:
        # 預設：處理 video 資料夾中的所有影片
        logger.info("未指定參數，將處理 video 資料夾中的所有影片")
        pipeline.process_batch(ref_audio=args.ref_audio, subtitle_only=args.subtitle_only)


if __name__ == "__main__":
    main()
