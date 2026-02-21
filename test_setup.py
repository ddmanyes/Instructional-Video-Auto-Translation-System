"""
測試腳本 - 驗證各模組功能
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_imports():
    """測試模組導入"""
    logger.info("測試模組導入...")
    try:
        from modules import ASRProcessor, SubtitleTranslator, TTSProcessor, VideoAssembler
        import config
        logger.info("✓ 所有模組導入成功")
        return True
    except Exception as e:
        logger.error(f"✗ 模組導入失敗: {e}")
        return False


def test_directories():
    """測試目錄結構"""
    logger.info("測試目錄結構...")
    import config
    
    dirs = [
        config.VIDEO_DIR,
        config.OUTPUT_DIR,
        config.SUBTITLE_DIR,
        config.AUDIO_DIR,
        config.FINAL_VIDEO_DIR
    ]
    
    all_exist = True
    for dir_path in dirs:
        if dir_path.exists():
            logger.info(f"✓ {dir_path}")
        else:
            logger.warning(f"⚠ {dir_path} 不存在，將自動創建")
            dir_path.mkdir(parents=True, exist_ok=True)
            all_exist = False
    
    return all_exist


def test_video_files():
    """測試影片檔案"""
    logger.info("檢查影片檔案...")
    import config
    
    video_files = list(config.VIDEO_DIR.glob("*.mp4"))
    
    if not video_files:
        logger.warning("⚠ video 資料夾中沒有 .mp4 檔案")
        return False
    
    logger.info(f"✓ 找到 {len(video_files)} 個影片檔案:")
    for i, video in enumerate(video_files[:5], 1):  # 只顯示前 5 個
        logger.info(f"  {i}. {video.name}")
    
    if len(video_files) > 5:
        logger.info(f"  ... 還有 {len(video_files) - 5} 個檔案")
    
    return True


def test_api_keys():
    """測試 API 金鑰"""
    logger.info("檢查 API 金鑰...")
    import config
    
    if config.TRANSLATION_CONFIG["api_provider"] == "google":
        logger.info("✓ 使用 Google Translate（免費，無需 API 金鑰）")
        return True
    
    has_key = False
    
    if config.OPENAI_API_KEY:
        logger.info("✓ OPENAI_API_KEY 已設定")
        has_key = True
    else:
        logger.warning("⚠ OPENAI_API_KEY 未設定")
    
    if config.ANTHROPIC_API_KEY:
        logger.info("✓ ANTHROPIC_API_KEY 已設定")
        has_key = True
    else:
        logger.warning("⚠ ANTHROPIC_API_KEY 未設定")
    
    if not has_key and config.TRANSLATION_CONFIG["api_provider"] != "google":
        logger.warning("⚠ 當前配置需要 API 金鑰，請設定或改用 Google Translate")
        return False
    
    return True


def test_dependencies():
    """測試依賴套件"""
    logger.info("檢查依賴套件...")
    
    required_packages = [
        'faster_whisper',
        'openai',
        'anthropic',
        'deep_translator',
        'moviepy',
        'librosa',
        'soundfile',
        'numpy',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✓ {package}")
        except ImportError:
            logger.error(f"✗ {package} 未安裝")
            all_installed = False
    
    return all_installed


def test_ffmpeg():
    """測試 FFmpeg"""
    logger.info("檢查 FFmpeg...")
    import subprocess
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✓ {version_line}")
            return True
        else:
            logger.error("✗ FFmpeg 執行失敗")
            return False
    except FileNotFoundError:
        logger.error("✗ 未找到 FFmpeg，請先安裝")
        logger.info("  Windows: choco install ffmpeg")
        logger.info("  Linux: sudo apt-get install ffmpeg")
        logger.info("  macOS: brew install ffmpeg")
        return False
    except Exception as e:
        logger.error(f"✗ FFmpeg 檢查失敗: {e}")
        return False


def main():
    """執行所有測試"""
    print("\n" + "="*60)
    print("  系統環境檢查")
    print("="*60 + "\n")
    
    tests = [
        ("模組導入", test_imports),
        ("目錄結構", test_directories),
        ("影片檔案", test_video_files),
        ("API 金鑰", test_api_keys),
        ("依賴套件", test_dependencies),
        ("FFmpeg", test_ffmpeg),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        result = test_func()
        results.append((name, result))
        print()
    
    # 總結
    print("="*60)
    print("  檢查結果總結")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} - {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n通過: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有檢查通過！可以開始使用系統。")
        print("\n執行以下命令開始處理影片：")
        print("  python main.py --batch")
        return 0
    else:
        print("\n⚠️  部分檢查未通過，請先解決上述問題。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
