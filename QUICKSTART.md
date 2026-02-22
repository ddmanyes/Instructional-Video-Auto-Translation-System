# 快速入門指南 🚀

這份指南將幫助你在 5 分鐘內開始使用影片翻譯系統。

## 🎓 專為生理醫學設計

本系統專門優化用於生理學教學影片翻譯，內建 100+ 專業醫學術語對照表，確保翻譯準確度。

## 📋 前置需求

- Windows 10/11
- Python 3.11+
- **NVIDIA GPU (推薦 RTX 30/40 系列)**
- 至少 16GB RAM (XTTS 運算建議)
- 硬碟空間：至少 20GB（用於模型和輸出檔案）

## 🔧 安裝步驟

### 1. 安裝與效能加速 (推薦使用 uv)

```powershell
uv sync
```

### 2. 安裝 FFmpeg (必需)

```powershell
choco install ffmpeg
# 或從 https://ffmpeg.org/download.html 下載
```

### 3. 安裝 Coqui XTTS-v2 (可選 - 聲音克隆功能)

```powershell
uv pip install "TTS>=0.22.0"
```

## ✅ 驗證安裝

```powershell
uv run python test_setup.py
```

## 🎬 開始使用

### 一鍵全自動模式 (強烈推薦)

**一般處理 (Edge TTS):**
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4"
```

**加入英文字幕精修 (去贅詞 + 合併短句):**
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4" --refine
```

**最高品質：XTTS 聲音克隆 + 字幕精修:**
```powershell
# 步驟 1: 提取參考音頻
uv run python scripts/extract_ref_audio.py `
    --video "video\Neurophysiology-1.mp4" --start 30 --duration 15

# 步驟 2: 完整高品質流程
uv run python main.py --video "video\Neurophysiology-1.mp4" `
    --xtts --ref-audio "output\ref_audio\Neurophysiology-1_ref.wav" `
    --refine
```

**批次處理所有影片:**
```powershell
uv run python main.py --batch --refine
```

### 結合人工校正的兩階段流程 (進階推薦)

1. **第一階段 - 僅提取原始中文字幕**：
   ```powershell
   uv run python main.py --video "video\Neurophysiology-1.mp4" --subtitle-only
   ```
2. **手動校正存檔**：打開 `output\subtitles\Neurophysiology-1_zh.srt`，修改後重新命名為 `Neurophysiology-1_zh_corrected.srt`。
3. **第二階段 - 續傳自動流程 (含精修 + XTTS)**：
   ```powershell
   uv run python main.py --video "video\Neurophysiology-1.mp4" `
       --xtts --ref-audio "output\ref_audio\Neurophysiology-1_ref.wav" `
       --refine
   ```

### 模組化命令行模式 (逐步執行)

**1. 翻譯現有中文字幕:**
```powershell
uv run python scripts/translate_subs.py
```

**2. 🆕 英文字幕三段式精修 (去贅詞 + AI 潤色 + 合併短句):**
```powershell
# 完整精修
uv run python scripts/refine_en_srt.py `
    --file "output\subtitles\Neurophysiology-1_en.srt"

# 只做規則清理 + 合併（最快，不呼叫 AI）
uv run python scripts/refine_en_srt.py `
    --file "output\subtitles\Neurophysiology-1_en.srt" --no-ai
```

**3. 提取聲音克隆參考音檔:**
```powershell
uv run python scripts/extract_ref_audio.py `
    --video "video\Neurophysiology-1.mp4" --start 30 --duration 15
```

**4. 生成 TTS 語音 (EdgeTTS 或 XTTS):**
```powershell
# 免費 Edge TTS
uv run python scripts/generate_tts.py `
    --srt "output\subtitles\Neurophysiology-1_en.srt"

# XTTS 聲音克隆（建議使用精修後的字幕）
uv run python scripts/generate_tts.py `
    --srt "output\subtitles\Neurophysiology-1_en_refined.srt" `
    --xtts --ref "output\ref_audio\Neurophysiology-1_ref.wav"
```

**5. 影片與音頻精準對齊與合成:**
```powershell
uv run python scripts/align_audio.py
```

## 📊 處理流程說明

1. **提取字幕** (約 2-5 分鐘) - AI 從影片提取中文字幕
2. **翻譯字幕** (約 1-3 分鐘) - Google Translate，自動優化 100+ 醫學術語
3. **🆕 英文字幕精修** (`--refine`, 約 1-2 分鐘):
   - 規則清理：移除 Then/Just/So 等句首贅詞（~50% 字幕改善）
   - AI 潤色：翻譯殘留中文、修飾奇怪語句
   - 合併短句：~4,676 條 → ~1,295 條（壓縮 3.6 倍）
4. **生成語音** (約 5-10 分鐘) - Edge TTS 或 XTTS 聲音克隆
5. **語音精準對齊** - 動態伸縮語音，對齊原始嘴型與畫面
6. **後處理與合成** (約 2-5 分鐘) - FFmpeg 無損合成，自動清除暫存檔

**總計時間**: 每個 1 小時影片約需 10-20 分鐘 | **成本**: **完全免費！** 🎉

## 📁 輸出檔案位置

```
output/
├── subtitles/
│   ├── Neurophysiology-1_zh.srt          # 中文字幕
│   ├── Neurophysiology-1_en.srt          # 英文字幕（翻譯後）
│   └── Neurophysiology-1_en_refined.srt  # 英文字幕（精修後）
├── ref_audio/
│   └── Neurophysiology-1_ref.wav         # XTTS 參考音頻
└── final_videos/
    └── Neurophysiology-1_EN.mp4          # 📹 最終成品
```

## ⚙️ 常見配置調整

### 永久啟用字幕精修

```python
# config.py
EN_REFINE_CONFIG = {
    "enabled": True,
    "ai_enabled": False,  # False = 只做規則清理+合併（最快）
}
```

### 永久啟用 XTTS

```python
# config.py
TTS_CONFIG = {
    "use_xtts": True,
    "ref_audio_path": "output/ref_audio/your_ref.wav",
}
```

### 沒有 GPU 的情況

```python
# config.py
ASR_CONFIG = {"model_size": "base", "device": "cpu"}
```

## 🐛 常見問題

| 問題 | 解法 |
|------|------|
| "CUDA out of memory" | `config.py` 改用較小 Whisper 模型 |
| FFmpeg not found | 確認 FFmpeg 在系統 PATH 中 |
| XTTS 無法使用 | `uv pip install "TTS>=0.22.0"`，初次需下載 1.8GB 模型 |
| 字幕有很多 Then/Just 或短碎句 | 加 `--refine` 或直接用 `scripts/refine_en_srt.py` |

## 💡 小技巧

1. **完全免費**: 預設配置使用 Google Translate
2. **最高品質**: 組合 `--refine --xtts`，字幕乾淨 + 音色保真
3. **先測小檔案**: 用 1-2 分鐘短片先測試流程
4. **斷點續傳**: 已存在的字幕/音頻會自動跳過，隨時可中斷重試

## � 相關文件

- [README.md](README.md) - 完整功能說明
- [MEDICAL_TERMS.md](MEDICAL_TERMS.md) - 100+ 生理醫學術語對照表
- [COST_FREE_GUIDE.md](COST_FREE_GUIDE.md) - 完全免費使用指南

---
**更新時間**: 2026年2月22日
