import traceback
print("Importing torch...")
import torch
print("Importing transformers...")
try:
    import transformers
    from transformers import GPT2Model
    print("Transformers OK")
except:
    traceback.print_exc()

print("Trying XTTS model loading...")
from TTS.api import TTS
try:
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())
    print("DONE SUCCESS")
except:
    traceback.print_exc()
