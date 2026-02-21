import os
import re
import wave
import subprocess
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def parse_srt(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(
        r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)',
        re.DOTALL
    )
    subtitles = []
    for match in pattern.finditer(content):
        # time to seconds
        h, m, s = match.group(2).replace(',', '.').split(':')
        start = int(h)*3600 + int(m)*60 + float(s)
        
        h, m, s = match.group(3).replace(',', '.').split(':')
        end = int(h)*3600 + int(m)*60 + float(s)
        
        subtitles.append({
            'index': int(match.group(1)),
            'start': start,
            'end': end
        })
    return subtitles

def get_actual_duration(filepath):
    if not os.path.exists(filepath):
        return 0.0
    try:
        with wave.open(filepath, 'rb') as f:
            return f.getnframes() / float(f.getframerate())
    except:
        return 0.0

def process_file(item, base_dir, output_dir, video_name):
    idx = item['index']
    target_d = item['target']
    
    in_wav = os.path.join(base_dir, f"{video_name}_seg_{idx:04d}.wav")
    out_wav = os.path.join(output_dir, f"{video_name}_aligned_{idx:04d}.wav")
    
    actual_d = get_actual_duration(in_wav)
    
    if actual_d == 0:
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc=0:d={target_d}",
            "-ac", "1", "-ar", "24000", out_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_wav
        
    speed = 1.0
    if actual_d > target_d:
        speed = actual_d / target_d
        if speed > 10.0: speed = 10.0
        
    speed_filter = f"atempo={speed}" if speed > 1.0 else "anull"
    
    cmd = [
        "ffmpeg", "-y", "-i", in_wav,
        "-filter_complex", f"[0:a]{speed_filter},apad[a]",
        "-map", "[a]",
        "-t", str(target_d),
        "-ac", "1", "-ar", "24000", out_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_wav


def align_audio(srt_path, base_dir, output_dir, video_name, final_audio_path):
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Reading SRT from {srt_path} ...")
    subtitles = parse_srt(srt_path)
    print(f"Parse complete, {len(subtitles)} items")

    timeline = []
    for i in range(len(subtitles)):
        curr = subtitles[i]
        if i < len(subtitles) - 1:
            target_dur = subtitles[i+1]['start'] - curr['start']
        else:
            target_dur = curr['end'] - curr['start']
        curr['target'] = target_dur
        timeline.append(curr)

    print("Starting audio processing...")
    aligned_files = []
    
    if not timeline:
        print("No subtitles found.")
        return None

    first_start = timeline[0]['start']
    if first_start > 0:
        initial_wav = os.path.join(output_dir, "initial_silence.wav")
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc=0:d={first_start}",
            "-ac", "1", "-ar", "24000", initial_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        aligned_files.append(initial_wav)

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = []
        for item in timeline:
            futures.append(executor.submit(process_file, item, base_dir, output_dir, video_name))
        results = [f.result() for f in futures]

    aligned_files.extend(results)

    concat_file = os.path.join(output_dir, "concat_list.txt")
    with open(concat_file, "w", encoding='utf-8') as f:
        for file in aligned_files:
            path_escaped = str(file).replace('\\', '/')
            f.write(f"file '{path_escaped}'\n")

    print(f"Concatenating all segments into {final_audio_path} ...")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", final_audio_path
    ]
    subprocess.run(concat_cmd)
    print("Merge complete!")

    final_d = get_actual_duration(final_audio_path)
    print(f"Final audio duration: {final_d / 60:.2f} minutes")
    return final_audio_path


def main():
    parser = argparse.ArgumentParser(description="語速壓縮與影片精準對齊工具")
    parser.add_argument("--srt", "-s", type=str, required=True, help="翻譯好的 SRT 檔案路徑")
    parser.add_argument("--video-name", "-n", type=str, required=True, help="影片前綴名稱")
    parser.add_argument("--audio-dir", "-a", type=str, default=r"output\audio", help="原始 TTS 音訊存放處")
    parser.add_argument("--output-dir", "-o", type=str, default=r"output\audio_aligned", help="對齊後的暫存輸出目錄")
    parser.add_argument("--final-output", "-f", type=str, default=r"output\final_synced_audio.wav", help="最終合併大檔")
    
    args = parser.parse_args()
    
    align_audio(args.srt, args.audio_dir, args.output_dir, args.video_name, args.final_output)

if __name__ == "__main__":
    main()
