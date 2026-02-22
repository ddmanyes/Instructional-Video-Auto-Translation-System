# 教學影片自動翻譯系統 🎥→🌍

[English Version (英文版)](README_EN.md) | [Quick Start (英文快速入門)](QUICKSTART_EN.md)

這是一個全自動的影片翻譯系統，專為生理學教學影片設計，可將中文教學影片轉換為高品質的英文版本。

## 🌟 核心功能

1. **語音轉文字 (ASR)** - 使用 Faster-Whisper 提取中文字幕
2. **智能翻譯** - 預設使用 Google Translate（免費）+ **生理醫學術語優化**
3. **語音生成與克隆** - 支援 Edge TTS (預設版) 與 **Coqui XTTS-v2** 聲音克隆 (保留原講者特色)
4. **精確對齊與合成** - 使用 `align_audio.py` 自動計算時長以 `FFmpeg` 無損伸縮，徹底解決影音不同步
5. **GPU 加速與版本鎖定** - 深度整合 **NVIDIA RTX 4090 (CUDA 12.1)**，速度提升 5 倍；手動鎖定 `transformers` 與 `torch` 版本以確保系統極度穩定
6. **模組化腳本管道** - 可單獨呼叫翻譯、提取參考音訊、TTS生成、音軌對齊等流程

## 🎓 專為生理醫學設計

- **100+ 專業術語對照表**: 涵蓋神經、內分泌、呼吸、循環、消化、生殖等系統
- **智能術語優化**: 自動檢查並確保醫學術語翻譯準確
- **學術語氣調整**: 適合大學醫學教育使用
- 詳見 [MEDICAL_TERMS.md](MEDICAL_TERMS.md) 查看完整術語列表

## 💰 成本說明

- **完全免費**: 使用預設配置（Google Translate + 醫學術語優化）
- **付費選項**: 若需要更專業的醫學術語翻譯，可選用 OpenAI/Claude

## 🔬 醫學術語準確度

系統內建 **100+ 生理醫學專業術語**，涵蓋：
- 神經系統 (action potential, neurotransmitter, synapse...)
- 內分泌系統 (hormone, insulin, thyroid gland...)
- 呼吸系統 (alveolus, gas exchange, vital capacity...)
- 循環系統 (cardiac output, blood pressure...)
- 消化系統 (peristalsis, gastric acid...)
- 生殖系統 (ovulation, menstrual cycle...)

查看 [MEDICAL_TERMS.md](MEDICAL_TERMS.md) 瞭解完整術語列表。

## 📁 專案結構

```
生理2/
├── video/                    # 原始影片資料夾
├── output/                   # 輸出資料夾
│   ├── subtitles/           # 生成的字幕檔案
│   ├── audio/               # 生成的音頻片段
│   └── final_videos/        # 最終處理完成的影片
├── modules/                  # 核心功能模組
│   ├── asr.py              # 語音轉文字模組
│   ├── subtitle_cleaner.py # 中文字幕清理/校稿模組
│   ├── translator.py       # 翻譯模組
│   ├── tts.py              # 語音合成模組
│   └── video_assembler.py  # 影音合成模組
├── config.py                # 配置檔案
├── main.py                  # 主程式
├── requirements.txt         # Python 依賴
└── README.md               # 本說明文件
```

## 🚀 快速開始

### 方法 A：使用 UV（推薦 - 穩定且現代）

**系統需求：**
- **Python**: 3.11+
- **GPU (推薦)**: NVIDIA GPU (RTX 30系/40系) 並安裝 CUDA 12.1+
- **Memory**: 16GB+ RAM (XTTS 運算建議)

```powershell
# 1. 確保環境與效能依賴對齊 (會自動根據 pyproject.toml 安裝 CUDA 加速版)
uv sync

# 2. 生成聲音克隆影片 (極速 GPU 模式)
uv run python main.py --video "video/example.mp4" --ref-audio "teacher.wav" --xtts

# 3. 批次處理所有影片
uv run python main.py --batch
```

詳見 [UV_GUIDE.md](UV_GUIDE.md) 完整說明。

### 方法 B：傳統 pip 安裝

### 1. 環境準備

#### 安裝 Python 依賴

```powershell
pip install -r requirements.txt
```

#### 安裝 FFmpeg

**Windows (使用 Chocolatey):**
```powershell
choco install ffmpeg
```

**或手動下載:**
- 下載: https://ffmpeg.org/download.html
- 解壓並添加到系統 PATH

### 2. 配置 API 金鑰（可選）

**使用預設 Google Translate（免費）**: 無需配置，直接跳過此步驟！

**若要使用 付費 AI 翻譯**: 創建環境變數或直接在 [config.py](config.py) 中設定：

