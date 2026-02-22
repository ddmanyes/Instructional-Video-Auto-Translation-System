# Completely Free Usage Guide 💯

This project can be used **completely free of charge**! No API keys or paid services are required.

## ✅ Free Feature List

| Feature | Technology Used | Cost |
| :--- | :--- | :--- |
| Speech-to-Text (ASR) | Faster-Whisper (Local) | **Free** |
| Subtitle Translation | Google Translate API | **Free** |
| Speech Synthesis (TTS) | Coqui XTTS-v2 (Local/Cloning) or Edge TTS | **Free** |
| Video Synthesis | FFmpeg (Local Lossless Stretching) | **Free** |

## 🚀 Quick Start (Free Version)

### 1. Install Dependencies
```powershell
uv sync
choco install ffmpeg
```

### 2. Verify Configuration
Check the translation settings in `config.py`:
```python
TRANSLATION_CONFIG = {
    "api_provider": "google",  # Using the free Google Translate
    ...
}
```

### 3. Start Processing
```powershell
uv run python main.py --batch
```

It's that simple! No API keys needed.

## 📊 Google Translate vs. Paid AI Comparison

| Feature | Google Translate (Free) | GPT-4o/Claude (Paid) |
| :--- | :--- | :--- |
| **Cost** | Completely Free | $0.3-$1.5 per video |
| **Speed** | Fast | Slower |
| **General Translation** | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Superior |
| **Medical Terminology** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Professional |
| **Naturalness** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Highly Natural |
| **Usage Limits** | None (Rate limited) | Requires API Keys & Balance |

## 💡 Recommended Usage Scenarios

### Use Free Google Translate when:
- ✅ Routine instructional video translation.
- ✅ Budget is limited.
- ✅ Fast processing is needed.
- ✅ Medium translation quality requirement.

### Upgrade to Paid AI when:
- 🎯 Highest quality medical terminology is required.
- 🎯 Extremenly natural language flow is desired.
- 🎯 Handling critical academic content.
- 🎯 Budget is sufficient.

## ⚙️ Switching Translation Providers

### Switch to Google Translate (Free)
In `config.py`:
```python
TRANSLATION_CONFIG = {
    "api_provider": "google",
}
```

### Switch to OpenAI GPT-4o (Paid)
```python
TRANSLATION_CONFIG = {
    "api_provider": "openai",
}
```
Set environment variable:
```powershell
$env:OPENAI_API_KEY="sk-your-key"
```

## 🔧 Optimizing Free Version Quality

### 1. Post-processing Medical Terms
Included professional glossary ensures accurate mapping:
```python
# Terms mapping automatically happens in translator.py
medical_terms = {
    "Action potential": "動作電位",
    # ... 100+ terms pre-configured
}
```

### 2. Manual Correction of Critical Terms
After translation, you can manually fix key terms in `output/subtitles/*_en.srt` or use the Stage 2 workflow with `_zh_corrected.srt`.

## ❓ FAQ

### Q: Does Google Translate have limits?
**A:** There is a rate limit, but typical usage will not trigger it. The program includes delay mechanisms.

### Q: Is the quality sufficient?
**A:** For general instructional content, Google Translate is excellent. For maximum precision, consider a hybrid approach or manual review.

### Q: Can I use it offline?
**A:** Google Translate requires an internet connection. Fully offline usage would require local LLMs or Argos Translate.

---
**Updated**: February 22, 2026
