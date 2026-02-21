import os
import wave

base_dir = r"h:\生理2\output\audio"
total_duration = 0.0
count = 0

for i in range(1, 2980):
    filename = f"Respiratory system I_seg_{i:04d}.wav"
    filepath = os.path.join(base_dir, filename)
    
    if os.path.exists(filepath):
        try:
            with wave.open(filepath, 'rb') as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                total_duration += duration
                count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    else:
        # print(f"File not found: {filename}")
        pass

print(f"Total duration: {total_duration} seconds")
print(f"Total duration: {total_duration / 60:.2f} minutes")
print(f"Total duration: {total_duration / 3600:.2f} hours")
print(f"Files processed: {count}")
