# 快速入門指南 🚀

這份指南將幫助你在 5 分鐘內開始使用影片翻譯系統。

## 🎓 專為生理醫學設計

本系統專門優化用於生理學教學影片翻譯，內建 100+ 專業醫學術語對照表，確保翻譯準確度。

## 📋 前置需求

- Windows 10/11
- Python 3.8 或更高版本
- 至少 8GB RAM（建議 16GB）
- 硬碟空間：至少 20GB（用於模型和輸出檔案）

## 🔧 安裝步驟

### 1. 安裝 Python 依賴

```powershell
# 建議使用虛擬環境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安裝依賴（包含免費的 Google Translate）
pip install -r requirements.txt
```

### 2. 安裝 FFmpeg

```powershell
# 使用 Chocolatey (推薦)
choco install ffmpeg

# 或從官網下載並添加到 PATH
# https://ffmpeg.org/download.html
```

### 3. 設定 API 金鑰（可選）

**預設使用免費的 Google Translate，無需任何設定！** 🎉

如果你想使用更專業的 AI 翻譯（需付費），可選擇以下任一方式：

**方式 A: 環境變數**
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

**方式 B: 修改 config.py**
```python
TRANSLATION_CONFIG = {
    "api_provider": "openai",  # 改為 openai 或 anthropic
}
OPENAI_API_KEY = "sk-your-key-here"
```

### 4. 安裝 Coqui XTTS-v2 (如果你需要聲音克隆)

如果希望生成的英文語音保留原講者的聲音特質（跨語言聲音克隆）：
```powershell
uv pip install "TTS>=0.22.0"
```

## ✅ 驗證安裝

```powershell
python test_setup.py
```

這會檢查所有必要的依賴和配置。

## 🎬 開始使用

### 使用互動式腳本 (推薦新手)

```powershell
.\run.ps1
```

這會啟動一個友善的互動介面，引導你完成整個流程。

### 一鍵全自動模式 (強烈推薦)

最新的 `main.py` 已經整合了所有的自動化魔法！它會一路跑完翻譯、生成 TTS、**動態伸縮音軌 (`align_audio`)** 來確保長短精準符合畫面，在最終合併影片之後，還會**自動把暫存幾千個零散音檔清除**替你節省空間。

**一般自動處理 (預設 EdgeTTS):**
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4"
```

**啟用聲音克隆 (XTTS) 全自動處理:**
提供一段參考音檔即可。
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4" --ref-audio "teacher_voice.wav"
```

**批次處理資料夾所有影片:**
```powershell
uv run python main.py --batch
```

### 結合人工校正的兩階段流程 (進階推薦)

如果在自動化翻譯生成配音前，你希望能先親自打磨與修改 AI 語音辨識出錯的中文：

1. **第一階段 - 僅提取原始中文字幕**：
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4" --subtitle-only
```
2. **手動校正存檔**：打開產出的 `output\subtitles\Neurophysiology-1_zh.srt` 進行編輯修改，完成後務必重新命名為 `Neurophysiology-1_zh_corrected.srt`。
3. **第二階段 - 續傳自動生成與後製**：再次執行一般的指令，程式會**自動優先偵測**你的 `_corrected` 檔，並直接跳過 AI 辨識接續完成最好的翻譯、XTTS與對齊合成：
```powershell
uv run python main.py --video "video\Neurophysiology-1.mp4" --ref-audio "teacher_voice.wav"
```

### 模組化命令行模式 (底層除錯分開執行)

如果過程有中斷，專案也支援更穩定的按步驟模組化獨立執行腳本：

**1. 翻譯現有中文字幕:**
```powershell
uv run python scripts/translate_subs.py
```

**2. 提取聲音克隆參考音檔 (可選):**
```powershell
uv run python scripts/extract_ref_audio.py --video "video\Neurophysiology-1.mp4"
```

**3. 生成 TTS 語音 (支援 EdgeTTS 與 XTTS聲音克隆):**
```powershell
# 一般免費 Edge TTS
uv run python scripts/generate_tts.py --srt "output\subtitles\Neurophysiology-1_en.srt"

