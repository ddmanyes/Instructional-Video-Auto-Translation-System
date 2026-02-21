import argparse
import sys
from pathlib import Path

# 將專案根目錄加入系統路徑
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.append(str(PROJECT_ROOT))

import config
from modules.translator import SubtitleTranslator

def main():
    parser = argparse.ArgumentParser(description="字幕翻譯工具")
    parser.add_argument("--file", "-f", type=str, help="指定要翻譯的 SRT 檔案路徑")
    args = parser.parse_args()

    subtitle_dir = config.SUBTITLE_DIR
    translator = SubtitleTranslator(
        api_provider=config.TRANSLATION_CONFIG["api_provider"],
        api_key=config.OPENAI_API_KEY if config.TRANSLATION_CONFIG["api_provider"] == "openai" else config.ANTHROPIC_API_KEY,
    )

    if args.file:
        # 單獨翻譯一個檔案
        srt_path = Path(args.file)
        if not srt_path.exists():
            print(f"❌ 找不到檔案: {srt_path}")
            return
        
        print(f"Translating: {srt_path.name}")
        translator.translate_subtitles(
            str(srt_path),
            target_lang=config.TRANSLATION_CONFIG["target_language"],
            output_dir=str(subtitle_dir),
        )
        print("Done")
    else:
        # 原有的批量翻譯邏輯
        preferred_suffixes = ["_zh_clean", "_zh"]
        all_zh = list(subtitle_dir.glob("*_zh*.srt"))
        print(f"Found {len(all_zh)} zh files")
        if not all_zh:
            print("No files to translate.")
            return

        by_base = {}
        for path in all_zh:
            name = path.stem
            base = name
            if "_zh" in name:
                base = name.split("_zh")[0]
            by_base.setdefault(base, []).append(path)

        selected = []
        for base, paths in by_base.items():
            chosen = None
            for suffix in preferred_suffixes:
                for candidate in paths:
                    if candidate.stem.endswith(suffix):
                        chosen = candidate
                        break
                if chosen:
                    break
            if chosen is None:
                chosen = sorted(paths)[0]
            selected.append(chosen)

        selected = sorted(selected)
        print(f"Selected {len(selected)} files for translation")

        for srt_path in selected:
            print(f"Translating: {srt_path.name}")
            translator.translate_subtitles(
                str(srt_path),
                target_lang=config.TRANSLATION_CONFIG["target_language"],
                output_dir=str(subtitle_dir),
            )
        print("Done")

if __name__ == "__main__":
    main()
