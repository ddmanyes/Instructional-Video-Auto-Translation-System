import os

base_dir = r"h:\生理2\output\audio"
missing = []

for i in range(1, 2980):
    filename = f"Respiratory system I_seg_{i:04d}.wav"
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        missing.append(filename)

print(f"Missing files: {missing}")
