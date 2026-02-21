@echo off
REM 使用 UV 虛擬環境運行專案

echo ====================================
echo   生理影片翻譯系統 - UV 環境
echo ====================================
echo.

REM 檢查虛擬環境是否存在
if not exist ".venv" (
    echo [錯誤] 找不到 .venv 虛擬環境
    echo 請先執行: uv venv
    pause
    exit /b 1
)

REM 顯示選單
echo 請選擇操作:
echo   1. 批次處理所有影片
echo   2. 處理單個影片
echo   3. 測試醫學術語
echo   4. 進入 Python Shell
echo   5. 列出已安裝套件
echo.

set /p choice="請輸入選項 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 開始批次處理所有影片...
    .\.venv\Scripts\python.exe main.py --batch
) else if "%choice%"=="2" (
    echo.
    echo 可用影片:
    dir /b video\*.mp4
    echo.
    set /p video="請輸入影片檔名: "
    .\.venv\Scripts\python.exe main.py --video "video\%video%"
) else if "%choice%"=="3" (
    echo.
    echo 測試醫學術語...
    .\.venv\Scripts\python.exe test_medical_terms.py
) else if "%choice%"=="4" (
    echo.
    echo 啟動 Python Shell (Ctrl+Z 離開)...
    .\.venv\Scripts\python.exe
) else if "%choice%"=="5" (
    echo.
    echo 已安裝套件:
    .\.venv\Scripts\python.exe -m pip list
) else (
    echo.
    echo [錯誤] 無效選項
)

echo.
pause
