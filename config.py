"""
配置文件
"""

import os
from pathlib import Path

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent

# 路徑配置
VIDEO_DIR = PROJECT_ROOT / "video"
OUTPUT_DIR = PROJECT_ROOT / "output"
SUBTITLE_DIR = OUTPUT_DIR / "subtitles"
AUDIO_DIR = OUTPUT_DIR / "audio"
FINAL_VIDEO_DIR = OUTPUT_DIR / "final_videos"

# ASR 配置
ASR_CONFIG = {
    "model_size": "base",  # tiny, base, small, medium, large-v3 (base 較快且準確)
    "device": "cpu",  # cpu (不需要 GPU)
    "compute_type": "int8",  # int8 在 CPU 上更快
    "language": "zh",  # 原始影片語言
}

# 中文字幕清理配置（只影響輸出的中文字幕檔）
CLEANER_CONFIG = {
    "enabled": False,
    "suffix": "_zh_clean",
    "overwrite_original": False,
    "filler_words": [
        "嗯",
        "呃",
        "啊",
        "那個",
        "這個",
        "就是",
        "其實",
        "然後",
        "你知道",
        "我覺得",
    ],
    "repeat_phrases": [
        "所以所以",
        "我們我們",
        "這個這個",
        "那個那個",
        "就是就是",
    ],
    "typo_map": {
        # "內份泌": "內分泌",
        # "胰島數": "胰島素",
    },
}

# 翻譯前中文短句合併設定
# 執行時機：ASR/手動校正 → 【合併短句】→ 翻譯
# 啟用方式：設 enabled=True，或執行時加 --merge-zh 旗標
ZH_MERGE_CONFIG = {
    "enabled": False,           # 是否啟用（可由 --merge-zh / --no-merge-zh 覆蓋）
    "suffix": "_zh_merged",     # 輸出後綴（不覆蓋原檔）
    "overwrite_original": False,# True = 直接覆蓋輸入檔

    # 合併參數
    "merge_gap_ms": 400,        # 相鄰字幕容忍間隔（毫秒）
    "merge_min_chars": 8,       # 合併目標最低中文字元數（< 此值才合併）
    "merge_max_chars": 35,      # 合併後中文字元數上限（防止過長）
}


# Gemini CLI 校稿設定
GEMINI_CONFIG = {
    "enabled": False,
    "command": "npx",
    "command_args": [
        "-y",
        "@google/generative-ai-cli",
    ],
    "model": "",
    "batch_size": 8,
    "timeout": 180,
    "max_length_ratio": 1.0,
    "suffix": "_zh_gemini",
    "overwrite_original": False,
}

# 英文字幕校稿設定（生理/解剖語境）
EN_PROOFREAD_PROMPT = (
    "You are an expert medical editor for university-level physiology textbooks.\n"
    "Refine the following English subtitles for clarity, medical accuracy, and academic tone.\n\n"
    "Specific Rules:\n"
    "1. Medical Accuracy: Ensure terms like 'Action Potential', 'Homeostasis', and 'Synaptic Transmission' are used precisely.\n"
    "2. Subtitle Pacing: Simplify complex sentences to be more readable on screen (conciseness is key).\n"
    "3. Grammar: Fix any translation artifacts.\n"
    "4. Preservation: Keep '\\n' for line breaks and ensure the line count remains identical to the input.\n"
    "5. Format: Output ONLY a valid JSON array of strings."
)

EN_PROOFREAD_CONFIG = {
    "enabled": False,
    "command": "npx",
    "command_args": [
        "-y",
        "@google/generative-ai-cli",
    ],
    "model": "",
    "batch_size": 8,
    "timeout": 180,
    "max_length_ratio": 1.0,
    "suffix": "_en_proofread",
    "overwrite_original": False,
    "only_flagged": False,
}

# 英文字幕三段式精修設定（規則清理 → AI 潤色 → 短句合併）
# 執行時機：翻譯完成後、TTS 語音生成前
# 啟用方式：設 enabled=True，或執行時加 --refine 旗標
EN_REFINE_CONFIG = {
    "enabled": False,           # 是否啟用（可由 --refine / --no-refine 覆蓋）
    "suffix": "_refined",       # 輸出檔案後綴
    "overwrite_original": False,# True = 直接覆蓋輸入檔（不建議）

    # ── AI 潤色選項 ───────────────────────────────────────────────
    "ai_enabled": False,         # False = 只做規則清理+合併，不呼叫 AI
    "ai_all": False,            # True = AI 處理所有行；False = 只修中文殘留行
    "command": "npx",
    "command_args": [
        "-y",
        "@google/generative-ai-cli",
    ],
    "model": "",                # 留空使用 Gemini CLI 預設模型
    "batch_size": 8,            # AI 每批次處理條數
    "timeout": 180,             # 每批次超時秒數

    # ── 短句合併選項 ───────────────────────────────────────────────
    "merge_gap_ms": 300,        # 相鄰字幕間隔容忍度（毫秒）
    "merge_min_words": 7,       # 合併目標最低字數
    "merge_max_words": 18,      # 合併後字數上限
}

# 翻譯配置
TRANSLATION_CONFIG = {
    "api_provider": "google",  # google (免費), openai, anthropic
    "target_language": "en",
    "batch_size": 20,  # 每批次翻譯的字幕數量 (已優化聚合請求)
    "domain": "physiology",  # 專業領域：生理醫學
}

# TTS 配置
TTS_CONFIG = {
    # ── Edge TTS 模式（免費，固定音色）──────────────────────────────────
    "voice": "en-US-GuyNeural",  # Edge TTS 音色
    # 其他推薦音色：en-US-JennyNeural | en-US-AriaNeural | en-GB-RyanNeural
    "speed": 1.3,  # 語速 (0.5-2.0)

    # ── XTTS-v2 聲音克隆模式 ─────────────────────────────────────────────
    # 設為 True 以啟用跨語言聲音克隆（從中文參考音頻生成英文語音）
    "use_xtts": False,
    # 參考音頻路徑（可由命令列 --ref-audio 覆蓋）
    # 使用 scripts/extract_ref_audio.py 從影片中提取
    "ref_audio_path": "output/ref_audio/110-Gastrointestinal system-I &II-115090_ref.wav",
}

# 影音合成配置
VIDEO_ASSEMBLY_CONFIG = {
    "method": "moviepy",  # moviepy 或 ffmpeg
    "embed_subtitles": True,  # 是否嵌入硬字幕（需要 FFmpeg）
    "keep_original_audio": False,  # 是否保留原始音軌（混音）
}

# API 金鑰（建議使用環境變數）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# 日誌配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S"
}
