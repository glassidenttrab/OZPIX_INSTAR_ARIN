import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing models...")
try:
    for model in client.models.list():
        if "imagen" in model.name.lower():
            print(f"- {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")
