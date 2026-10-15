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

def generate_quote_card(quote_text, hook_title=None, header_title="የዕለቱ የስነ-ልቦና ማስታወሻ", theme_index=None):
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
            logo_y = 75
            img.paste(logo, (logo_x, logo_y), mask)

            draw.ellipse([logo_x - 3, logo_y - 3, logo_x + logo_size + 3, logo_y + logo_size + 3], outline=theme["border"], width=2)
            logo_drawn = True
        except Exception:
            logo_drawn = False

    # 4. Header title & Hook title
    if hook_title:
        header_font = get_ethiopic_font(24)
        draw.text((img_w // 2, 215), header_title, font=header_font, fill=theme["footer_sub"], anchor="mm")
        
        hook_font = get_ethiopic_font(34)
        hook_lines = wrap_text(hook_title.strip(), hook_font, 780, draw)
        hook_y = 255
        for hline in hook_lines[:2]:
            draw.text((img_w // 2, hook_y), hline, font=hook_font, fill=theme["header_color"], anchor="mm")
            hook_y += 42
        line_y = hook_y + 4
        draw.line([(img_w // 2 - 100, line_y), (img_w // 2 + 100, line_y)], fill=theme["accent_line"], width=2)
        center_y = (line_y + (img_h - 170)) // 2
    else:
        header_y = 240 if logo_drawn else 140
        header_font = get_ethiopic_font(34)
        draw.text((img_w // 2, header_y), header_title, font=header_font, fill=theme["header_color"], anchor="mm")
        draw.line([(img_w // 2 - 80, header_y + 30), (img_w // 2 + 80, header_y + 30)], fill=theme["accent_line"], width=2)
        center_y = 525 if logo_drawn else 510

    # 5. Adaptive font sizing & wrapping for the quote
    max_text_width = img_w - 220
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


def generate_tiktok_card(quote_text, hook_title=None, header_title="የዕለቱ የስነ-ልቦና ማስታወሻ", theme_index=None, format="JPEG"):
    """
    Renders an elegant, high-impact 1080x1350 (4:5 aspect ratio) portrait card optimized for TikTok & Social Media.
    Returns bytes of the image (JPEG or PNG).
    """
    clean_text = quote_text.strip()
    if not clean_text.startswith("«") and not clean_text.startswith('"'):
        clean_text = f"«{clean_text}»"

    theme = THEMES[theme_index % len(THEMES)] if theme_index is not None else random.choice(THEMES)

    img_w, img_h = 1080, 1350
    img = Image.new("RGB", (img_w, img_h), color=theme["top_color"])
    draw = ImageDraw.Draw(img)

    # 1. Background gradient (1080x1350)
    t_r, t_g, t_b = theme["top_color"]
    b_r, b_g, b_b = theme["bottom_color"]
    for y in range(img_h):
        ratio = y / img_h
        r = int(t_r * (1 - ratio) + b_r * ratio)
        g = int(t_g * (1 - ratio) + b_g * ratio)
        b = int(t_b * (1 - ratio) + b_b * ratio)
        draw.line([(0, y), (img_w, y)], fill=(r, g, b))

    # 2. Modern double border (margins 44px left/right, 48px top/bottom)
    m_x, m_y = 44, 48
    draw.rectangle([(m_x, m_y), (img_w - m_x, img_h - m_y)], outline=theme["border"], width=2)
    draw.rectangle([(m_x + 6, m_y + 6), (img_w - m_x - 6, img_h - m_y - 6)], outline=theme["inner_border"], width=1)

    # 3. Logo integration (centered around y = 75)
    logo_path = os.path.join(os.path.dirname(__file__), "static", "covers", "baya_logo.jpg")
    logo_drawn = False
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = 115
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            mask = Image.new("L", (logo_size, logo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)

            logo_x = (img_w - logo_size) // 2
            logo_y = 75
            img.paste(logo, (logo_x, logo_y), mask)

            draw.ellipse([logo_x - 3, logo_y - 3, logo_x + logo_size + 3, logo_y + logo_size + 3], outline=theme["border"], width=2)
            logo_drawn = True
        except Exception:
            logo_drawn = False

    # 4. Header title & Hook Title
    if hook_title:
        header_font = get_ethiopic_font(26)
        draw.text((img_w // 2, 225), header_title, font=header_font, fill=theme["footer_sub"], anchor="mm")

        hook_font = get_ethiopic_font(38)
        hook_lines = wrap_text(hook_title.strip(), hook_font, 840, draw)
        hook_y = 270
        for hline in hook_lines[:2]:
            draw.text((img_w // 2, hook_y), hline, font=hook_font, fill=theme["header_color"], anchor="mm")
            hook_y += 48
        line_y = hook_y + 6
        draw.line([(img_w // 2 - 110, line_y), (img_w // 2 + 110, line_y)], fill=theme["accent_line"], width=2)
        center_y = (line_y + 1140) // 2
    else:
        header_y = 245 if logo_drawn else 145
        header_font = get_ethiopic_font(38)
        draw.text((img_w // 2, header_y), header_title, font=header_font, fill=theme["header_color"], anchor="mm")
        draw.line([(img_w // 2 - 100, header_y + 32), (img_w // 2 + 100, header_y + 32)], fill=theme["accent_line"], width=2)
        center_y = 660

    # 5. Adaptive font sizing & wrapping for the quote
    max_text_width = 860
    text_len = len(clean_text)
    if text_len < 80:
        base_size = 50
        line_spacing = 80
    elif text_len < 180:
        base_size = 44
        line_spacing = 72
    elif text_len < 280:
        base_size = 38
        line_spacing = 62
    else:
        base_size = 32
        line_spacing = 54

    quote_font = get_ethiopic_font(base_size)
    lines = wrap_text(clean_text, quote_font, max_text_width, draw)

    # Center the quote block vertically in the middle area
    total_text_h = len(lines) * line_spacing
    start_y = center_y - (total_text_h // 2)

    for i, line in enumerate(lines):
        y = start_y + i * line_spacing
        draw.text((img_w // 2, y), line, font=quote_font, fill=theme["text_color"], anchor="mm")

    # 6. Footer branding (Safe above bottom border, y=1140..1265)
    draw.line([(img_w // 2 - 180, 1140), (img_w // 2 + 180, 1140)], fill="#334155", width=1)
    
    brand_font = get_ethiopic_font(28)
    footer_font = get_ethiopic_font(26)
    cta_font = get_ethiopic_font(30)
    
    draw.text((img_w // 2, 1175), "BAYA BOOKS — የስነ-ልቦና እና የህይወት መመሪያዎች", font=brand_font, fill=theme["footer_sub"], anchor="mm")
    draw.text((img_w // 2, 1215), "የራስዎን ስነ-ልቦና በነጻ በ AI ለመመርመር፦", font=footer_font, fill=theme["text_color"], anchor="mm")
    draw.text((img_w // 2, 1255), "ቴሌግራም ላይ ያግኙን: @bayabooks_bot (Link in Bio)", font=cta_font, fill=theme["footer_link"], anchor="mm")

    # 7. Export to BytesIO
    buf = io.BytesIO()
    if format.upper() == "PNG":
        img.save(buf, format="PNG", optimize=True)
    else:
        img.save(buf, format="JPEG", quality=95, optimize=True)
    buf.seek(0)
    return buf.getvalue()

def generate_winners_card_1_1(secret_word, word_title, word_body, winners, cycle_date=None, tiktok_name="የአዕምሮ ምግቦች", theme_index=None, format="JPEG"):
    """
    Renders an elegant 1080x1080 (1:1 Square) card celebrating today's giveaway:
    - Today's secret word
    - About the word (psychological insight)
    - Today's 5 winners (or open spots)
    - Partner branding (የአዕምሮ ምግቦች × Baya Books)
    """
    theme = THEMES[theme_index % len(THEMES)] if theme_index is not None else random.choice(THEMES)
    img_w, img_h = 1080, 1080
    img = Image.new("RGB", (img_w, img_h), color=theme["top_color"])
    draw = ImageDraw.Draw(img)

    # 1. Gradient Background
    t_r, t_g, t_b = theme["top_color"]
    b_r, b_g, b_b = theme["bottom_color"]
    for y in range(img_h):
        ratio = y / img_h
        r = int(t_r * (1 - ratio) + b_r * ratio)
        g = int(t_g * (1 - ratio) + b_g * ratio)
        b = int(t_b * (1 - ratio) + b_b * ratio)
        draw.line([(0, y), (img_w, y)], fill=(r, g, b))

    # 2. Modern Double Border
    margin = 36
    draw.rectangle([(margin, margin), (img_w - margin, img_h - margin)], outline=theme["border"], width=2)
    draw.rectangle([(margin + 6, margin + 6), (img_w - margin - 6, img_h - margin - 6)], outline=theme["inner_border"], width=1)

    # 3. Logo integration (Top Left)
    logo_path = os.path.join(os.path.dirname(__file__), "static", "covers", "baya_logo.jpg")
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_size = 72
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (logo_size, logo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)
            img.paste(logo, (58, 52), mask)
            draw.ellipse([55, 49, 58 + logo_size + 3, 52 + logo_size + 3], outline=theme["border"], width=2)
        except Exception:
            pass

    # 4. Header Banner
    header_font = get_ethiopic_font(28)
    sub_header_font = get_ethiopic_font(22)
    
    draw.text((img_w // 2, 68), f"{tiktok_name}  ×  BAYA BOOKS", font=header_font, fill=theme["header_color"], anchor="mm")
    draw.text((img_w // 2, 104), "የዕለቱ የነፃ መጽሐፍ ስጦታ አሸናፊዎች", font=sub_header_font, fill=theme["footer_sub"], anchor="mm")
    draw.line([(140, 132), (img_w - 140, 132)], fill=theme["accent_line"], width=2)

    # 5. Secret Word Card Box (y = 150 .. 395)
    box_x1, box_y1 = 60, 150
    box_x2, box_y2 = img_w - 60, 395
    card_bg = (15, 23, 42)
    draw.rectangle([(box_x1, box_y1), (box_x2, box_y2)], fill=card_bg, outline=theme["border"], width=1)
    
    # Badge: የዕለቱ ሚስጥራዊ ቃል
    badge_font = get_ethiopic_font(20)
    badge_text = "የዕለቱ ሚስጥራዊ ቃል (Secret Word)"
    draw.rectangle([(img_w // 2 - 170, box_y1 - 15), (img_w // 2 + 170, box_y1 + 17)], fill=theme["accent_line"])
    draw.text((img_w // 2, box_y1 + 1), badge_text, font=badge_font, fill="#ffffff", anchor="mm")

    # Big Word
    word_font = get_ethiopic_font(52)
    clean_word_raw = str(secret_word or "").strip().strip("«»\"' ").strip()
    clean_word = f"«{clean_word_raw}»"
    draw.text((img_w // 2, box_y1 + 68), clean_word, font=word_font, fill=theme["header_color"], anchor="mm")

    # About the word (Pure psychological insight explaining the word, NO repetitive 'አዎ አንተ...' title)
    body_font = get_ethiopic_font(22)
    insight_text = (word_body or "").strip()
    if not insight_text:
        insight_text = (
            f"«{clean_word_raw}» የሚለው ቃል በአዕምሯችን ውስጥ ያለውን ድብቅ አቅም እና የማይናወጥ ጥንካሬ የሚቀሰቅስ ታላቅ ኃይል አለው። "
            f"አዕምሮአችንን በምንመግበው አዎንታዊ አስተሳሰብ ልክ ህይወታችን ይለወጣል።"
        )
        
    wrapped_lines = wrap_text(insight_text, body_font, 920, draw)
    text_y = box_y1 + 122
    for wline in wrapped_lines[:3]:
        draw.text((img_w // 2, text_y), wline, font=body_font, fill=theme["text_color"], anchor="mm")
        text_y += 34

    # 6. Winners Section Header (y = 415)
    win_header_font = get_ethiopic_font(28)
    draw.text((img_w // 2, 428), "—  የዛሬ 5ቱ ፈጣን አሸናፊዎች (Top 5 Winners)  —", font=win_header_font, fill=theme["header_color"], anchor="mm")
    draw.line([(img_w // 2 - 200, 452), (img_w // 2 + 200, 452)], fill=theme["accent_line"], width=2)

    # 7. Winners List Rows (y = 470 .. 885)
    row_h = 75
    start_row_y = 470
    win_by_rank = {w.get("rank"): w for w in (winners or [])}
    
    row_font_rank = get_ethiopic_font(24)
    row_font_name = get_ethiopic_font(25)
    row_font_book = get_ethiopic_font(23)
    
    for r in range(1, 6):
        ry = start_row_y + (r - 1) * row_h
        r_bg = (20, 27, 48) if r % 2 == 1 else (16, 22, 40)
        draw.rectangle([(70, ry), (img_w - 70, ry + 62)], fill=r_bg, outline=theme["inner_border"], width=1)
        
        # Rank pill on left
        pill_color = theme["accent_line"] if r == 1 else theme["inner_border"]
        draw.rectangle([(80, ry + 12), (180, ry + 50)], fill=pill_color, outline=theme["border"] if r == 1 else None)
        draw.text((130, ry + 31), f"{r}ኛ", font=row_font_rank, fill="#ffffff" if r == 1 else theme["header_color"], anchor="mm")
        
        w_entry = win_by_rank.get(r)
        if w_entry:
            uname = f"@{w_entry.get('username')}" if w_entry.get('username') else (w_entry.get('first_name') or f"User {w_entry.get('user_id')}")
            btitle = w_entry.get('book_title') or w_entry.get('book_chosen') or "የነፃ መጽሐፍ"
            
            draw.text((205, ry + 31), uname, font=row_font_name, fill="#ffffff", anchor="lm")
            book_str = f"«{btitle}»"
            draw.text((img_w - 95, ry + 31), book_str, font=row_font_book, fill=theme["border"], anchor="rm")
        else:
            open_msg = "ክፍት ቦታ — አሁኑኑ በቦቱ ተሳትፈው ያሸንፉ!"
            draw.text((205, ry + 31), open_msg, font=row_font_name, fill="#94a3b8", anchor="lm")

    # 8. Footer (y = 905 .. 1040)
    draw.line([(100, 915), (img_w - 100, 915)], fill="#334155", width=1)
    
    f_sub = get_ethiopic_font(24)
    f_cta = get_ethiopic_font(26)
    f_brand = get_ethiopic_font(22)
    
    draw.text((img_w // 2, 945), f"የነገውን ሚስጥራዊ ቃል በቲክቶክ @yeaemromgboch ይከታተሉ!", font=f_sub, fill=theme["footer_sub"], anchor="mm")
    draw.text((img_w // 2, 982), "በየቀኑ በነፃ ለመሸለም፦ ቴሌግራም ላይ @bayabooks_bot (Link in Bio)", font=f_cta, fill=theme["footer_link"], anchor="mm")
    draw.text((img_w // 2, 1018), "BAYA BOOKS — በኢትዮጵያ የመጀመሪያው የኤአይ የስነ-ልቦና ማማከሪያ", font=f_brand, fill="#64748b", anchor="mm")

    buf = io.BytesIO()
    if format.upper() == "PNG":
        img.save(buf, format="PNG", optimize=True)
    else:
        img.save(buf, format="JPEG", quality=95, optimize=True)
    buf.seek(0)
    return buf.getvalue()