```powershell
# PowerShell（可選）
$env:OPENAI_API_KEY="your-api-key-here"  # 若使用 OpenAI
$env:ANTHROPIC_API_KEY="your-api-key-here"  # 若使用 Claude
```

### 3. 配置聲音克隆 Coqui XTTS-v2（可選）

如需保留講者原生音色，請透過 UV 安裝 `TTS` (需使用 0.22.0 或以上)：
```powershell
uv pip install "TTS>=0.22.0"
```

### 4. 運行程式 - 一鍵全自動模式 (推薦)

最新版 `main.py` 已經整合了自動化音軌拉伸對齊 (`align_audio`) 與**垃圾清除功能**。它可以無腦地一鍵跑完影片解碼、ASR、翻譯、對齊、合成。

#### 處理單個影片
```powershell
uv run python main.py --video "video/Neurophysiology-1.mp4"
```

#### 使用聲音克隆 (直接全自動跑完 XTTS 到影片產出)
```powershell
uv run python main.py --video "video/Neurophysiology-1.mp4" --ref-audio "reference_voice.wav"
```

#### 批次處理所有資料夾影片
```powershell
uv run python main.py --batch
```

#### 手動校正字幕結合兩階段全自動處理 (極端推薦)

若你非常在意翻譯成效並希望先行手動優化生成的中文稿：
1. **第一階段 (僅提取原始字幕)**：
   利用 `--subtitle-only` 參數只提取第一手的 ASR `_zh.srt`（處理極快）：
   ```powershell
   uv run python main.py --video "video/Neurophysiology-1.mp4" --subtitle-only
   ```
2. **手動編輯**：打開字幕檔修正語句與錯字後，儲存成 `_zh_corrected.srt`。
3. **第二階段 (續傳全自動流程)**：
   再次下達同樣的一鍵指令（例如加入 XTTS），程式將**自動辨識與採納修改後的檔案**，接續並自動化無痛完成翻譯、TTS、對齊與結合。
   ```powershell
   uv run python main.py --video "video/Neurophysiology-1.mp4" --ref-audio "reference.wav"
   ```

### 5. 模組化進階腳本執行 (可單獨呼叫)

如果不幸執行中斷或只想更新配音，你可以分拆多個模組化腳本分階段執行：

#### A. 翻譯中文字幕
```powershell
uv run python scripts/translate_subs.py
```

#### B. 提取參考音訊 (只有使用 XTTS 時才需要)
擷取片花中的一小段作為克隆依據。
```powershell
uv run python scripts/extract_ref_audio.py --video "video/Neurophysiology-1.mp4"
```

#### C. 生成 AI 語音 (支援 EdgeTTS 與 XTTS)
```powershell
# 預設 Edge TTS：
uv run python scripts/generate_tts.py --srt "output/subtitles/Neurophysiology-1_en.srt"

# 如果你啟用 XTTS 聲音克隆：
uv run python scripts/generate_tts.py --srt "output/subtitles/Neurophysiology-1_en.srt" --xtts --ref "output/ref_audio/Neurophysiology-1_ref.wav"
```

#### D. 影音精準對齊與後製合成
自動套用 FFmpeg 的 `atempo` 並且填補靜音（無損 Time Stretch 伸縮時間長度），完美對上口型與投影片進度：
```powershell
uv run python scripts/align_audio.py
```
*(執行完後，你可以用 FFmpeg 把合併好的音軌與原影像結合，`align_audio.py` 中也有提示對應指令)*

-------

## ⚙️ 配置說明

在 [config.py](config.py) 中可自訂以下設定：

### ASR 配置

```python
ASR_CONFIG = {
    "model_size": "large-v3",  # 模型大小
    "device": "cuda",          # cuda 或 cpu
    "compute_type": "float16", # 計算類型
}
```

### 翻譯配置

```python
TRANSLATION_CONFIG = {
    "api_provider": "google",  # google (免費), openai, anthropic
    "target_language": "en",
    "batch_size": 10,
}
```

### TTS 配置

```python
TTS_CONFIG = {
    "voice": "en-US-GuyNeural",  # Edge TTS 音色
    "speed": 1.3,                # 語速
}
```

### 中文字幕清理/校稿配置

```python
CLEANER_CONFIG = {
    "enabled": True,
    "suffix": "_zh_clean",
    "overwrite_original": False,
    "filler_words": ["嗯", "呃", "啊", "那個", "這個", "就是"],
    "repeat_phrases": ["所以所以", "我們我們"],
    "typo_map": {},
}

GEMINI_CONFIG = {
    "enabled": True,
    "model": "",  # 留空使用 CLI 預設模型
    "batch_size": 20,
    "timeout": 120,
    "suffix": "_zh_gemini",
    "overwrite_original": False,
}
```

