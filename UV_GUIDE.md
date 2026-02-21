# UV 虛擬環境使用指南

本專案使用 UV 管理 Python 環境，確保在不同機器上都能快速部署。

## 📦 環境結構

```
生理2/
├── .venv/              # UV 創建的虛擬環境
├── .python-version     # Python 版本 (3.11)
├── pyproject.toml      # 專案配置 & 依賴定義
├── uv.lock            # UV 鎖定檔案
└── LICENSE             # MIT 授權
```

## 🚀 在本機使用

### 1. 啟動虛擬環境

```powershell
# PowerShell
.\.venv\Scripts\activate

# 或直接使用 UV 的 Python
.\.venv\Scripts\python.exe main.py
```

### 2. 執行程式

```powershell
# 啟動虛擬環境後
python main.py --batch

# 或不啟動虛擬環境，直接執行
.\.venv\Scripts\python.exe main.py --batch
```

### 3. 測試環境

```powershell
# 測試醫學術語
.\.venv\Scripts\python.exe test_medical_terms.py

# 測試系統環境（較慢）
.\.venv\Scripts\python.exe test_setup.py
```

## 📤 部署到其他機器

### 方法 A：完整傳輸（推薦）

將整個專案資料夾複製到新機器，包含 `.venv` 目錄：

```powershell
# 在新機器上，直接啟動即可
cd 生理2
.\.venv\Scripts\activate
python main.py --batch
```

### 方法 B：僅傳輸程式碼（需重建環境）

如果 `.venv` 太大，只傳輸程式碼：

```powershell
# 在新機器上
cd 生理2

# 安裝 UV（如果沒有）
pip install uv

# 創建虛擬環境
uv venv

# 安裝依賴
uv pip install faster-whisper openai anthropic moviepy librosa soundfile deep-translator numpy scipy tqdm "TTS>=0.22.0"
```

### 方法 C：使用 pyproject.toml（最標準）

```powershell
# 在新機器上
cd 生理2
uv venv
uv pip install -r requirements.txt
```

## 🔧 UV 常用命令

### 環境管理

```powershell
# 創建虛擬環境
uv venv

# 刪除虛擬環境
rmdir /s .venv

# 重建環境
rmdir /s .venv
uv venv
uv pip install faster-whisper openai anthropic moviepy librosa soundfile deep-translator numpy scipy tqdm "TTS>=0.22.0"
```

### 套件管理

```powershell
# 安裝單個套件
uv pip install package-name

# 安裝多個套件
uv pip install package1 package2 package3

# 列出已安裝套件
uv pip list

# 更新套件
uv pip install --upgrade package-name

# 移除套件
uv pip uninstall package-name
```

## 📋 依賴清單

當前已安裝的主要套件：

| 套件 | 版本 | 用途 |
|------|------|------|
| faster-whisper | 1.2.1 | 語音轉文字 (ASR) |
| deep-translator | 1.11.4 | Google Translate（免費） |
| openai | 2.17.0 | GPT-4o 翻譯（選用） |
| anthropic | 0.78.0 | Claude 翻譯（選用） |
| moviepy | 2.2.1 | 影音合成 |
| librosa | 0.11.0 | 音頻處理 |
| soundfile | 0.13.1 | 音頻讀寫 |
| TTS | 0.22.0 | Coqui XTTS聲音克隆 |
| numpy | 2.3.5 | 數值運算 |
| scipy | 1.17.0 | 科學運算 |

完整清單請查看：
```powershell
uv pip list
```

## 💾 磁碟空間

- `.venv` 大小：約 1-2 GB
- 包含所有 Python 套件和依賴

如果空間有限，可以只複製程式碼到新機器後重建環境。

## ⚡ 為什麼使用 UV？

相比傳統的 `pip + venv`：

| 特性 | pip + venv | UV |
|------|-----------|-----|
| 安裝速度 | 慢 | **10-100x 更快** |
| 依賴解析 | 慢且可能衝突 | 快速且準確 |
| 跨平台 | 需要手動處理 | 自動處理 |
| 可重現性 | 需要 requirements.txt | pyproject.toml + uv.lock |

## 🐛 故障排除

### 問題：找不到 uv 命令

```powershell
# 安裝 UV
pip install uv

# 或使用 pip 的完整路徑
python -m pip install uv
```

### 問題：虛擬環境啟動後仍找不到套件

```powershell
# 確認使用的是虛擬環境的 Python
where.exe python

# 應顯示：H:\生理2\.venv\Scripts\python.exe

# 如果不是，重新啟動虛擬環境
deactivate
.\.venv\Scripts\activate
```

### 問題：套件導入很慢

第一次導入某些套件（如 openai, anthropic）可能較慢，這是正常的。後續會快很多。

## 📱 快速啟動腳本

為方便使用，可以創建啟動腳本：

```powershell
# activate_and_run.ps1
.\.venv\Scripts\activate
python main.py --batch
```

使用：
```powershell
.\activate_and_run.ps1
```

## 🆚 對比表

### 本機開發 vs 新機器部署

| 操作 | 本機 | 新機器（有 .venv） | 新機器（無 .venv） |
|------|------|------------------|------------------|
| 啟動時間 | 1秒 | 1秒 | 3-5分鐘 |
| 需要網路 | 否 | 否 | 是 |
| 磁碟傳輸 | - | 1-2 GB | 100 MB |
| 額外步驟 | 無 | 無 | 重建環境 |

**建議**：如果可能，直接複製包含 `.venv` 的完整資料夾。

---

## 🎓 實際使用範例

### 場景 1：在實驗室電腦處理影片

```powershell
cd H:\生理2
.\.venv\Scripts\activate
python main.py --video "video\Neurophysiology-1.mp4"
```

### 場景 2：批次處理所有影片

```powershell
cd H:\生理2
.\.venv\Scripts\python.exe main.py --batch
```

### 場景 3：帶回家繼續處理

```
1. 複製整個「生理2」資料夾到隨身碟
2. 在家中電腦：
   D:\> xcopy F:\生理2 D:\生理2 /E /I
   D:\> cd 生理2
   D:\生理2> .\.venv\Scripts\activate
   D:\生理2> python main.py --batch
```

---

**創建日期**: 2026年2月6日  
**UV 版本**: 0.9.24  
**Python 版本**: 3.11.14
