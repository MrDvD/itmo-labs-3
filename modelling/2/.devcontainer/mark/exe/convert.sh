#!/bin/bash
set -euo pipefail

CHM="${1:-WinMark.chm}"
WORK="extracted_html"
OUT="WinMark.pdf"

# ---------- 1. Extract ----------
echo ">>> Extracting $CHM"
rm -rf "$WORK"
7z x "$CHM" -o"$WORK" >/dev/null

# ---------- 2. Convert & Decode Entities to Clean UTF-8 ----------
echo ">>> Converting files to UTF-8 and decoding HTML entities"
python3 -c '
import os, glob, re, html
work_dir = "extracted_html"

for ext in ["*.htm", "*.html", "*.hhc", "*.hhk"]:
    for filepath in glob.glob(os.path.join(work_dir, ext)):
        try:
            with open(filepath, "r", encoding="cp1251", errors="ignore") as f:
                content = f.read()
        except Exception:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        def replacer(match):
            entity = match.group(0)
            unescaped = html.unescape(entity)
            if len(unescaped) == 1:
                try:
                    return bytes([ord(unescaped)]).decode("cp1251")
                except Exception:
                    return entity
            return entity

        content = re.sub(r"&[a-zA-Z]+;", replacer, content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
print("    Decoding complete.")
'

# ---------- 3. Merge into a Single HTML File ----------
echo ">>> Merging HTML files into a single document"
cd "$WORK"
python3 -c '
import os, glob

# Logical reading order based on the help structure
order = ["main.htm", "about.htm", "menus.htm", "windows.htm", "working.htm", "glossary.htm"]
all_files = [f for f in order if os.path.exists(f)]
for f in glob.glob("*.htm") + glob.glob("*.html"):
    if f not in all_files:
        all_files.append(f)

combined_content = """<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\">
<title>WinMark Help</title>
<style>
    body { font-family: Arial, sans-serif; margin: 40px; color: #333; line-height: 1.6; }
    h1, h2, h3 { color: #111; page-break-before: always; }
    .chapter { page-break-after: always; }
    img { max-width: 100%; height: auto; }
</style>
</head>
<body>
"""

for fname in all_files:
    with open(fname, "r", encoding="utf-8", errors="ignore") as f:
        html_data = f.read()
        # Extract body content if present to avoid nested html tags
        if "<body" in html_data.lower():
            body_start = html_data.lower().find("<body")
            body_content_start = html_data.find(">", body_start) + 1
            body_end = html_data.lower().rfind("</body>")
            if body_end != -1:
                html_data = html_data[body_content_start:body_end]
        
        combined_content += f"<div class=\"chapter\">\n{html_data}\n</div>\n"

combined_content += "</body></html>"

with open("combined.html", "w", encoding="utf-8") as f:
    f.write(combined_content)
print("    Merged into combined.html")
'

# ---------- 4. Convert to PDF ----------
echo ">>> Converting to PDF"
if ! command -v wkhtmltopdf &> /dev/null; then
    echo "Installing wkhtmltopdf..."
    apt-get update && apt-get install -y wkhtmltopdf
fi

wkhtmltopdf --enable-local-file-access combined.html "$OUT"

mv "$OUT" ..
cd ..

echo ">>> Done: $OUT"