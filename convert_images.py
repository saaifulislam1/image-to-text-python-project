import os
import json
import re
from PIL import Image
import pytesseract

# Input/output paths
INPUT_FOLDER = "screenshots"
OUTPUT_FILE = "output.json"

# OCR languages (English + Bengali + Japanese)
LANGS = "eng+ben+jpn"

# Better OCR settings
CUSTOM_CONFIG = r'--oem 3 --psm 6'

def fix_japanese_spacing(text: str) -> str:
    """
    Removes unwanted spaces between Japanese characters (Kana + Kanji).
    Example: ブラ ンド クラ ウド -> ブランドクラウド
    """
    return re.sub(
        r'(?<=[\u3040-\u30ff\u4e00-\u9fff])\s+(?=[\u3040-\u30ff\u4e00-\u9fff])',
        '',
        text
    )

def remove_search_icon_noise(line: str) -> str:
    """
    Cleans up OCR artifacts where search icons are misread as Q, O, 0, @.
    - Removes them if they appear alone.
    - Strips them if they appear at the start or end of a line.
    """
    line = line.strip()
    # Drop if it's just a single suspicious character
    if re.fullmatch(r'[QO0@]', line):
        return ""
    # Remove leading/trailing Q, O, 0, @
    return re.sub(r'^[QO0@]+\s*|\s*[QO0@]+$', '', line).strip()

results = {}

for filename in sorted(os.listdir(INPUT_FOLDER)):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        filepath = os.path.join(INPUT_FOLDER, filename)
        print(f"Processing {filename}...")

        # OCR
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang=LANGS, config=CUSTOM_CONFIG)

        # Extract + clean lines
        lines = []
        for line in text.split("\n"):
            if not line.strip():
                continue
            clean_line = fix_japanese_spacing(line.strip())
            clean_line = remove_search_icon_noise(clean_line)
            if clean_line and clean_line not in lines:  # remove empties + duplicates
                lines.append(clean_line)

        # Save under filename
        results[filename] = lines

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done! Results saved in {OUTPUT_FILE}")
