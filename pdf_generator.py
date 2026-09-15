import os
import re
import logging
import requests
from fpdf import FPDF

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONT_FILE = os.path.join(FONT_DIR, "AbyssinicaSIL-Regular.ttf")
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansEthiopic/NotoSansEthiopic-Regular.ttf"
FONT_FILE_NOTO = os.path.join(FONT_DIR, "NotoSansEthiopic-Regular.ttf")

def ensure_font():
    """Download Ethiopian font if not present."""
    os.makedirs(FONT_DIR, exist_ok=True)
    if os.path.exists(FONT_FILE_NOTO):
        return FONT_FILE_NOTO
    if os.path.exists(FONT_FILE):
        return FONT_FILE
    # Download Noto Sans Ethiopic
    try:
        logging.info("Downloading Ethiopian font...")
        resp = requests.get(FONT_URL, timeout=30)
        if resp.status_code == 200:
            with open(FONT_FILE_NOTO, "wb") as f:
                f.write(resp.content)
            logging.info("Font downloaded successfully.")
            return FONT_FILE_NOTO
    except Exception as e:
        logging.error(f"Font download failed: {e}")
    return None


class EthiopicPDF(FPDF):
    """Custom PDF class with Ethiopic font support."""

    def __init__(self, font_path):
        super().__init__()
        self.font_path = font_path
        self.set_auto_page_break(auto=True, margin=20)
        self.add_page()
        # Register Ethiopian font
        self.add_font("Ethiopic", "", font_path, uni=True)
        self.add_font("Ethiopic", "B", font_path, uni=True)
        self.add_font("Ethiopic", "I", font_path, uni=True)

    def header(self):
        self.set_font("Ethiopic", "B", 10)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "Baya Books | Personalized Transformation Protocol", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Ethiopic", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def markdown_to_pdf(markdown_text, output_path, title="Protocol"):
    """Convert markdown text to a beautifully formatted PDF with Ethiopic fonts."""
    font_path = ensure_font()
    if not font_path:
        logging.error("No Ethiopian font available!")
        return False

    pdf = EthiopicPDF(font_path)
    pdf.alias_nb_pages()

    lines = markdown_text.split("\n")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        # ─── Horizontal rule ───
        if stripped in ("---", "***", "━━━"):
            pdf.set_draw_color(180, 180, 180)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            continue

        # ─── Headings ───
        if stripped.startswith("# ") and not stripped.startswith("## "):
            text = stripped[2:].strip("*# ")
            pdf.set_font("Ethiopic", "B", 18)
            pdf.set_text_color(30, 60, 120)
            pdf.multi_cell(0, 10, text)
            pdf.ln(3)
            continue

        if stripped.startswith("## "):
            text = stripped[3:].strip("*# ")
            pdf.set_font("Ethiopic", "B", 14)
            pdf.set_text_color(40, 80, 140)
            pdf.multi_cell(0, 9, text)
            pdf.ln(2)
            continue

        if stripped.startswith("### "):
            text = stripped[4:].strip("*# ")
            pdf.set_font("Ethiopic", "B", 12)
            pdf.set_text_color(50, 100, 150)
            pdf.multi_cell(0, 8, text)
            pdf.ln(2)
            continue

        # ─── Blockquotes ───
        if stripped.startswith("> "):
            text = stripped[2:]
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            pdf.set_font("Ethiopic", "I", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_x(20)
            pdf.multi_cell(170, 7, text)
            pdf.ln(2)
            continue

        # ─── Bullet points ───
        if stripped.startswith(("- ", "* ", "•  ")):
            bullet_text = re.sub(r'^[-*•]\s+', '', stripped)
            # Handle bold within bullets
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
            clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)
            pdf.set_font("Ethiopic", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(18)
            pdf.cell(5, 7, "•")
            pdf.multi_cell(167, 7, clean_text)
            pdf.ln(1)
            continue

        # ─── Bold lines ───
        if stripped.startswith("**") and stripped.endswith("**"):
            text = stripped.strip("*")
            pdf.set_font("Ethiopic", "B", 11)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 7, text)
            pdf.ln(1)
            continue

        # ─── Italic lines ───
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            text = stripped.strip("*")
            pdf.set_font("Ethiopic", "I", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 7, text)
            pdf.ln(1)
            continue

        # ─── Regular text ───
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
        clean_text = re.sub(r'\*(.*?)\*', r'\1', clean_text)
        pdf.set_font("Ethiopic", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 7, clean_text)
        pdf.ln(1)

    try:
        pdf.output(output_path)
        return True
    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        return False
