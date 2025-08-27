import os
import json
import re
from PIL import Image
import pytesseract

# Input/output paths
INPUT_FOLDER = "screenshots"
OUTPUT_FILE = "output.json"

# OCR languages (English + Bengali + Japanese)
LANGS = "jpn"

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


def clean_ocr_line(line: str) -> str:
    """
    Cleans OCR text by removing UI artifacts, noise, and junk symbols.
    Specially ignores Google search icon artifacts (O, 0, Q, G, © etc).
    """
    line = line.strip()
    if not line:
        return ""

    # --- NEW: Drop if line is just the search icon OCR garbage ---
    if line in {"O", "0", "Q", "G", "©", "®", "●", "○"}:
        return ""

    # 1. Drop pure garbage (symbols/numbers only)
    if re.fullmatch(r'[\W\d_]+', line):
        return ""

    # 2. Remove leading artifacts like "ও.", "O.", "0.", "•"
    line = re.sub(r'^(ও\.|[O0Q•●○□◇|]+\s*)', '', line)

    # 3. Remove trailing garbage like "G", "O", "@"
    line = re.sub(r'(\s*[GO0@]+)$', '', line)

    # 4. Normalize multiple spaces
    line = re.sub(r'\s+', ' ', line).strip()

    # 5. Drop if still too short or meaningless
    if len(line) < 3:
        return ""

    return line


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
            clean_line = fix_japanese_spacing(line.strip())
            clean_line = clean_ocr_line(clean_line)
            if not clean_line:
                continue
            if clean_line not in lines:  # avoid duplicates
                lines.append(clean_line)

        # Save under filename
        results[filename] = lines

# Save JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done! Results saved in {OUTPUT_FILE}")
