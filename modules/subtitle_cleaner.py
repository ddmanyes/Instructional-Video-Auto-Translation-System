"""
Subtitle Cleaner
Rule-based cleanup for Chinese SRT subtitles.
"""

import json
import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class SubtitleCleaner:
    def __init__(self, filler_words=None, repeat_phrases=None, typo_map=None):
        self.filler_words = filler_words or []
        self.repeat_phrases = repeat_phrases or []
        self.typo_map = typo_map or {}

        self._repeat_map = {}
        for phrase in self.repeat_phrases:
            half = len(phrase) // 2
            if half > 0:
                self._repeat_map[phrase] = phrase[:half]

    def proofread_srt(
        self,
        srt_path,
        output_dir=None,
        suffix="_zh_gemini",
        overwrite=False,
        model=None,
        batch_size=20,
        timeout=120,
        command=None,
        command_args=None,
        max_length_ratio=1.0,
    ):
        srt_path = Path(srt_path)
        output_dir = Path(output_dir) if output_dir else srt_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        if overwrite:
            output_path = srt_path
        else:
            output_path = output_dir / f"{srt_path.stem}{suffix}{srt_path.suffix}"

        with srt_path.open("r", encoding="utf-8") as f:
            content = f.read()

        pattern = re.compile(
            r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)",
            re.DOTALL,
        )

        blocks = []
        lines = []
        for match in pattern.finditer(content):
            index = match.group(1)
            start = match.group(2)
            end = match.group(3)
            text = match.group(4)

            normalized = text.replace("\n", "\\n")
            blocks.append((index, start, end))
            lines.append(normalized)

        if not lines:
            return str(output_path)

        line_mask = [self._should_proofread_line(line) for line in lines]
        usage_records = []
        if any(line_mask):
            target_lines = [line for line, keep in zip(lines, line_mask) if keep]
            proofread_targets, usage_records = self._proofread_lines_with_gemini(
                lines=target_lines,
                model=model,
                batch_size=batch_size,
                timeout=timeout,
                command=command,
                command_args=command_args,
                max_length_ratio=max_length_ratio,
            )

            proofread_lines = []
            proofread_iter = iter(proofread_targets)
            for line, keep in zip(lines, line_mask):
                proofread_lines.append(next(proofread_iter) if keep else line)
        else:
            proofread_lines = lines

        with output_path.open("w", encoding="utf-8") as f:
            for (index, start, end), text in zip(blocks, proofread_lines):
                restored = text.replace("\\n", "\n")
                f.write(f"{index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{restored}\n\n")

        logger.info(f"Gemini 校稿完成: {output_path}")

        if usage_records:
            total_usage = self._summarize_usage(usage_records)
            logger.info(
                "Gemini token usage: input=%s output=%s total=%s",
                total_usage.get("input_tokens"),
                total_usage.get("output_tokens"),
                total_usage.get("total_tokens"),
            )
            usage_path = output_path.with_suffix(".usage.json")
            with usage_path.open("w", encoding="utf-8") as f:
                f.write(self._format_usage_json(total_usage))
            logger.info(f"Gemini token 記錄: {usage_path}")

        return str(output_path)

    def proofread_srt_with_prompt(
        self,
        srt_path,
        output_dir=None,
        suffix="_proofread",
        overwrite=False,
        prompt=None,
        model=None,
        batch_size=20,
        timeout=120,
        command=None,
        command_args=None,
        max_length_ratio=1.0,
        only_flagged=False,
    ):
        srt_path = Path(srt_path)
        output_dir = Path(output_dir) if output_dir else srt_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        if overwrite:
            output_path = srt_path
        else:
            output_path = output_dir / f"{srt_path.stem}{suffix}{srt_path.suffix}"

        with srt_path.open("r", encoding="utf-8") as f:
            content = f.read()

        pattern = re.compile(
            r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)",
            re.DOTALL,
        )

        blocks = []
        lines = []
        for match in pattern.finditer(content):
            index = match.group(1)
            start = match.group(2)
            end = match.group(3)
            text = match.group(4)

            normalized = text.replace("\n", "\\n")
            blocks.append((index, start, end))
            lines.append(normalized)

        if not lines:
            return str(output_path)

        if only_flagged:
            line_mask = [self._should_proofread_english_line(line) for line in lines]
        else:
            line_mask = [True for _ in lines]

        usage_records = []
        if any(line_mask):
            target_lines = [line for line, keep in zip(lines, line_mask) if keep]
            proofread_targets, usage_records = self._proofread_lines_with_gemini(
                lines=target_lines,
                model=model,
                batch_size=batch_size,
                timeout=timeout,
                command=command,
                command_args=command_args,
                max_length_ratio=max_length_ratio,
                prompt_override=prompt,
            )

            proofread_lines = []
            proofread_iter = iter(proofread_targets)
            for line, keep in zip(lines, line_mask):
                proofread_lines.append(next(proofread_iter) if keep else line)
        else:
            proofread_lines = lines

        with output_path.open("w", encoding="utf-8") as f:
            for (index, start, end), text in zip(blocks, proofread_lines):
                restored = text.replace("\\n", "\n")
                f.write(f"{index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{restored}\n\n")

        logger.info(f"字幕校稿完成: {output_path}")

        if usage_records:
            total_usage = self._summarize_usage(usage_records)
            logger.info(
                "Gemini token usage: input=%s output=%s total=%s",
                total_usage.get("input_tokens"),
                total_usage.get("output_tokens"),
                total_usage.get("total_tokens"),
            )
            usage_path = output_path.with_suffix(".usage.json")
            with usage_path.open("w", encoding="utf-8") as f:
                f.write(self._format_usage_json(total_usage))
            logger.info(f"Gemini token 記錄: {usage_path}")

        return str(output_path)

    def clean_srt(self, srt_path, output_dir=None, suffix="_zh_clean", overwrite=False):
        srt_path = Path(srt_path)
        output_dir = Path(output_dir) if output_dir else srt_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        if overwrite:
            output_path = srt_path
        else:
            base_stem = srt_path.stem
            if base_stem.endswith("_zh") and suffix.startswith("_zh"):
                output_stem = base_stem.replace("_zh", "") + suffix
            else:
                output_stem = base_stem + suffix
            output_path = output_dir / f"{output_stem}{srt_path.suffix}"

        with srt_path.open("r", encoding="utf-8") as f:
            content = f.read()

        pattern = re.compile(
            r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)",
            re.DOTALL,
        )

        cleaned_blocks = []
        for match in pattern.finditer(content):
            index = match.group(1)
            start = match.group(2)
            end = match.group(3)
            text = match.group(4)

            cleaned_text = self._clean_text(text)
            cleaned_blocks.append((index, start, end, cleaned_text))

        with output_path.open("w", encoding="utf-8") as f:
            for index, start, end, text in cleaned_blocks:
                f.write(f"{index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")

        logger.info(f"中文字幕清理完成: {output_path}")
        return str(output_path)

    def _clean_text(self, text):
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            original = line
            cleaned = self._clean_line(line)
            cleaned_lines.append(cleaned if cleaned else original)
        return "\n".join(cleaned_lines)

    def _clean_line(self, text):
        cleaned = text

        for wrong, correct in self.typo_map.items():
            if wrong in cleaned:
                cleaned = cleaned.replace(wrong, correct)

        for phrase, replacement in self._repeat_map.items():
            cleaned = cleaned.replace(phrase, replacement)

        for word in self.filler_words:
            pattern = rf"(?:(?<=^)|(?<=[，。！？、\s])){re.escape(word)}(?=$|[，。！？、\s])"
            cleaned = re.sub(pattern, "", cleaned)

        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = re.sub(r"\s*([，。！？、])\s*", r"\1", cleaned)
        cleaned = re.sub(r"([，。！？、]){2,}", r"\1", cleaned)
        cleaned = re.sub(r"^[，。！？、]+", "", cleaned)
        cleaned = re.sub(r"[，。！？、]+$", "", cleaned)
        cleaned = cleaned.strip()

        return cleaned

    def _proofread_lines_with_gemini(
        self,
        lines,
        model=None,
        batch_size=20,
        timeout=120,
        command=None,
        command_args=None,
        max_length_ratio=1.0,
        prompt_override=None,
    ):
        prompt = prompt_override or (
            "你是中文字幕校稿助手。請修正文句錯誤與贅詞，但不要改變意思。\n"
            "要求：\n"
            "1. 每行輸入對應一行輸出\n"
            "2. 只能輸出校稿後的文字，不要加任何說明、前言、後記\n"
            "3. 不要加入編號或符號\n"
            "4. 不要合併或拆分行\n"
            "5. 請精簡句子，避免擴寫\n"
            "6. 句長盡量接近原文（±10%），若超過請再縮短\n"
            "7. 每行輸出字數不得超過原文的 110%\n"
            "8. 如果看到\\n字樣，請保留它（代表原本的換行）\n"
            "9. 請只輸出 JSON 陣列（例如 [\"...\", \"...\"]），不得有其他文字\n"
            "10. JSON 陣列的元素數量必須等於輸入行數\n"
        )

        outputs = []
        usage_records = []
        for i in range(0, len(lines), batch_size):
            batch = lines[i:i + batch_size]
            stdin_text = "\n".join(batch)

            cmd = [command or "gemini"]
            if command_args:
                cmd.extend(command_args)
            cmd.extend(["--output-format", "json", "--prompt", prompt])
            if model:
                cmd.extend(["--model", model])

            try:
                result = subprocess.run(
                    cmd,
                    input=stdin_text,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=timeout,
                    check=True,
                )
            except Exception as exc:
                logger.error(f"Gemini 校稿失敗，改用原文: {exc}")
                outputs.extend(batch)
                continue

            out_text, usage = self._parse_gemini_json_output(result.stdout or "")
            if usage:
                usage_records.append(usage)

            raw_output = out_text.strip("\n")
            out_lines = self._parse_json_lines(raw_output, len(batch))

            if len(out_lines) != len(batch):
                logger.warning(
                    "Gemini 回傳行數不符（預期 %s，實際 %s），改用原文",
                    len(batch),
                    len(out_lines),
                )
                outputs.extend(batch)
                continue

            outputs.extend(
                [
                    self._enforce_length_limit(original, revised, max_length_ratio)
                    for original, revised in zip(batch, out_lines)
                ]
            )

        return outputs, usage_records

    def _should_proofread_line(self, line):
        if not line:
            return False

        for word in self.filler_words:
            if word and word in line:
                return True

        for wrong in self.typo_map.keys():
            if wrong and wrong in line:
                return True

        if re.search(r"([，。！？、]){2,}", line):
            return True

        if re.search(r"\s{2,}", line):
            return True

        return False

    def _should_proofread_english_line(self, line):
        if not line:
            return False

        if re.search(r"[\u4e00-\u9fff]", line):
            return True

        if re.search(r"\s{2,}", line):
            return True

        if re.search(r"([,.;!?]){2,}", line):
            return True

        return False

    def _parse_gemini_json_output(self, raw_text):
        raw_text = raw_text.strip()
        if not raw_text:
            return "", None

        try:
            payload = json.loads(raw_text)
        except Exception:
            return raw_text, None

        text = ""
        usage = None

        if isinstance(payload, dict):
            usage = self._extract_usage(payload)
            candidates = payload.get("candidates")
            if isinstance(candidates, list) and candidates:
                content = candidates[0].get("content", {}) if isinstance(candidates[0], dict) else {}
                parts = content.get("parts") if isinstance(content, dict) else None
                if isinstance(parts, list) and parts:
                    part = parts[0]
                    if isinstance(part, dict) and "text" in part:
                        text = part.get("text", "")
                elif isinstance(content, dict) and "text" in content:
                    text = content.get("text", "")
        elif isinstance(payload, list) and payload:
            first = payload[0]
            if isinstance(first, dict):
                usage = self._extract_usage(first)
                text = first.get("text", "")

        if not text:
            text = raw_text

        return text, usage

    def _parse_json_lines(self, raw_output, expected_count):
        if not raw_output:
            return []

        try:
            parsed = json.loads(raw_output)
        except Exception:
            parsed = None

        if isinstance(parsed, list):
            normalized = [str(item) for item in parsed]
            if expected_count is None or len(normalized) == expected_count:
                return normalized

        return raw_output.split("\n")

    def _enforce_length_limit(self, original, revised, max_length_ratio):
        if not original or not revised:
            return revised

        if max_length_ratio is None:
            return revised

        try:
            ratio = float(max_length_ratio)
        except (TypeError, ValueError):
            return revised

        if ratio <= 0:
            return revised

        max_len = int(len(original) * ratio)
        if max_len <= 0:
            return revised

        if len(revised) <= max_len:
            return revised

        shortened = revised[:max_len].strip()
        if not shortened:
            shortened = original[:max_len]

        return shortened

    def _extract_usage(self, payload):
        usage = payload.get("usage") if isinstance(payload, dict) else None
        if not usage and isinstance(payload, dict):
            usage = payload.get("usageMetadata")

        if not isinstance(usage, dict):
            return None

        input_tokens = usage.get("promptTokenCount") or usage.get("input_tokens")
        output_tokens = usage.get("candidatesTokenCount") or usage.get("output_tokens")
        total_tokens = usage.get("totalTokenCount") or usage.get("total_tokens")

        if input_tokens is None and output_tokens is None and total_tokens is None:
            return None

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

    def _summarize_usage(self, usage_records):
        total_input = 0
        total_output = 0
        total_all = 0

        for usage in usage_records:
            if not usage:
                continue
            if usage.get("input_tokens") is not None:
                total_input += usage.get("input_tokens")
            if usage.get("output_tokens") is not None:
                total_output += usage.get("output_tokens")
            if usage.get("total_tokens") is not None:
                total_all += usage.get("total_tokens")

        return {
            "input_tokens": total_input or None,
            "output_tokens": total_output or None,
            "total_tokens": total_all or None,
        }

    def _format_usage_json(self, usage):
        return (
            "{\n"
            f"  \"input_tokens\": {usage.get('input_tokens')},\n"
            f"  \"output_tokens\": {usage.get('output_tokens')},\n"
            f"  \"total_tokens\": {usage.get('total_tokens')}\n"
            "}\n"
        )
