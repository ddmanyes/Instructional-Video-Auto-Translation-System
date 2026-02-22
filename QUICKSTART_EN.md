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

### 1. Installation & Performance Acceleration (Recommended via uv)

This project supports **RTX 4090 GPU Hardware Acceleration**. Using `uv` automatically installs compatible CUDA packages, ensuring a 5x+ increase in generation speed.

```powershell
# Clone and enter the folder
# Run sync to automatically configure the best environment for your GPU
uv sync
```

### 2. Install FFmpeg (Required)

```powershell
# Using Chocolatey (Recommended)
choco install ffmpeg

# Or download from the official site and add to PATH
# https://ffmpeg.org/download.html
```

### 3. Set API Keys (Optional)

**Defaults to free Google Translate, no setup required!** 🎉

If you want to use professional AI translation (Paid), choose one of the following:

**Option A: Environment Variables**
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

**Option B: Modify config.py**
```python
TRANSLATION_CONFIG = {
    "api_provider": "openai",  # Change to openai or anthropic
}
OPENAI_API_KEY = "sk-your-key-here"
```

## ✅ Verify Installation

```powershell
uv run python test_setup.py
```

This checks all necessary dependencies and configurations.

## 🎬 Getting Started

### One-Click Fully Automatic Mode (Highly Recommended)

The latest `main.py` integrates all the automation magic! It handles translation, TTS generation, **Dynamic Audio Alignment (`align_audio`)** to ensure precision, and final merging. It also **automatically clears thousands of temporary audio files** to save space.

**Standard Automatic Processing (EdgeTTS):**
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4"
```

**Voice Cloning (XTTS) Processing:**
Provide a reference audio file.
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4" --ref-audio "teacher_voice.wav" --xtts
```

**Batch Processing a Folder:**
```powershell
uv run python main.py --batch
```

### Two-Stage Workflow with Manual Correction (Advanced)

If you want to polish transcribed Chinese subtitles before translation and dubbing:

1.  **Stage 1 - Extract Initial Subtitles**:
    ```powershell
    uv run python main.py --video "video\Neurophysiology-1.mp4" --subtitle-only
    ```
2.  **Manual Correction**: Edit `output\subtitles\Neurophysiology-1_zh.srt`. Once done, rename it to `Neurophysiology-1_zh_corrected.srt`.
3.  **Stage 2 - Automatic Continuation**: Run the standard command; the program will **automatically detect** your `_corrected` file and skip directly to translation and XTTS.
    ```powershell
    uv run python main.py --video "video\Neurophysiology-1.mp4" --ref-audio "teacher_voice.wav" --xtts
    ```

## 📊 Processing Workflow Detailed

1.  **Extract Subtitles** - AI extracts Chinese text.
2.  **Translate Subtitles** - Optimized for 100+ medical terms.
3.  **Generate Speech** - TTS or Voice Cloning.
4.  **Precise Alignment** - Time-stretching audio to match visuals.
5.  **Synthesis & Cleanup** - FFmpeg merging and clearing temporary assets.

## 🐛 Troubleshooting

-   **"CUDA out of memory"**: Switch to a smaller Whisper model size in `config.py`.
-   **"FFmpeg not found"**: Ensure FFmpeg is in your system PATH.
-   **XTTS not working**: Ensure `uv sync` completed and you have an NVIDIA GPU.

---
**Updated**: February 22, 2026
