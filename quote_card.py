# quote_card.py — High-impact visual quote card generator for Facebook & Social Media
import io
import os
import random
from PIL import Image, ImageDraw, ImageFont

# 4 Rotating Aesthetic Color Themes
THEMES = [
    {
        "name": "ocean_midnight",
        "top_color": (11, 19, 41),     # #0b1329
        "bottom_color": (30, 27, 75),  # #1e1b4b
        "border": "#38bdf8",           # Sky blue
        "inner_border": "#1e293b",
        "header_color": "#38bdf8",
        "accent_line": "#6366f1",      # Indigo
        "text_color": "#f8fafc",
        "footer_sub": "#94a3b8",
        "footer_link": "#38bdf8"
    },
    {
        "name": "golden_charcoal",
        "top_color": (15, 23, 42),     # #0f172a
        "bottom_color": (28, 25, 23),  # #1c1917
        "border": "#fbbf24",           # Warm Gold
        "inner_border": "#292524",
        "header_color": "#fbbf24",
        "accent_line": "#f59e0b",      # Amber
        "text_color": "#fafaf9",
        "footer_sub": "#a8a29e",
        "footer_link": "#fbbf24"
    },
    {
        "name": "emerald_forest",
        "top_color": (6, 26, 20),      # #061a14
        "bottom_color": (6, 44, 34),   # #062c22
        "border": "#34d399",           # Emerald
        "inner_border": "#064e3b",
        "header_color": "#34d399",
        "accent_line": "#10b981",      # Mint
        "text_color": "#f0fdf4",
        "footer_sub": "#9ca3af",
        "footer_link": "#34d399"
    },
    {
        "name": "ruby_plum",
        "top_color": (31, 12, 25),     # #1f0c19
        "bottom_color": (47, 14, 38),  # #2f0e26
        "border": "#f472b6",           # Rose
        "inner_border": "#4c0519",
        "header_color": "#f472b6",
        "accent_line": "#ec4899",      # Pink
        "text_color": "#fff1f2",
        "footer_sub": "#9ca3af",
        "footer_link": "#f472b6"
    }
]

def get_ethiopic_font(size):
    """Locate and load an Ethiopic-capable TTF font."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "static", "fonts", "AbyssinicaSIL-Regular.ttf"),
        "static/fonts/AbyssinicaSIL-Regular.ttf",
        "C:\\Windows\\Fonts\\AbyssinicaSIL-Regular.ttf",
        "C:\\Windows\\Fonts\\Nyala.ttf",
        "C:\\Windows\\Fonts\\ARIALUNI.TTF",
        "/usr/share/fonts/truetype/abyssinica/AbyssinicaSIL-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    try:
        return ImageFont.load_default()
    except Exception:
        return None

def wrap_text(text, font, max_width, draw):
    """Word-wrap text to fit within max_width."""
    words = text.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        line_str = " ".join(curr)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        if bbox[2] - bbox[0] > max_width:
            curr.pop()
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))
    return lines

def generate_quote_card(quote_text, header_title="የዕለቱ የስነ-ልቦና ማስታወሻ", theme_index=None):
    """
    Renders an elegant, high-resolution 1080x1080 branded social card.
    Returns bytes of the PNG image ready for multipart upload.
    """
    clean_text = quote_text.strip()
    # Format quote with Amharic brackets if not already present
    if not clean_text.startswith("«") and not clean_text.startswith('"'):
        clean_text = f"«{clean_text}»"

    theme = THEMES[theme_index % len(THEMES)] if theme_index is not None else random.choice(THEMES)

    img_w, img_h = 1080, 1080
    img = Image.new("RGB", (img_w, img_h), color=theme["top_color"])
    draw = ImageDraw.Draw(img)

    # 1. Background gradient
    t_r, t_g, t_b = theme["top_color"]
    b_r, b_g, b_b = theme["bottom_color"]
    for y in range(img_h):
        ratio = y / img_h
        r = int(t_r * (1 - ratio) + b_r * ratio)
        g = int(t_g * (1 - ratio) + b_g * ratio)
        b = int(t_b * (1 - ratio) + b_b * ratio)
        draw.line([(0, y), (img_w, y)], fill=(r, g, b))

    # 2. Modern double border
    margin = 44
    draw.rectangle([(margin, margin), (img_w - margin, img_h - margin)], outline=theme["border"], width=2)
    draw.rectangle([(margin + 6, margin + 6), (img_w - margin - 6, img_h - margin - 6)], outline=theme["inner_border"], width=1)

    # 3. Logo integration
    logo_path = os.path.join(os.path.dirname(__file__), "static", "covers", "baya_logo.jpg")
    logo_drawn = False
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = 110
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            mask = Image.new("L", (logo_size, logo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)

            logo_x = (img_w - logo_size) // 2
            logo_y = 85
            img.paste(logo, (logo_x, logo_y), mask)

            draw.ellipse([logo_x - 3, logo_y - 3, logo_x + logo_size + 3, logo_y + logo_size + 3], outline=theme["border"], width=2)
            logo_drawn = True
        except Exception:
            logo_drawn = False

    header_y = 240 if logo_drawn else 140

    # 4. Header title
    header_font = get_ethiopic_font(34)
    draw.text((img_w // 2, header_y), header_title, font=header_font, fill=theme["header_color"], anchor="mm")
    draw.line([(img_w // 2 - 80, header_y + 30), (img_w // 2 + 80, header_y + 30)], fill=theme["accent_line"], width=2)

    # 5. Adaptive font sizing & wrapping for the quote
    max_text_width = img_w - 220
    # Determine best font size based on text length
    text_len = len(clean_text)
    if text_len < 80:
        base_size = 46
        line_spacing = 74
    elif text_len < 180:
        base_size = 42
        line_spacing = 68
    elif text_len < 280:
        base_size = 36
        line_spacing = 60
    else:
        base_size = 32
        line_spacing = 54

    quote_font = get_ethiopic_font(base_size)
    lines = wrap_text(clean_text, quote_font, max_text_width, draw)

    # Center the quote block vertically in the middle area
    total_text_h = len(lines) * line_spacing
    center_y = 525 if logo_drawn else 510
    start_y = center_y - (total_text_h // 2)

    for i, line in enumerate(lines):
        y = start_y + i * line_spacing
        draw.text((img_w // 2, y), line, font=quote_font, fill=theme["text_color"], anchor="mm")

    # 6. Footer branding
    draw.line([(img_w // 2 - 160, img_h - 170), (img_w // 2 + 160, img_h - 170)], fill="#334155", width=1)
    
    brand_font = get_ethiopic_font(30)
    footer_font = get_ethiopic_font(28)
    
    draw.text((img_w // 2, img_h - 130), "BAYA BOOKS — የስነ-ልቦና እና የህይወት መመሪያዎች", font=brand_font, fill=theme["footer_sub"], anchor="mm")
    draw.text((img_w // 2, img_h - 85), "ቴሌግራም ላይ ያግኙን: @bayabooks_bot", font=footer_font, fill=theme["footer_link"], anchor="mm")

    # 7. Export to BytesIO
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf.getvalue()
