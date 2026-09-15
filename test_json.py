import requests
import json
import config
import urllib3
urllib3.disable_warnings()

prompt = """You are a book recommendation expert for Ethiopian readers.
Category: Habits & Discipline

Recommend exactly 3 transformative books for this category. For each book, write exactly 1 sentence in Amharic explaining how it changes the reader's life.

Respond in this exact JSON format only, no other text:
[
  {"title": "Book Title in English", "description": "One sentence in Amharic"},
  {"title": "Book Title in English", "description": "One sentence in Amharic"},
  {"title": "Book Title in English", "description": "One sentence in Amharic"}
]"""

url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={config.GEMINI_API_KEY}'
payload = {
    'contents': [{'parts': [{'text': prompt}]}]
}
response = requests.post(url, json=payload, verify=False)
try:
    text = response.json()['candidates'][0]['content']['parts'][0]['text']
    with open("gemini_output.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Wrote output to gemini_output.txt")
    
    # Try parsing logic from ai_engine.py
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()
    
    parsed = json.loads(text)
    print("\nPARSED:")
    print(parsed)
except Exception as e:
    print('Error:', e)
    print(response.text)
