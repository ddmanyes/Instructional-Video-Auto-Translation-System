import sys
from TTS.api import TTS
import traceback

try:
    print("Trying to load XTTS-v2 model...")
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    print("Success loading model!")
except Exception as e:
    print("\n--- ERROR DETAILS ---")
    traceback.print_exc()
    print("----------------------")