## 📊 處理流程

```
原始影片 (video/*.mp4)
    ↓
[步驟 1] ASR - 提取中文字幕
    ↓
output/subtitles/*_zh.srt
    ↓
[可選] 規則清理/校稿 - 清理贅詞與錯字
    ↓
output/subtitles/*_zh_clean.srt / *_zh_gemini.srt
    ↓
[步驟 2] 翻譯 - 生成英文字幕
    ↓
output/subtitles/*_en.srt
    ↓
[步驟 3] TTS - 生成英文語音
    ↓
output/audio/*_seg_*.wav
    ↓
[步驟 4] 完美時長對齊與影片合成
    ↓
[步驟 5] 清理垃圾與數以千計的中間音檔...
output/final_videos/*_EN.mp4 (最終成品)
```

## 🎯 進階功能

### 聲音克隆 (Voice Cloning, Coqui XTTS-v2)

可從原始影片中獨立提取音頻，作為參考模型：

```powershell
uv run python scripts/extract_ref_audio.py --video "video/Neurophysiology-1.mp4" --start 30 --duration 15
```
然後利用 `--xtts` 與 `--ref` 選項輸入給 TTS 生成器：
```powershell
uv run python scripts/generate_tts.py --srt "output/subtitles/xxx_en.srt" --xtts --ref "output/ref_audio/xxx_ref.wav"
```

### 自訂翻譯提示詞

在 [modules/translator.py](modules/translator.py#L89) 中修改提示詞以調整翻譯風格。

### 語速調整與對齊 (`align_audio.py` / `main.py`)

為了解決中文翻譯成英文後，語意變長導致音軌失控的問題，這套管線 (`main.py`) 已內嵌了強制的動態語速校正：
透過調用同等於 `scripts/align_audio.py` 的邏輯，程式會自動讀取字幕規範的理想長度 `target_dur` 去利用 FFmpeg **無損 Time-Stretch** 動態加速每一句話，最後加上必要留白後合成一軌完美的 `.wav`，並且**自動抹除數千個中間雜亂切塊**與暫存檔。

## 🛠️ 故障排除

### GPU 加速

如果有 NVIDIA GPU，安裝 CUDA 版本的 PyTorch：

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 記憶體不足

處理大型影片時，可降低 Whisper 模型大小：

```python
ASR_CONFIG = {
    "model_size": "medium",  # 改為 medium 或 base
}
```

### 聲音克隆模型記憶體 / 環境問題

若 `Coqui TTS` 報錯或需要重新安裝 `torch` 與 `torchaudio`，可用 `uv pip` 單獨覆蓋重裝並將 `--extra-index-url` 指定於 `cu118` / `cu121` 相關輪子，讓 GPU 加速生效。

## 🔧 Gemini 校稿開關

可在命令列切換是否啟用 Gemini 校稿：

```powershell
python main.py --batch --gemini
python main.py --batch --no-gemini
```

## 📝 已處理影片列表

目前 video 資料夾中有以下影片待處理：

1. 110-Gastrointestinal system-I &II.mp4
2. 110-Gastrointestinal system-III.mp4
3. Endocrine-1.mp4
4. Endocrine-2.mp4
5. Endocrine-3.mp4
6. Neurophysiology-1.mp4
7. Neurophysiology-2.mp4
8. Neurophysiology-3.mp4
9. Reproduction-1.mp4
10. Respiratory system I.mp4
11. Respiratory system II.mp4
12. reproduction-2.mp4

## 📄 授權

本專案僅供教育用途。

## 🤝 貢獻

如有問題或建議，歡迎提出 Issue 或 Pull Request。

## 📚 相關文件

- [UV_GUIDE.md](UV_GUIDE.md) - **UV 虛擬環境完整使用指南**
- [QUICKSTART.md](QUICKSTART.md) - 快速入門指南
- [MEDICAL_TERMS.md](MEDICAL_TERMS.md) - 完整醫學術語對照表（100+）
- [MEDICAL_OPTIMIZATION.md](MEDICAL_OPTIMIZATION.md) - 生理醫學領域優化說明
- [COST_FREE_GUIDE.md](COST_FREE_GUIDE.md) - 完全免費使用指南

## 🧪 測試工具

```powershell
# 使用 UV 虛擬環境

# 醫學術語測試（推薦先執行這個）
.\.venv\Scripts\python.exe test_medical_terms.py

# 環境測試（較慢）
.\.venv\Scripts\python.exe test_setup.py

# 或使用互動式腳本
.\run_uv.ps1
```
