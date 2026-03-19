import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=key)

model = genai.GenerativeModel('gemini-1.5-flash')
try:
    response = model.generate_content("Hi, tell me one word: Success")
    print(f"RESULT: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
