# UV Virtual Environment Guide

This project utilizes `uv` to manage the Python environment, ensuring lightning-fast deployment across different machines.

## 📦 Environment Structure

```
Physiology_Translator/
├── .venv/              # Virtual environment created by uv
├── .python-version     # Python version (3.11)
├── pyproject.toml      # Project configuration & dependencies
├── uv.lock            # uv lockfile (ensures deterministic environment)
└── LICENSE             # MIT License
```

## 🚀 Usage on Local Machine

### 1. Activating the Environment

```powershell
# PowerShell
.\.venv\Scripts\activate

# Or use uv run (highly recommended)
uv run python main.py
```

### 2. Running the Program

```powershell
# Batch process all videos
uv run python main.py --batch

# Process a single video with XTTS
uv run python main.py --video "video/example.mp4" --ref-audio "teacher.wav" --xtts
```

## 📤 Deploying to Another Machine

### Method A: Full Transfer (Recommended)

Copy the entire project folder to the new machine, including the `.venv` directory. This is the fastest way as it includes all pre-compiled assets.

### Method B: Reconstruction via uv (Standard)

If the `.venv` folder is too large for transfer:

```powershell
# On the new machine
cd Physiology_Translator

# Install uv if not present
pip install uv

# Synchronize the environment (installs and locks versions automatically)
uv sync
```

## 🔧 Useful uv Commands

### Environment Management
-   `uv sync`: Synchronizes the environment with `pyproject.toml`.
-   `uv run <cmd>`: Runs a command within the virtual environment context.
-   `uv pip list`: Lists installed packages.

### Package Installation
-   `uv pip install <package>`: Installs a new package (not added to pyproject.toml permanently unless edited).

## 📋 Key Dependency Matrix

| Package | Purpose |
| :--- | :--- |
| **faster-whisper** | Speech-to-Text (ASR) |
| **deep-translator** | Google Translate (Free) |
| **TTS (Coqui XTTS-v2)** | Voice Cloning |
| **torch / torchaudio** | NVIDIA CUDA Accelerated Engine (RTX 4090 support) |
| **moviepy** | Video & Audio merging |

## ⚡ Why UV?

Compared to traditional `pip + venv`:
-   **Installation Speed**: 10-100x faster.
-   **Reproducibility**: `uv.lock` ensures every machine has the EXACT same library versions.
-   **Unified Workflow**: Handles Python versioning, virtual environments, and dependencies in one tool.

---
**Updated**: February 22, 2026
