# Quick Start Guide 🚀

This guide will help you get started with the video translation system in 5 minutes.

## 🎓 Tailored for Physiology & Medicine

This system is specifically optimized for physiology instructional videos, featuring 100+ built-in medical terminology mappings to ensure translation accuracy.

## 📋 Prerequisites

-   Windows 10/11
-   Python 3.11+
-   **NVIDIA GPU (Recommended RTX 30/40 series)**
-   Minimum 16GB RAM (Recommended for XTTS)
-   Disk Space: At least 20GB (for models and output files)

## 🔧 Installation Steps

### 1. Install & Configure (Recommended via uv)

```powershell
uv sync
```

### 2. Install FFmpeg (Required)

```powershell
choco install ffmpeg
# Or: https://ffmpeg.org/download.html
```

### 3. Install Coqui XTTS-v2 (Optional - for Voice Cloning)

```powershell
uv pip install "TTS>=0.22.0"
```

## ✅ Verify Installation

```powershell
uv run python test_setup.py
```

## 🎬 Getting Started

### One-Click Fully Automatic Mode (Highly Recommended)

**Standard Processing (Edge TTS):**
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4"
```

**With Subtitle Refinement (remove fillers + merge short segments):**
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4" --refine
```

**Full Premium Pipeline: XTTS Voice Cloning + Subtitle Refinement:**
```powershell
# Step 1: Extract reference audio
uv run python scripts/extract_ref_audio.py `
    --video "video\Neurophysiology-1.mp4" --start 30 --duration 15

# Step 2: Full high-quality pipeline
uv run python main.py --video "video\Neurophysiology-1.mp4" `
    --xtts --ref-audio "output\ref_audio\Neurophysiology-1_ref.wav" `
    --refine
```

**Batch Processing:**
```powershell
uv run python main.py --batch --refine
```

### Two-Stage Workflow with Manual Correction (Advanced)

1.  **Stage 1 - Extract Initial Chinese Subtitles**:
    ```powershell
    uv run python main.py --video "video\Neurophysiology-1.mp4" --subtitle-only
    ```
2.  **Manual Correction**: Edit `output\subtitles\Neurophysiology-1_zh.srt`. Save as `Neurophysiology-1_zh_corrected.srt`.
3.  **Stage 2 - Automatic Continuation with Refinement + XTTS**:
    ```powershell
    uv run python main.py --video "video\Neurophysiology-1.mp4" `
        --xtts --ref-audio "output\ref_audio\Neurophysiology-1_ref.wav" `
        --refine
    ```

### Modular Step-by-Step Execution

**1. Translate Chinese subtitles:**
```powershell
uv run python scripts/translate_subs.py
```

**2. 🆕 Three-stage English subtitle refinement:**
```powershell
# Full refinement (rule cleanup + AI polish + merge shorts)
uv run python scripts/refine_en_srt.py `
    --file "output\subtitles\Neurophysiology-1_en.srt"

# Rule cleanup + merge only (fastest, no AI)
uv run python scripts/refine_en_srt.py `
    --file "output\subtitles\Neurophysiology-1_en.srt" --no-ai
```

**3. Extract reference audio (XTTS only):**
```powershell
uv run python scripts/extract_ref_audio.py `
    --video "video\Neurophysiology-1.mp4" --start 30 --duration 15
```

**4. Generate TTS audio (Edge TTS or XTTS):**
```powershell
# Edge TTS (free)
uv run python scripts/generate_tts.py `
    --srt "output\subtitles\Neurophysiology-1_en.srt"

# XTTS Voice Cloning (use refined subtitles for best results)
uv run python scripts/generate_tts.py `
    --srt "output\subtitles\Neurophysiology-1_en_refined.srt" `
    --xtts --ref "output\ref_audio\Neurophysiology-1_ref.wav"
```

**5. Audio alignment & synthesis:**
```powershell
uv run python scripts/align_audio.py
```

## 📊 Processing Workflow

1.  **Extract Subtitles** (~2-5 mins) - ASR extracts Chinese text.
2.  **Translate Subtitles** (~1-3 mins) - Google Translate, 100+ medical terms optimized.
3.  **🆕 Subtitle Refinement** (`--refine`, ~1-2 mins):
    -   Rule cleaning: Remove Then/Just/So sentence starters
    -   AI polishing: Translate residual Chinese, fix awkward phrasing
    -   Merge segments: ~4,676 → ~1,295 entries (3.6x compression)
4.  **Generate Speech** (~5-10 mins) - Edge TTS or XTTS voice cloning.
5.  **Precise Alignment** - Dynamically time-stretch audio to match video.
6.  **Synthesis & Cleanup** (~2-5 mins) - FFmpeg merging, auto-delete temp files.

**Total time**: ~10-20 mins per 1-hour video | **Cost**: **Free!** 🎉

## ⚙️ Key Configuration

### Permanently enable subtitle refinement

```python
# config.py
EN_REFINE_CONFIG = {
    "enabled": True,     # auto-refine every run
    "ai_enabled": False, # False = rule cleanup + merge only (fastest)
}
```

### Permanently enable XTTS voice cloning

```python
# config.py
TTS_CONFIG = {
    "use_xtts": True,
    "ref_audio_path": "output/ref_audio/your_ref.wav",
}
```

## 🐛 Troubleshooting

-   **"CUDA out of memory"**: Switch to a smaller Whisper model size in `config.py`.
-   **"FFmpeg not found"**: Ensure FFmpeg is in your system PATH.
-   **XTTS not working**: Ensure `uv pip install "TTS>=0.22.0"` completed. First run downloads ~1.8GB model.
-   **Too many filler words or short fragments**: Add `--refine` flag or use `scripts/refine_en_srt.py`.

## 💡 Tips

1.  **Completely Free**: Default config uses Google Translate — no cost.
2.  **Best Quality**: Combine `--refine --xtts` for clean subtitles + faithful voice.
3.  **Test Small First**: Try a 1-2 min clip before processing full lectures.
4.  **Resume Anytime**: Existing subtitle/audio files are auto-skipped; interrupt and retry safely.

---
**Updated**: February 22, 2026