# 使用聲音克隆
uv run python scripts/generate_tts.py --srt "output\subtitles\Neurophysiology-1_en.srt" --xtts --ref "output\ref_audio\Neurophysiology-1_ref.wav"
```

**4. 影片與音頻精準對齊與合成:**
```powershell
uv run python scripts/align_audio.py
```
*(程式將透過自動排程器或 `scripts/auto_xtts_pipeline.py` 一鍵全處理)*

## 📊 處理流程說明

系統會自動執行以下步驟 (`main.py`)：

1. **提取字幕** (約 2-5 分鐘) - 使用 AI 從影片提取中文字幕
2. **翻譯字幕** (約 1-3 分鐘) - 使用 Google Translate 翻譯成英文（免費！）
   - ✅ 自動優化 100+ 生理醫學專業術語
   - ✅ 確保 action potential、homeostasis 等術語準確
3. **生成語音** (約 5-10 分鐘) - 使用 TTS 生成英文語音或克隆聲音
4. **語音精準對齊** - 動態伸縮語音長度（Time-Stretch），對齊原始嘴型與畫面
5. **後處理與合成** (約 2-5 分鐘) - FFmpeg 無損替換軌道合成，並**自動清除暫存龐大數量的 TTS 碎片檔案**。

**總計時間**: 每個 1 小時的影片約需 10-20 分鐘處理  
**總計成本**: **完全免費！** 🎉  
**術語準確度**: **醫學級專業** 🎓

## 📁 輸出檔案位置

處理完成後，你會在以下位置找到檔案：

```
output/
├── subtitles/
│   ├── Neurophysiology-1_zh.srt    # 中文字幕
│   └── Neurophysiology-1_en.srt    # 英文字幕
├── audio/
│   ├── Neurophysiology-1_seg_0001.wav
│   ├── Neurophysiology-1_seg_0002.wav
│   └── ...
└── final_videos/
    └── Neurophysiology-1_EN.mp4     # 📹 最終成品
```

## ⚙️ 常見配置調整

### 如果你的電腦沒有 GPU

在 `config.py` 中修改：
```python
ASR_CONFIG = {
    "model_size": "base",  # 改用較小的模型
    "device": "cpu",       # 使用 CPU
}
```

### 如果翻譯不夠專業

修改 `modules/translator.py` 第 89 行的提示詞，加入更多專業要求。

### 如果語音太快或太慢

在 `config.py` 中調整：
```python
TTS_CONFIG = {
    "speed": 1.2,  # 1.0 是正常速度，>1 加速，<1 減速
}
```

## 🐛 常見問題

### Q: 出現 "CUDA out of memory" 錯誤
**A:** 使用較小的 Whisper 模型或切換到 CPU 模式

### Q: 預設使用免費的 Google Translate，不需要 API 金鑰。如使用付費方案，請檢查 API 金鑰與
**A:** 檢查 API 金鑰是否正確，並確認帳戶有足夠餘額

### Q: FFmpeg not found
**A:** 確認 FFmpeg 已安裝並在系統 PATH 中

### Q: 聲音克隆 (XTTS) 無法使用
**A:** 請確保你已執行 `uv pip install "TTS>=0.22.0"`，且初次執行需要下載約 1.8GB 的模型。

## 📚 下一步

- 閱讀 [README.md](README.md) 瞭解完整功能
- 查看 [config.py](config.py) 自訂所有設定
- 修改 [modules/translator.py](modules/translator.py) 調整翻譯品質
- 配置 [modules/tts.py](modules/tts.py) 整合聲音克隆功能

## 💡 小技巧
完全免費**: 預設配置使用 Google Translate，無需任何費用
2. **批次處理省時間**: 批次處理多個影片可以重複使用已載入的模型
3. **先測試小檔案**: 用 1-2 分鐘的短片先測試整個流程
4. **保留中間檔案**: 如果只需要調整音頻，可以直接使用已生成的字幕
5. **切換翻譯方式**: 需要更專業的翻譯品質時，可在 config.py 切換到付費 AI
MEDICAL_TERMS.md](MEDICAL_TERMS.md) - **100+ 生理醫學專業術語對照表**
- [
## 📚 相關文件

- [COST_FREE_GUIDE.md](COST_FREE_GUIDE.md) - 完全免費使用指南
- [README.md](README.md) - 完整功能說明
- [config.py](config.py) - 配置選項的字幕
4. **使用聲音克隆**: 提取老師的聲音樣本，讓英文版更有親切感

## ✨ 享受使用！

如有任何問題，請查看 README.md 或提出 Issue。

---
**更新時間**: 2026年2月6日
