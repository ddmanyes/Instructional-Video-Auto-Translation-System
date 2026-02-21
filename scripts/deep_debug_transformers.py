import traceback
try:
    print("Importing GPT2Model directly...")
    from transformers.models.gpt2.modeling_gpt2 import GPT2Model
    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"OTHER ERROR: {e}")
    traceback.print_exc()
