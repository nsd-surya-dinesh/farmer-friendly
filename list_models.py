"""
list_models.py — quick diagnostic to see which Gemini models your API
key actually has access to. Run this if you still get 404 errors after
updating the model name in server.py.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("No API key found in .env")
    exit(1)

genai.configure(api_key=API_KEY)

print("Models available to your API key that support generateContent:\n")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"  {m.name}")
