# 🎉 UV 環境建立完成！

## ✅ 已完成項目

### 1. 虛擬環境
- ✅ 使用 UV 創建 `.venv` 虛擬環境
- ✅ Python 3.11.14
- ✅ 68 個套件已安裝

### 2. 核心依賴
- ✅ faster-whisper 1.2.1 (ASR)
- ✅ deep-translator 1.11.4 (免費翻譯)
- ✅ openai 2.17.0 (可選)
- ✅ anthropic 0.78.0 (可選)
- ✅ moviepy 2.2.1 (影音合成)
- ✅ librosa 0.11.0 (音頻處理)
- ✅ 93 個生理醫學專業術語

### 3. 配置文件
- ✅ pyproject.toml (UV 專案配置)
- ✅ .python-version (Python 3.11)
- ✅ LICENSE (MIT)

### 4. 使用指南
- ✅ UV_GUIDE.md (完整 UV 使用說明)
- ✅ run_uv.ps1 (PowerShell 互動式腳本)
- ✅ run_uv.bat (Windows 批次腳本)

## 🚀 立即開始使用

### 快速命令

```powershell
# 批次處理所有影片
.\.venv\Scripts\python.exe main.py --batch

# 處理單個影片
.\.venv\Scripts\python.exe main.py --video "video\Neurophysiology-1.mp4"

# 測試醫學術語
.\.venv\Scripts\python.exe test_medical_terms.py
```

### 互動式腳本（推薦）

```powershell
# PowerShell
.\run_uv.ps1

# 或 CMD
.\run_uv.bat
```

會顯示選單讓你選擇操作。

## 📦 部署到其他機器

### 選項 A：複製完整資料夾（最簡單）

```powershell
# 直接複製整個「生理2」資料夾到新機器
# 包含 .venv 目錄（約 1-2 GB）

# 在新機器上直接執行：
cd 生理2
.\.venv\Scripts\python.exe main.py --batch
```

### 選項 B：僅複製程式碼（需重建）

```powershell
# 複製時排除 .venv 目錄

# 在新機器上：
cd 生理2
pip install uv
uv venv
uv pip install faster-whisper openai anthropic moviepy librosa soundfile deep-translator numpy scipy tqdm "TTS>=0.22.0"
```

## 🎯 目前狀態

| 項目 | 狀態 | 說明 |
|------|------|------|
| UV 環境 | ✅ 完成 | Python 3.11.14 + 68 packages |
| 依賴安裝 | ✅ 完成 | 所有核心套件已安裝 |
| 翻譯功能 | ✅ 就緒 | Google Translate + 93 醫學術語 |
| ASR 功能 | ✅ 就緒 | Faster-Whisper (需下載模型) |
| TTS 功能 | ✅ 支援 XTTS | Coqui XTTS-v2 (聲音克隆) |
| FFmpeg | ✅ 已安裝 | 支援影音處理 |

## ⚠️ 下一步

### 1. 測試系統（推薦）

```powershell
# 快速測試（約 10 秒）
.\.venv\Scripts\python.exe -c "from modules.translator import MEDICAL_TERMS; print(f'✓ 載入 {len(MEDICAL_TERMS)} 個醫學術語')"

# 完整術語測試（約 1 分鐘）
.\.venv\Scripts\python.exe test_medical_terms.py
```

### 2. 測試聲音克隆（選用）

可先透過 `scripts/extract_ref_audio.py` 提取一小段參考影片，初次跑 `scripts/generate_tts.py --xtts` 會自動下載所需 Coqui TTS 模型 (約 1.8GB)。

### 3. 處理第一個影片

```powershell
# 建議先用較短的影片測試
.\.venv\Scripts\python.exe main.py --video "video\[選擇一個較短的影片].mp4"
```

⚠️ **注意**: 第一次執行 ASR 時，Whisper 會自動下載模型（約 1-3 GB），需要網路連線。

## 💾 磁碟空間需求

- `.venv` 虛擬環境：約 1-2 GB
- Whisper 模型（首次下載）：約 1-3 GB
- 輸出檔案：依影片數量而定

**總計建議**：至少 10 GB 可用空間

## 📘 相關文檔

| 文件 | 用途 |
|------|------|
| [UV_GUIDE.md](UV_GUIDE.md) | UV 環境完整使用說明 |
| [README.md](README.md) | 專案總覽 |
| [QUICKSTART.md](QUICKSTART.md) | 快速入門 |
| [MEDICAL_TERMS.md](MEDICAL_TERMS.md) | 醫學術語對照表 |
| [COST_FREE_GUIDE.md](COST_FREE_GUIDE.md) | 免費使用指南 |

## 🆘 常見問題

### Q: 為什麼選擇 UV？
A: UV 比傳統 pip 快 10-100 倍，且能正確解析依賴關係。

### Q: .venv 可以刪除嗎？
A: 可以，但需要重建（約 3-5 分鐘）。建議保留。

### Q: 如何更新套件？
A: `uv pip install --upgrade package-name`

### Q: 在其他機器上需要重新安裝嗎？
A: 如果複製了 .venv 目錄，不需要。否則需重建環境。

## 🎊 恭喜！

你的生理影片翻譯系統已經準備就緒！

**現在可以開始處理 15 個生理學教學影片了！**

---

**建立時間**: 2026年2月6日  
**UV 版本**: 0.9.24  
**Python 版本**: 3.11.14  
**總安裝套件**: 68 個  
**醫學術語**: 93 個
