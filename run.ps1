# 快速啟動腳本 - Windows PowerShell

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  教學影片自動翻譯系統" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Python
Write-Host "[1/4] 檢查 Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 未找到 Python，請先安裝 Python 3.8+" -ForegroundColor Red
    exit 1
}

# 檢查 FFmpeg
Write-Host "[2/4] 檢查 FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version | Select-String "ffmpeg version" | Select-Object -First 1
    Write-Host "✓ FFmpeg 已安裝" -ForegroundColor Green
} catch {
    Write-Host "✗ 未找到 FFmpeg" -ForegroundColor Red
    Write-Host "請執行: choco install ffmpeg" -ForegroundColor Yellow
    $install = Read-Host "是否現在安裝? (y/n)"
    if ($install -eq "y") {
        choco install ffmpeg
    } else {
        exit 1
    }
}

# 檢查依賴
Write-Host "[3/4] 檢查 Python 依賴..." -ForegroundColor Yellow
if (-Not (Test-Path "venv")) {
    Write-Host "創建虛擬環境..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "啟動虛擬環境..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "安裝依賴套件..." -ForegroundColor Yellow
pip install -r requirements.txt

# 檢查環境變數
Write-Host "[4/4] 檢查環境變數..." -ForegroundColor Yellow
if (-Not $env:OPENAI_API_KEY -and -Not $env:ANTHROPIC_API_KEY) {
    Write-Host "⚠ 未設定 API 金鑰" -ForegroundColor Yellow
    Write-Host "請設定環境變數或修改 config.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "範例:" -ForegroundColor Cyan
    Write-Host '  $env:OPENAI_API_KEY="your-key-here"' -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  環境設定完成！" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# 選單
Write-Host "請選擇操作:" -ForegroundColor Cyan
Write-Host "  1. 批次處理所有影片" -ForegroundColor White
Write-Host "  2. 處理單個影片" -ForegroundColor White
Write-Host "  3. 僅測試 ASR (提取字幕)" -ForegroundColor White
Write-Host "  4. 僅測試翻譯" -ForegroundColor White
Write-Host "  5. 退出" -ForegroundColor White
Write-Host ""

$choice = Read-Host "請輸入選項 (1-5)"

switch ($choice) {
    "1" {
        Write-Host "開始批次處理..." -ForegroundColor Green
        python main.py --batch
    }
    "2" {
        $videos = Get-ChildItem -Path "video" -Filter "*.mp4"
        Write-Host ""
        Write-Host "可用影片:" -ForegroundColor Cyan
        for ($i=0; $i -lt $videos.Count; $i++) {
            Write-Host "  $($i+1). $($videos[$i].Name)" -ForegroundColor White
        }
        Write-Host ""
        $videoChoice = Read-Host "請選擇影片編號"
        $selectedVideo = $videos[[int]$videoChoice - 1].FullName
        python main.py --video "$selectedVideo"
    }
    "3" {
        Write-Host "測試 ASR 功能..." -ForegroundColor Green
        python -c "from modules.asr import ASRProcessor; asr = ASRProcessor(model_size='base'); print('ASR 模組載入成功')"
    }
    "4" {
        Write-Host "測試翻譯功能..." -ForegroundColor Green
        python -c "from modules.translator import SubtitleTranslator; t = SubtitleTranslator(); print('翻譯模組載入成功')"
    }
    "5" {
        Write-Host "再見！" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "無效選項" -ForegroundColor Red
    }
}
