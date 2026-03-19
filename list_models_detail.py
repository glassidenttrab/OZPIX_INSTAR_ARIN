import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=key)

try:
    models = genai.list_models()
    for m in models:
        print(f"Name: {m.name}, DisplayName: {m.display_name}, Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"ERROR: {e}")
