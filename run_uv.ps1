# 使用 UV 虛擬環境運行專案
# PowerShell 版本

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  生理影片翻譯系統 - UV 環境" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 檢查虛擬環境是否存在
if (-Not (Test-Path ".venv")) {
    Write-Host "[錯誤] 找不到 .venv 虛擬環境" -ForegroundColor Red
    Write-Host "請先執行: uv venv" -ForegroundColor Yellow
    Read-Host "按 Enter 鍵離開"
    exit 1
}

# 顯示選單
Write-Host "請選擇操作:" -ForegroundColor Cyan
Write-Host "  1. 批次處理所有影片" -ForegroundColor White
Write-Host "  2. 處理單個影片" -ForegroundColor White
Write-Host "  3. 測試醫學術語" -ForegroundColor White
Write-Host "  4. 測試環境配置" -ForegroundColor White
Write-Host "  5. 列出已安裝套件" -ForegroundColor White
Write-Host "  6. 進入虛擬環境 Shell" -ForegroundColor White
Write-Host ""

$choice = Read-Host "請輸入選項 (1-6)"

switch ($choice) {
    "1" {
        Write-Host "`n開始批次處理所有影片..." -ForegroundColor Green
        .\.venv\Scripts\python.exe main.py --batch
    }
    "2" {
        Write-Host "`n可用影片:" -ForegroundColor Cyan
        Get-ChildItem video\*.mp4 | ForEach-Object { Write-Host "  - $($_.Name)" }
        Write-Host ""
        $video = Read-Host "請輸入影片檔名"
        .\.venv\Scripts\python.exe main.py --video "video\$video"
    }
    "3" {
        Write-Host "`n測試醫學術語..." -ForegroundColor Green
        .\.venv\Scripts\python.exe test_medical_terms.py
    }
    "4" {
        Write-Host "`n測試環境配置..." -ForegroundColor Green
        .\.venv\Scripts\python.exe test_setup.py
    }
    "5" {
        Write-Host "`n已安裝套件:" -ForegroundColor Cyan
        .\.venv\Scripts\python.exe -m pip list
    }
    "6" {
        Write-Host "`n啟動虛擬環境 Shell..." -ForegroundColor Green
        Write-Host "執行: .\.venv\Scripts\activate" -ForegroundColor Yellow
        .\.venv\Scripts\activate
    }
    default {
        Write-Host "`n[錯誤] 無效選項" -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "按 Enter 鍵繼續..."
