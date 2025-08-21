import json
import openai
import os
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()



openai.api_key = os.getenv("OPENAI_API_KEY")

INPUT_FILE = "output.json"
OUTPUT_FILE = "normalized_output.json"

# Load OCR JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    ocr_data = json.load(f)

normalized_data = {}

def normalize_keywords(keywords):
    prompt = (
        "You are an expert text cleaner for OCR-extracted data. The input is a list of text lines from images via OCR. "
        "These lines may contain duplicates, random characters, misrecognized symbols, or irrelevant content.\n\n"
        "Your task:\n"
        "1. Remove all lines that are clearly garbage, nonsense, or unreadable.\n"
        "2. Remove duplicates.\n"
        "3. Remove any random OCR artifacts (e.g., repeated characters, stray symbols).\n"
        "4. Keep meaningful words, phrases, or proper names intact.\n"
        "5. Strip leading and trailing whitespace from each line.\n"
        "6. Return the cleaned list in the same language as the original (do not translate).\n"
        "7. Return output ONLY as a JSON array of strings, with no extra text, explanation, or commentary.\n\n"
        "You must be strict: discard anything that looks like OCR artifacts, repeated characters, "
        f"Input: {json.dumps(keywords, ensure_ascii=False)}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        output_text = response.choices[0].message.content.strip()
        return json.loads(output_text)
    except Exception as e:
        print("Error normalizing keywords:", e)
        return keywords

# Normalize each screenshot
for filename, keywords in ocr_data.items():
    print(f"Normalizing {filename}...")
    normalized_data[filename] = normalize_keywords(keywords)
    time.sleep(1)  # small delay to avoid rate limits

# Save normalized JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(normalized_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Normalized data saved to {OUTPUT_FILE}")
