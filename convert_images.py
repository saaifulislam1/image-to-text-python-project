import os
import json
from PIL import Image
import pytesseract

# Input/output paths
INPUT_FOLDER = "screenshots"
OUTPUT_FILE = "output.json"

# OCR languages (English + Bengali + Japanese)
LANGS = "eng+ben+jpn"

results = {}

for filename in sorted(os.listdir(INPUT_FOLDER)):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        filepath = os.path.join(INPUT_FOLDER, filename)
        print(f"Processing {filename}...")

        # OCR
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang=LANGS)

        # Extract lines (keywords)
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Save under filename
        results[filename] = lines

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done! Results saved in {OUTPUT_FILE}")
