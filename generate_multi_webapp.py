import os, json

books_meta = {
    "narcissist": {
        "key": "narcissist",
        "title": "የናርስሲስቶች ወጥመድ",
        "subtitle": "ከመርዛማ ግንኙነት የማምለጫ ጥበብ",
        "author": "ዶ/ር ራማኒ ዱርቫሱላ | ትርጉም፦ የአዕምሮ ምግቦች & Baya Books",
        "short_author": "ዶ/ር ራማኒ ዱርቫሱላ",
        "cover": "/static/covers/narcissist_trap.jpg",
        "pages": "274 ገጾች",
        "rating": "⭐ 4.9 (1.2k)",
        "badge": "🔥 በጣም ተነባቢ | 274 ገጾች",
        "badge_style": "",
        "category": "psychology",
        "data_url": "/static/books_data/narcissist_full.json",
        "paywall_desc": "ይህን ሙሉ የ 274 ገጽ መጽሐፍ (ሁሉንም 11 ክፍሎች) አሁኑኑ በ 399 ብር ብቻ በመክፈት፣ ከመርዛማ ግንኙነት ራስሽን ነጻ የምታወጪበትን ሙሉ ጥበብ በ«📖 የኔ መጻሕፍት» ውስጥ ለዘላለም አግኚ።"
    },
    "boundaries": {
        "key": "boundaries",
        "title": "ድንበርህን አብጅ",
        "subtitle": "ምንም ይቅርታ ሳትጠይቅ ጤናማ ድንበር የማስከበር ጥበብ",
        "author": "ኔድራ ግሎቨር ታዋብ | ትርጉም፦ Baya Books",
        "short_author": "ኔድራ ታዋብ",
        "cover": "/static/covers/boundaries.png",
        "pages": "216 ገጾች",
        "rating": "⭐ 4.9 (950+)",
        "badge": "✨ አዲስ የተጨመረ | 216 ገጾች",
        "badge_style": "color: #34d399; background: rgba(16, 185, 129, 0.15); border-color: rgba(16, 185, 129, 0.3);",
        "category": "psychology",
        "data_url": "/static/books_data/boundaries_full.json",
        "paywall_desc": "ይህን ሙሉ የ 216 ገጽ መጽሐፍ (ሁሉንም 17 ክፍሎች) አሁኑኑ በ 399 ብር ብቻ በመክፈት፣ ምንም የጥፋተኝነት ስሜት ሳይሰማዎት ጤናማ ድንበር የሚያበጁበትን ሙሉ መመሪያ በ«📖 የኔ መጻሕፍት» ውስጥ ለዘላለም ያግኙ።"
    },
    "buyback": {
        "key": "buyback",
        "title": "ጊዜህን አስመልስ (Buy Back Your Time)",
        "subtitle": "ንግድህን እያሳደግክ ነጻነትህን የምታገኝበት ጥበብ",
        "author": "ዳን ማርቴል (Dan Martell) | ትርጉም፦ Baya Books",
        "short_author": "ዳን ማርቴል",
        "cover": "/static/covers/buy_back_time.png",
        "pages": "213 ገጾች",
        "rating": "⭐ 4.8 (890)",
        "badge": "⚡ ምርጥ የቢዝነስ መጽሐፍ | 213 ገጾች",
        "badge_style": "color: #60a5fa; background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.3);",
        "category": "productivity",
        "data_url": "/static/books_data/buyback_full.json",
        "paywall_desc": "ይህን ሙሉ የ 213 ገጽ መጽሐፍ (ሁሉንም 16 ክፍሎች) አሁኑኑ በ 399 ብር ብቻ በመክፈት፣ ጊዜዎን መልሰው የሚገዙበትን እና ገቢዎን በእጥፍ የሚያሳድጉበትን ሙሉ ቀመር በ«📖 የኔ መጻሕፍት» ውስጥ ለዘላለም ያግኙ።"
    },
    "meaning": {
        "key": "meaning",
        "title": "የህይወት ትርጉም",
        "subtitle": "በባዶነት ዘመን ውስጥ የሕይወት ዓላማን የማግኘት ጥበብ",
        "author": "አርተር ሲ. ብሩክስ (Arthur C. Brooks) | ትርጉም፦ Baya Books",
        "short_author": "አርተር ብሩክስ",
        "cover": "/static/covers/meaning.jpg",
        "pages": "176 ገጾች",
        "rating": "⭐ 4.9 (1.1k)",
        "badge": "🌟 #1 NYT Bestseller | 176 ገጾች",
        "badge_style": "color: #fbbf24; background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3);",
        "category": "psychology",
        "data_url": "/static/books_data/meaning_full.json",
        "paywall_desc": "ይህን ሙሉ የ 176 ገጽ መጽሐፍ (ሁሉንም 11 ክፍሎች) አሁኑኑ በ 399 ብር ብቻ በመክፈት፣ እውነተኛ የሕይወት ትርጉምና ዓላማን የሚያገኙበትን ሙሉ ጥበብ በ«📖 የኔ መጻሕፍት» ውስጥ ለዘላለም ያግኙ።"
    }
}

books_meta_js = json.dumps(books_meta, ensure_ascii=False, separators=(',', ':'))

initial_preview = {}
for b_key, b_info in books_meta.items():
    json_path = b_info["data_url"].lstrip("/")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as jf:
            ch_list = json.load(jf)
            if isinstance(ch_list, dict):
                ch_list = ch_list.get("chapters", [])
            preview_chs = []
            for idx, c in enumerate(ch_list):
                blocks = c.get("blocks") or []
                words = sum(len(str(b.get("text", "")).split()) for b in blocks)
                mins = max(2, round(words / 135))
                sub = next((b.get("text", "") for b in blocks if b.get("type") == "subtitle"), c.get("name", ""))
                preview_chs.append({
                    "id": c["id"],
                    "label": c["label"],
                    "name": c["name"],
                    "subtitle": sub,
                    "mins": mins,
                    "free": c["free"],
                    "blocks": blocks if idx == 0 else None
                })
            initial_preview[b_key] = preview_chs
initial_preview_js = json.dumps(initial_preview, ensure_ascii=False, separators=(',', ':'))

html_content = f'''<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Baya Books — Digital Library</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Ethiopic:wght@400;600;700;800&family=Noto+Sans+Ethiopic:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0d1017;
            --bg-secondary: #161b26;
            --bg-card: #1c2230;
            --text-primary: #eef2f6;
            --text-secondary: #b0b8c4;
            --text-muted: #6e7888;
            --accent: #6366f1;
            --accent-soft: rgba(99, 102, 241, 0.14);
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
            --gold: #f59e0b;
            --green: #10b981;
            --border: rgba(255, 255, 255, 0.08);
            --font-ui: 'Noto Sans Ethiopic', 'Plus Jakarta Sans', system-ui, sans-serif;
            --font-reader: 'Noto Serif Ethiopic', 'Noto Sans Ethiopic', Georgia, serif;
        }}

        body.light-theme {{
            --bg-primary: #f8fafc;
            --bg-secondary: #eef2f6;
            --bg-card: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --accent: #4f46e5;
            --accent-soft: rgba(79, 70, 229, 0.1);
            --border: rgba(0, 0, 0, 0.08);
        }}

        body.sepia-theme {{
            --bg-primary: #f6efe2;
            --bg-secondary: #eadec9;
            --bg-card: #fbf6ec;
            --text-primary: #3d2e1e;
            --text-secondary: #5c4730;
            --text-muted: #8c7355;
            --accent: #b45309;
            --accent-soft: rgba(180, 83, 9, 0.12);
            --border: rgba(95, 75, 50, 0.14);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        body {{
            font-family: var(--font-ui);
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            overflow-x: hidden;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        header {{
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(13, 16, 23, 0.88);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border);
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        body.light-theme header {{ background: rgba(248, 250, 252, 0.9); }}
        body.sepia-theme header {{ background: rgba(246, 239, 226, 0.9); }}

        .brand {{ display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; padding-right: 8px; }}
        .brand-icon {{
            width: 42px; height: 42px; border-radius: 10px;
            overflow: hidden; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            border: 1.5px solid rgba(99, 102, 241, 0.45);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
        }}
        .brand-icon img {{
            width: 100%; height: 100%; object-fit: cover; display: block;
        }}
        .brand-text h1 {{ font-size: 15px; font-weight: 800; letter-spacing: -0.2px; line-height: 1.25; }}
        .brand-text p {{ font-size: 11px; color: var(--text-muted); line-height: 1.35; margin-top: 2px; }}

        .btn-icon {{
            background: var(--bg-secondary); border: 1px solid var(--border);
            color: var(--text-primary); width: 36px; height: 36px; flex-shrink: 0;
            border-radius: 10px; display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 14px; font-weight: 700; transition: all 0.2s;
        }}
        .btn-icon:active {{ transform: scale(0.94); }}

        .container {{ max-width: 680px; margin: 0 auto; padding: 18px 16px 80px; }}

        .hero-banner {{
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%);
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 18px; padding: 20px; margin-bottom: 20px;
            position: relative; overflow: hidden;
        }}
        .hero-tag {{
            display: inline-flex; align-items: center; gap: 6px;
            font-size: 11px; font-weight: 700; text-transform: uppercase;
            color: #ec4899; background: rgba(236, 72, 153, 0.12);
            padding: 4px 10px; border-radius: 20px; margin-bottom: 10px;
        }}
        .hero-title {{ font-size: 18px; font-weight: 800; line-height: 1.35; margin-bottom: 8px; }}
        .hero-desc {{ font-size: 13px; color: var(--text-secondary); line-height: 1.5; }}

        /* Filter Pills */
        .filter-scroll {{
            display: flex; gap: 8px; margin-bottom: 20px;
            overflow-x: auto; padding-bottom: 4px; scrollbar-width: none;
        }}
        .filter-scroll::-webkit-scrollbar {{ display: none; }}
        .filter-pill {{
            padding: 8px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
            background: var(--bg-card); border: 1px solid var(--border);
            color: var(--text-secondary); cursor: pointer; white-space: nowrap; transition: all 0.2s;
            display: inline-flex; align-items: center; gap: 5px;
        }}
        .filter-pill.active {{
            background: var(--accent); color: #ffffff; border-color: var(--accent);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
        }}
        .count-badge {{
            background: rgba(255, 255, 255, 0.2);
            padding: 1px 6px; border-radius: 10px; font-size: 10px; font-weight: 800;
        }}

        /* My Books Dedicated Section */
        #my-books-section {{
            display: none;
            margin-bottom: 28px;
            padding: 16px;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        /* Book Cards */
        .book-list {{ display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }}
        .featured-card {{
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 20px; padding: 16px; display: flex; gap: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }}
        .book-cover-wrap {{
            flex-shrink: 0; width: 112px; height: auto; align-self: flex-start; border-radius: 10px;
            overflow: hidden; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.12); background: transparent;
        }}
        .book-cover {{ width: 100%; height: auto; object-fit: contain; display: block; border-radius: 10px; }}

        .book-details {{ display: flex; flex-direction: column; justify-content: space-between; flex: 1; }}
        .book-badge {{
            display: inline-block; align-self: flex-start; font-size: 10px; font-weight: 700;
            padding: 3px 8px; border-radius: 6px; background: rgba(245, 158, 11, 0.15);
            color: var(--gold); border: 1px solid rgba(245, 158, 11, 0.3); margin-bottom: 4px;
        }}
        .book-badge.owned {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border-color: rgba(16, 185, 129, 0.35);
        }}
        .book-title {{ font-size: 16px; font-weight: 800; line-height: 1.3; margin-bottom: 4px; }}
        .book-subtitle {{ font-size: 11.5px; color: var(--text-secondary); margin-bottom: 6px; line-height: 1.4; }}
        .book-meta {{
            display: flex; align-items: center; gap: 10px; font-size: 11px;
            color: var(--text-muted); margin-bottom: 10px;
        }}
        .btn-group {{ display: flex; gap: 8px; margin-top: auto; }}
        .btn {{
            flex: 1; padding: 9px 12px; border-radius: 10px; font-size: 12px; font-weight: 700;
            border: none; cursor: pointer; display: inline-flex; align-items: center;
            justify-content: center; gap: 5px; transition: all 0.2s; font-family: var(--font-ui);
        }}
        .btn:active {{ transform: scale(0.97); }}
        .btn-primary {{ background: var(--accent-gradient); color: #ffffff; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4); }}
        .btn-success {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff; box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35); }}
        .btn-outline {{ background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-primary); }}

        .empty-mybooks {{
            background: var(--bg-card); border: 1px dashed var(--border);
            border-radius: 18px; padding: 32px 20px; text-align: center; display: none;
        }}

        /* ══════════════════════════════════════════
           PUBLICATION-GRADE READER VIEW
        ══════════════════════════════════════════ */
        #view-reader {{ display: none; }}
        .reader-header {{
            position: sticky; top: 0; z-index: 60;
            background: rgba(13, 16, 23, 0.95); backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border); padding: 10px 14px;
            display: flex; align-items: center; justify-content: space-between;
            transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.28s ease;
        }}
        .reader-header.zen-hidden {{
            transform: translateY(-110%);
            opacity: 0;
            pointer-events: none;
        }}
        body.light-theme .reader-header {{ background: rgba(248, 250, 252, 0.95); }}
        body.sepia-theme .reader-header {{ background: rgba(246, 239, 226, 0.95); }}

        .progress-bar-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 3.5px; z-index: 120; background: rgba(255,255,255,0.04); }}
        .progress-bar-fill {{ height: 100%; width: 0%; background: var(--accent-gradient); box-shadow: 0 0 8px rgba(99, 102, 241, 0.6); transition: width 0.15s ease; }}

        .reader-top-title {{
            font-size: 13.5px; font-weight: 700; color: var(--text-primary);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
            flex: 1; min-width: 0; margin: 0 10px; cursor: pointer; display: block;
        }}
        .reader-controls {{ display: flex; align-items: center; gap: 6px; flex-shrink: 0; }}

        /* Chapter Tabs Bar */
        .chapter-tabs {{
            display: flex; gap: 8px; padding: 12px 16px;
            background: var(--bg-secondary); border-bottom: 1px solid var(--border);
            overflow-x: auto; scrollbar-width: none; position: sticky; top: 57px; z-index: 55;
            transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.28s ease;
        }}
        .chapter-tabs.zen-hidden {{
            transform: translateY(-180%);
            opacity: 0;
            pointer-events: none;
        }}
        .chapter-tabs::-webkit-scrollbar {{ display: none; }}
        .chapter-tabs::after {{
            content: '';
            position: sticky;
            right: 0;
            top: 0;
            bottom: 0;
            min-width: 32px;
            flex-shrink: 0;
            background: linear-gradient(to right, transparent, var(--bg-secondary) 85%);
            pointer-events: none;
        }}
        .ch-tab {{
            padding: 7px 14px; border-radius: 10px; font-size: 12px; font-weight: 700;
            background: var(--bg-card); color: var(--text-secondary);
            border: 1px solid var(--border); cursor: pointer; white-space: nowrap;
            transition: all 0.2s; font-family: var(--font-ui);
        }}
        .ch-tab.active {{
            background: var(--accent); color: #ffffff; border-color: var(--accent);
            box-shadow: 0 3px 10px rgba(99, 102, 241, 0.35);
        }}
        .ch-tab.done {{
            border-color: rgba(16, 185, 129, 0.4);
        }}
        .ch-tab.locked {{
            opacity: 0.75;
            border-style: dashed;
        }}

        /* Reader Typography & Article Container */
        .reader-content {{
            max-width: 600px;
            margin: 0 auto;
            padding: 28px 22px 110px;
            font-family: var(--font-reader);
            font-size: 17.5px;
            line-height: 2.0;
            color: var(--text-primary);
            transition: font-size 0.15s ease, line-height 0.15s ease;
        }}

        .ch-header-card {{
            margin-bottom: 30px;
            padding-bottom: 22px;
            border-bottom: 2px solid var(--border);
        }}
        .ch-meta-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }}
        .ch-badge {{
            display: inline-block;
            font-family: var(--font-ui);
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--accent);
            background: var(--accent-soft);
            padding: 4px 12px;
            border-radius: 20px;
        }}
        .ch-time-badge {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-family: var(--font-ui);
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            padding: 4px 10px;
            border-radius: 20px;
        }}
        .ch-main-subtitle {{
            font-size: 1.38em;
            font-weight: 800;
            line-height: 1.4;
            color: var(--text-primary);
        }}
        .ch-tip-hint {{
            font-family: var(--font-ui);
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .reader-p {{
            margin-bottom: 1.35em;
            text-align: left;
            letter-spacing: 0.01em;
            word-spacing: 0.04em;
            border-radius: 10px;
            transition: background 0.2s ease, padding 0.2s ease;
            position: relative;
        }}
        .reader-p.highlighted, .reader-li.highlighted, .reader-quote.highlighted {{
            background: rgba(245, 158, 11, 0.16) !important;
            border-left: 3.5px solid #f59e0b !important;
            padding: 10px 14px 24px 14px;
            border-radius: 6px 12px 12px 6px;
            position: relative;
        }}
        .reader-p.highlighted::after, .reader-li.highlighted::after, .reader-quote.highlighted::after {{
            content: '🔖';
            position: absolute;
            bottom: 5px;
            right: 10px;
            font-size: 13px;
            line-height: 1;
        }}

        .block-actions {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            margin-top: 8px;
            font-family: var(--font-ui);
        }}
        .block-act-btn {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 16px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-family: var(--font-ui);
        }}
        .block-act-btn:active {{ transform: scale(0.95); }}
        .block-act-btn.saved {{
            color: #fbbf24;
            border-color: rgba(245, 158, 11, 0.45);
            background: rgba(245, 158, 11, 0.12);
        }}

        .reader-p.lead-p::first-letter {{
            font-size: 1.65em;
            font-weight: 800;
            color: var(--accent);
            padding-right: 3px;
        }}

        .reader-h4 {{
            font-family: var(--font-ui);
            font-size: 1.15em;
            font-weight: 800;
            color: var(--text-primary);
            margin: 2.0em 0 0.85em;
            padding-left: 12px;
            border-left: 4px solid var(--accent);
            line-height: 1.45;
        }}

        .reader-quote {{
            background: var(--accent-soft);
            border-left: 4px solid var(--accent);
            border-radius: 0 14px 14px 0;
            padding: 18px 20px 14px;
            margin: 1.8em 0;
        }}
        .reader-quote-text {{
            font-style: italic;
            font-weight: 600;
            line-height: 1.75;
            margin-bottom: 8px;
        }}
        .reader-quote-author {{
            font-family: var(--font-ui);
            font-size: 0.82em;
            font-weight: 700;
            color: var(--accent);
            text-align: right;
        }}

        .reader-li {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 1.0em;
            line-height: 1.8;
        }}
        .reader-li-dot {{
            color: var(--accent);
            font-weight: 800;
            font-size: 1.1em;
            flex-shrink: 0;
            margin-top: 1px;
        }}

        .reader-divider {{
            text-align: center;
            color: var(--gold);
            font-size: 16px;
            letter-spacing: 8px;
            margin: 2.2em 0;
            opacity: 0.85;
        }}

        .ch-nav-footer {{
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 12px;
        }}

        /* Book Progress Bar on Card */
        .book-progress-wrap {{
            margin: 6px 0 10px;
        }}
        .book-progress-top {{
            display: flex;
            justify-content: space-between;
            font-size: 10.5px;
            font-weight: 700;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }}
        .book-progress-bar {{
            height: 5px;
            width: 100%;
            background: var(--bg-secondary);
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        .book-progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981, #34d399);
            border-radius: 6px;
            transition: width 0.3s ease;
        }}

        /* Floating Reading Status Pill */
        #readingStatusPill {{
            position: fixed;
            bottom: 18px;
            right: 16px;
            z-index: 90;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-family: var(--font-ui);
            font-size: 11px;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 20px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.35);
            display: none;
            align-items: center;
            gap: 8px;
            backdrop-filter: blur(12px);
            opacity: 1;
            transition: opacity 0.5s ease;
        }}
        #readingStatusPill.faded {{
            opacity: 0;
            pointer-events: none;
        }}

        /* Toast Notification */
        #readerToast {{
            position: fixed;
            bottom: 64px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: #10b981;
            color: #ffffff;
            font-family: var(--font-ui);
            font-size: 12.5px;
            font-weight: 700;
            padding: 9px 18px;
            border-radius: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            z-index: 350;
            opacity: 0;
            pointer-events: none;
            transition: all 0.25s ease;
            white-space: nowrap;
        }}
        #readerToast.show {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}

        /* Typography Popover */
        .typo-popover {{
            position: fixed;
            top: 58px;
            right: 14px;
            width: 265px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px;
            z-index: 150;
            box-shadow: 0 14px 34px rgba(0,0,0,0.45);
            display: none;
            font-family: var(--font-ui);
        }}
        .typo-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .typo-row:last-child {{ margin-bottom: 0; }}
        .typo-label {{ font-size: 11.5px; font-weight: 700; color: var(--text-secondary); }}
        .typo-btn {{
            flex: 1;
            padding: 7px 8px;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            font-family: var(--font-ui);
            text-align: center;
        }}
        .typo-btn.active {{
            border-color: var(--accent);
            background: var(--accent-soft);
            color: var(--accent);
        }}

        /* TOC & Highlights Drawer List */
        .drawer-list {{
            max-height: 62vh;
            overflow-y: auto;
            padding-right: 4px;
        }}
        .toc-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding: 12px 14px;
            border-radius: 12px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.18s;
        }}
        .toc-item.active {{
            border-color: var(--accent);
            background: var(--accent-soft);
        }}
        .hl-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-left: 3.5px solid #f59e0b;
            border-radius: 8px 14px 14px 8px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }}

        /* Paywall Box */
        .paywall-box {{
            background: linear-gradient(135deg, rgba(28, 34, 48, 0.96) 0%, rgba(15, 19, 28, 0.98) 100%);
            border: 1.5px solid rgba(245, 158, 11, 0.45);
            border-radius: 20px;
            padding: 26px 20px;
            text-align: center;
            margin: 42px 0 20px;
            box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35);
            font-family: var(--font-ui);
            color: #f3f4f6;
        }}
        .paywall-icon {{
            width: 50px; height: 50px; border-radius: 50%;
            background: rgba(245, 158, 11, 0.15); color: var(--gold);
            font-size: 22px; display: flex; align-items: center; justify-content: center;
            margin: 0 auto 12px; border: 1px solid rgba(245, 158, 11, 0.35);
        }}
        .paywall-title {{ font-size: 17px; font-weight: 800; margin-bottom: 8px; color: #ffffff; }}
        .paywall-desc {{ font-size: 13px; color: #b0b8c4; line-height: 1.6; margin-bottom: 18px; }}

        /* Modal */
        .modal-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px);
            z-index: 200; display: none; align-items: flex-end; justify-content: center;
        }}
        .modal-card {{
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 24px 24px 0 0; width: 100%; max-width: 540px;
            padding: 24px 20px 36px; animation: slideUp 0.25s ease-out;
        }}
        @keyframes slideUp {{ from {{ transform: translateY(100%); }} to {{ transform: translateY(0); }} }}
        .bank-item {{
            background: var(--bg-secondary); border: 1px solid var(--border);
            border-radius: 12px; padding: 12px 14px; margin-bottom: 10px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .bank-name {{ font-size: 11px; color: var(--text-muted); }}
        .bank-acc {{ font-size: 14px; font-weight: 700; user-select: all; }}

        /* Reading Streak & Daily Goal Bar */
        .streak-goal-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 12px 14px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            box-shadow: var(--shadow);
        }}
        .streak-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(245, 158, 11, 0.14);
            border: 1px solid rgba(245, 158, 11, 0.35);
            color: #fbbf24;
            padding: 6px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 800;
            white-space: nowrap;
        }}
        .goal-progress-wrap {{
            flex: 1;
            min-width: 0;
        }}
        .goal-progress-top {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            font-weight: 700;
            color: var(--text-secondary);
            margin-bottom: 5px;
        }}
        .goal-bar-bg {{
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 99px;
            overflow: hidden;
        }}
        .goal-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #f59e0b, #10b981);
            border-radius: 99px;
            transition: width 0.35s ease;
        }}

        /* Search Input & Results */
        .search-input {{
            width: 100%;
            padding: 11px 14px;
            border-radius: 12px;
            border: 1.5px solid var(--border);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-family: var(--font-ui);
            font-size: 13.5px;
            outline: none;
            margin-bottom: 12px;
        }}
        .search-input:focus {{
            border-color: var(--accent);
        }}
        .search-hit-mark {{
            background: rgba(245, 158, 11, 0.35);
            color: #fde68a;
            padding: 0 3px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .hl-note-box {{
            margin-top: 8px;
            padding: 8px 10px;
            background: rgba(99, 102, 241, 0.1);
            border-left: 2.5px solid var(--accent);
            border-radius: 6px;
            font-size: 12px;
            color: var(--text-secondary);
            font-family: var(--font-ui);
        }}
    </style>
</head>
<body>

    <div class="progress-bar-container">
        <div id="readingProgress" class="progress-bar-fill"></div>
    </div>

    <!-- ══════════════════════════════════════════
         VIEW 1: STORE / LIBRARY
    ══════════════════════════════════════════ -->
    <div id="view-home">
        <header>
            <div class="brand">
                <div class="brand-icon"><img src="/static/covers/baya_logo.jpg" alt="Baya Books"></div>
                <div class="brand-text">
                    <h1>የአዕምሮ ምግቦች &amp; Baya books</h1>
                    <p>እያንዳንዱ የሚያነቡት ገጽ ከፍ ወዳለ ማንነት እንዲወስድዎት ተመኘን</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <button class="btn-icon" onclick="openHighlightsModal('all')" title="Saved Quotes">🔖</button>
                <button class="btn-icon" onclick="toggleTheme()" title="Theme">🌓</button>
            </div>
        </header>

        <div class="container">
            <div class="hero-banner">
                <div class="hero-tag">✨ የዕለቱ ምርጥ ስጦታ</div>
                <h2 class="hero-title">የዓለማችን ተፅዕኖ ፈጣሪ የስነ-ልቦና መጻሕፍት</h2>
                <p class="hero-desc">ጥልቅ ግንዛቤ፣ የተግባር መመሪያ እና የህይወት ለውጥ የሚያመጡ መጻሕፍትን በደቂቃዎች ውስጥ ያንብቡ።</p>
            </div>

            <!-- Daily Reading Goal & Streak Bar -->
            <div class="streak-goal-card" onclick="cycleDailyGoal()" title="ዕለታዊ የንባብ ግብ ለመቀየር ይጫኑ">
                <div class="streak-badge" id="streakBadge">🔥 1 ቀን</div>
                <div class="goal-progress-wrap">
                    <div class="goal-progress-top">
                        <span id="goalStatusText">🎯 የዛሬ ንባብ፦ 0 / 15 ደቂቃ</span>
                        <span id="goalTotalBooksText" style="color: #34d399;">⏱ ግብ ቀይር ▾</span>
                    </div>
                    <div class="goal-bar-bg">
                        <div class="goal-bar-fill" id="goalBarFill" style="width: 0%;"></div>
                    </div>
                </div>
            </div>

            <!-- Dedicated My Books Section (Auto-shows when customer owns >= 1 book) -->
            <div id="my-books-section">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="font-size: 15px; font-weight: 800; color: #34d399; display: flex; align-items: center; gap: 6px;">
                        <span>📖 የኔ መጻሕፍት (My Purchased Books)</span>
                    </div>
                </div>
                <div class="book-list" id="my-books-list" style="margin-bottom: 0;"></div>
            </div>

            <!-- Filter Pills -->
            <div class="filter-scroll">
                <div class="filter-pill active" id="pill-all" onclick="filterCategory('all', this)">🔥 ሁሉም (All)</div>
                <div class="filter-pill" id="pill-mybooks" onclick="filterCategory('mybooks', this)">
                    <span>📖 የኔ መጻሕፍት</span>
                    <span class="count-badge" id="mybooks-count">0</span>
                </div>
                <div class="filter-pill" onclick="openHighlightsModal('all')">
                    <span>🔖 ጥቅሶች</span>
                    <span class="count-badge" id="highlights-count">0</span>
                </div>
                <div class="filter-pill" onclick="filterCategory('psychology', this)">🧠 ግንኙነት & ስነ-ልቦና</div>
                <div class="filter-pill" onclick="filterCategory('productivity', this)">⏱️ ጊዜ & ቢዝነስ</div>
            </div>

            <div class="section-header" id="catalog-header" style="margin-bottom: 12px; font-size: 15px; font-weight: 700;">
                <span>📚 የሚገኙ መጻሕፍት (Available Books)</span>
            </div>

            <!-- Dynamic Catalog List -->
            <div class="book-list" id="catalog-list"></div>

            <!-- Empty state when user taps 'My Books' tab but hasn't purchased any yet -->
            <div class="empty-mybooks" id="empty-mybooks">
                <div style="font-size: 36px; margin-bottom: 10px;">📚</div>
                <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 6px;">ገና የገዙት መጽሐፍ የለም</h3>
                <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
                    ከመጻሕፍት መደብሩ ውስጥ የሚፈልጉትን መጽሐፍ በ 399 ብር ሲገዙ፣ ሙሉው መጽሐፍ እዚህ <b>«የኔ መጻሕፍት»</b> ስር ለዘላለም ይቀመጥልዎታል።
                </p>
                <button class="btn btn-primary" onclick="filterCategory('all', document.getElementById('pill-all'))">
                    <span>🔥 መጻሕፍትን ተመልከት</span>
                </button>
            </div>
        </div>
    </div>


    <!-- ══════════════════════════════════════════
         VIEW 2: PUBLICATION-GRADE READER
    ══════════════════════════════════════════ -->
    <div id="view-reader">
        <div class="reader-header" id="readerHeader">
            <button class="btn-icon" onclick="closeReader()" title="Back">‹</button>
            <div class="reader-top-title" id="readerBookTitle" onclick="openTocModal()" title="ማውጫ ክፈት">የመጽሐፍ ርዕስ ▾</div>
            <div class="reader-controls">
                <button class="btn-icon" onclick="adjustFontSize(-1)" title="Smaller">A-</button>
                <button class="btn-icon" onclick="adjustFontSize(1)" title="Larger">A+</button>
                <button class="btn-icon" onclick="toggleTheme()" title="Theme">🌓</button>
            </div>
        </div>

        <!-- Chapter Switcher Bar -->
        <div class="chapter-tabs" id="chapterTabs"></div>

        <div class="reader-content" id="readerBody" onclick="handleReaderBodyTap()">
            <!-- Dynamic Chapter Content -->
            <div id="readerChapterContent"></div>

            <!-- Next / Previous Chapter Buttons -->
            <div class="ch-nav-footer" id="chapterNavFooter"></div>

            <!-- Paywall Card (shown on last free chapter if not owned) -->
            <div class="paywall-box" id="readerPaywall" style="display: none;">
                <div class="paywall-icon">🔥</div>
                <h3 class="paywall-title">ሙሉውን መጽሐፍ ዛሬውኑ ማንበብ ይጀምሩ!</h3>
                <p class="paywall-desc" id="paywallDesc"></p>
                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 12px;">
                    <button id="paywallBtnExtend" class="btn btn-primary" style="display: none; width: 100%; padding: 13px; font-size: 14px; background: linear-gradient(135deg, #10b981, #059669);" onclick="openPayModal(activeBookKey, 'extend')">
                        <span>➕ ተጨማሪ 5 ቀናት ጨምር — 49 ብር</span>
                    </button>
                    <button class="btn btn-primary" style="width: 100%; padding: 13px; font-size: 14px;" onclick="openPayModal(activeBookKey, 'buy')">
                        <span>💎 ሙሉውን መጽሐፍ ለዘላለም ግዛ — 399 ብር</span>
                    </button>
                    <button class="btn btn-outline" style="width: 100%; padding: 12px; font-size: 14px; border-color: rgba(245, 158, 11, 0.45); color: #fbbf24; background: rgba(245, 158, 11, 0.1);" onclick="openPayModal(activeBookKey, 'rent')">
                        <span>⏳ ለ 10 ቀናት ተከራይ — 149 ብር (ኪራይ)</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Floating Reading Progress & Time Left Pill -->
    <div id="readingStatusPill" onclick="openTocModal()">
        <span id="pillChapterPct">0%</span>
        <span style="opacity: 0.4;">•</span>
        <span id="pillTimeLeft">⏱ ቀሪ 5 ደቂቃ</span>
    </div>

    <!-- Toast Notification -->
    <div id="readerToast">✅ ተቀምጧል!</div>

    <!-- ══════════════════════════════════════════
         MODAL: IN-BOOK SEARCH (🔍 ፈልግ)
    ══════════════════════════════════════════ -->
    <div id="modal-search" class="modal-overlay" onclick="closeSearchModal()">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <h3 style="font-size: 16px; font-weight: 800;">🔍 በመጽሐፉ ውስጥ ፈልግ</h3>
                    <p style="font-size: 11.5px; color: var(--text-secondary);" id="searchBookSub">ቃል ወይም ሐረግ ይጻፉ</p>
                </div>
                <button class="btn-icon" onclick="closeSearchModal()">✕</button>
            </div>
            <input type="text" id="bookSearchInput" class="search-input" placeholder="ለምሳሌ፦ ፍቅር፣ ድንበር፣ ትኩረት..." oninput="runBookSearch(this.value)">
            <div class="drawer-list" id="searchResultsList"></div>
        </div>
    </div>

    <!-- ══════════════════════════════════════════
         MODAL: QUOTE IMAGE CARD (🖼️ ምስል አጋራ)
    ══════════════════════════════════════════ -->
    <div id="modal-quote-card" class="modal-overlay" onclick="closeQuoteCardModal()">
        <div class="modal-card" onclick="event.stopPropagation()" style="text-align: center;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                <h3 style="font-size: 15px; font-weight: 800;">🖼️ የጥቅስ ምስል (Quote Card)</h3>
                <button class="btn-icon" onclick="closeQuoteCardModal()">✕</button>
            </div>
            <canvas id="quoteCanvas" width="720" height="720" style="width: 100%; max-width: 320px; border-radius: 14px; border: 1px solid var(--border); margin-bottom: 12px;"></canvas>
            <div style="display: flex; gap: 8px;">
                <button class="btn btn-outline" style="flex: 1;" onclick="downloadQuoteCanvas()">📥 ምስል አውርድ</button>
                <button class="btn btn-primary" style="flex: 1;" onclick="shareCurrentQuoteCard()">📤 በቴሌግራም አጋራ</button>
            </div>
        </div>
    </div>

    <!-- ══════════════════════════════════════════
         MODAL: TABLE OF CONTENTS (📑 ማውጫ)
    ══════════════════════════════════════════ -->
    <div id="modal-toc" class="modal-overlay" onclick="closeTocModal()">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                <div>
                    <h3 style="font-size: 16px; font-weight: 800;" id="tocBookTitle">📑 የመጽሐፉ ማውጫ</h3>
                    <p style="font-size: 11.5px; color: var(--text-secondary);" id="tocProgressSub">0% ተነቧል</p>
                </div>
                <button class="btn-icon" onclick="closeTocModal()">✕</button>
            </div>
            <div class="drawer-list" id="tocList"></div>
        </div>
    </div>

    <!-- ══════════════════════════════════════════
         MODAL: SAVED HIGHLIGHTS & QUOTES (🔖 ጥቅሶች)
    ══════════════════════════════════════════ -->
    <div id="modal-highlights" class="modal-overlay" onclick="closeHighlightsModal()">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <div>
                    <h3 style="font-size: 16px; font-weight: 800;">🔖 የተቀመጡ ጥቅሶች እና ማስታወሻዎች</h3>
                    <p style="font-size: 11.5px; color: var(--text-secondary);">የወደዱትን አንቀጽ ተጭነው በመቆየት (Long-press) እዚህ ማስቀመጥ ይችላሉ</p>
                </div>
                <button class="btn-icon" onclick="closeHighlightsModal()">✕</button>
            </div>
            <div class="drawer-list" id="highlightsList"></div>
        </div>
    </div>


    <!-- ══════════════════════════════════════════
         MODAL: PAYMENT (399 Buy / 149 10d Rent / 49 +5d Extend)
    ══════════════════════════════════════════ -->
    <div id="modal-pay" class="modal-overlay">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div class="modal-header" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 class="modal-title" id="modalBookTitle">📱 የክፍያ መረጃ</h3>
                <button class="btn-icon" onclick="closePayModal()">✕</button>
            </div>

            <!-- Plan Toggle (Full Purchase vs 10-Day Rental vs +5-Day Extension) -->
            <div id="planGrid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 14px;">
                <button id="planBtnBuy" onclick="selectPayPlan('buy')" style="padding: 10px 8px; border-radius: 12px; border: 1.5px solid #6366f1; background: rgba(99, 102, 241, 0.18); color: #fff; font-family: inherit; font-weight: 700; font-size: 12.5px; cursor: pointer; text-align: center;">
                    💎 ሙሉ ግዢ<br><span style="font-size: 13.5px; color: #a5b4fc;">399 ብር (ለዘላለም)</span>
                </button>
                <button id="planBtnRent" onclick="selectPayPlan('rent')" style="padding: 10px 8px; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04); color: var(--text-secondary); font-family: inherit; font-weight: 700; font-size: 12.5px; cursor: pointer; text-align: center;">
                    ⏳ የ 10 ቀን ኪራይ<br><span style="font-size: 13.5px; color: #fbbf24;">149 ብር (10 ቀናት)</span>
                </button>
                <button id="planBtnExtend" onclick="selectPayPlan('extend')" style="display: none; grid-column: span 2; padding: 10px 8px; border-radius: 12px; border: 1.5px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.04); color: var(--text-secondary); font-family: inherit; font-weight: 700; font-size: 12.5px; cursor: pointer; text-align: center;">
                    ➕ ተጨማሪ 5 ቀናት ኪራይ — <span style="font-size: 13.5px; color: #34d399;">49 ብር (+5 ቀናት)</span>
                </button>
            </div>

            <p id="modalPayInstruction" style="font-size: 13px; color: var(--text-secondary); margin-bottom: 14px;">
                እባክዎ <b>399 ብር (ለሙሉ ግዢ)</b> በሚከተሉት አማራጮች ያስገቡ፦
            </p>

            <div class="bank-item">
                <div>
                    <div class="bank-name">🏦 CBE (ንግድ ባንክ)</div>
                    <div class="bank-acc">1000073164765</div>
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">በኃይሉ ጌታቸው</div>
            </div>

            <div class="bank-item">
                <div>
                    <div class="bank-name">🏦 CBE Birr (ሲቢኢ ብር)</div>
                    <div class="bank-acc">0912689900</div>
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">በኃይሉ ጌታቸው</div>
            </div>

            <div class="bank-item">
                <div>
                    <div class="bank-name">📱 Telebirr (ቴሌብር)</div>
                    <div class="bank-acc">0912689900</div>
                </div>
                <div style="font-size: 12px; color: var(--text-muted);">በኃይሉ ጌታቸው</div>
            </div>

            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 12px; padding: 12px; margin: 14px 0; font-size: 12px; line-height: 1.5;">
                ✅ <b>ከከፈሉ በኋላ፦</b> የከፈሉበትን ደረሰኝ (Screenshot) በቀጥታ በቦቱ ላይ ይላኩልን። ሲስተማችን በሰከንዶች ውስጥ አረጋግጦ መጽሐፉን <b>«📖 የኔ መጻሕፍት»</b> ውስጥ ይከፍትልዎታል!
            </div>

            <button class="btn btn-primary" style="width: 100%;" onclick="returnToBot()">
                <span>💬 ወደ ቦቱ ተመልሰህ ደረሰኝ ላክ</span>
            </button>
        </div>
    </div>


    <script>
        const BOOKS_META = {books_meta_js};
        const LOADED_CHAPTERS = {initial_preview_js};
        const FULL_LOADED_FLAG = {{}};
        const INFLIGHT_FETCHES = {{}};
        let ownedBooks = [];
        let rentedBooks = {{}};
        let expiredBooks = [];
        let activeBookKey = 'narcissist';
        let activePayBookKey = 'narcissist';
        let activePayMode = 'buy';
        let activeChapterIdx = 0;
        let currentCategory = 'all';
        let activeChapterMins = 5;
        let lastScrollY = 0;
        let _toastTimer = null;
        let _pillFadeTimer = null;

        const tg = window.Telegram ? window.Telegram.WebApp : null;
        if (tg) {{ tg.ready(); tg.expand(); }}

        // ══════════════════════════════════════════
        // 1. PERSISTENT STORAGE (Progress, Highlights, Prefs)
        // ══════════════════════════════════════════
        const STORAGE_PROGRESS_KEY = 'baya_progress_v1';
        const STORAGE_HIGHLIGHTS_KEY = 'baya_highlights_v1';
        const STORAGE_PREFS_KEY = 'baya_prefs_v1';

        function getReadingProgressMap() {{
            try {{
                return JSON.parse(localStorage.getItem(STORAGE_PROGRESS_KEY) || '{{}}') || {{}};
            }} catch (e) {{ return {{}}; }}
        }}

        function saveBookProgress(bookKey, chIdx, scrollPct, markCompleted) {{
            try {{
                const map = getReadingProgressMap();
                const prev = map[bookKey] || {{ ch: 1, pct: 0, completed: [] }};
                const completedSet = new Set(Array.isArray(prev.completed) ? prev.completed : []);
                if (markCompleted && chIdx > 0) completedSet.add(chIdx);
                map[bookKey] = {{
                    ch: chIdx,
                    pct: Math.round(scrollPct || 0),
                    completed: Array.from(completedSet),
                    updatedAt: Date.now()
                }};
                localStorage.setItem(STORAGE_PROGRESS_KEY, JSON.stringify(map));
            }} catch (e) {{}}
        }}

        function getBookOverallPct(bookKey) {{
            const chapters = LOADED_CHAPTERS[bookKey] || [];
            const totalReadingCh = Math.max(1, chapters.length - 1); // exclude ch 0 overview
            const prog = getReadingProgressMap()[bookKey];
            if (!prog) return 0;
            const completedCount = (prog.completed || []).filter(i => i > 0).length;
            let pct = Math.round((completedCount / totalReadingCh) * 100);
            if (prog.ch > 0 && !(prog.completed || []).includes(prog.ch)) {{
                pct += Math.round(((prog.pct || 0) / 100) * (100 / totalReadingCh));
            }}
            return Math.min(100, Math.max(0, pct));
        }}

        function getSavedHighlights() {{
            try {{
                const arr = JSON.parse(localStorage.getItem(STORAGE_HIGHLIGHTS_KEY) || '[]');
                return Array.isArray(arr) ? arr : [];
            }} catch (e) {{ return []; }}
        }}

        function setSavedHighlights(arr) {{
            try {{
                localStorage.setItem(STORAGE_HIGHLIGHTS_KEY, JSON.stringify(arr));
            }} catch (e) {{}}
            updateHighlightsBadge();
        }}

        function updateHighlightsBadge() {{
            const el = document.getElementById('highlights-count');
            if (el) el.innerText = getSavedHighlights().length;
        }}

        function isTextHighlighted(bookKey, chIdx, text) {{
            const list = getSavedHighlights();
            return list.some(h => h.bookKey === bookKey && h.chIdx === chIdx && h.text === text);
        }}

        function toggleHighlightItem(bookKey, chIdx, chLabel, text) {{
            const clean = (text || '').trim();
            if (!clean) return false;
            let list = getSavedHighlights();
            const existsIdx = list.findIndex(h => h.bookKey === bookKey && h.chIdx === chIdx && h.text === clean);
            if (existsIdx >= 0) {{
                list.splice(existsIdx, 1);
                setSavedHighlights(list);
                showToast('🗑️ ጥቅሱ ከተቀመጡት ተወግዷል');
                return false;
            }} else {{
                const meta = BOOKS_META[bookKey] || {{}};
                list.unshift({{
                    id: Date.now() + '_' + Math.random().toString(36).slice(2, 6),
                    bookKey: bookKey,
                    bookTitle: meta.title || bookKey,
                    chIdx: chIdx,
                    chLabel: chLabel || ('ክፍል ' + chIdx),
                    text: clean,
                    savedAt: new Date().toLocaleDateString('am-ET')
                }});
                setSavedHighlights(list);
                showToast('🔖 ጥቅሱ በ«ጥቅሶች» ውስጥ ተቀምጧል!');
                return true;
            }}
        }}

        function showToast(msg) {{
            const t = document.getElementById('readerToast');
            if (!t) return;
            t.innerText = msg;
            t.classList.add('show');
            if (_toastTimer) clearTimeout(_toastTimer);
            _toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
        }}

        function shareQuoteText(text, bookKey) {{
            const meta = BOOKS_META[bookKey] || BOOKS_META[activeBookKey] || {{}};
            const title = meta.title || 'Baya Books';
            const snippet = (text || '').trim();
            const shareBody = `“${{snippet}}”\n\n📖 ከ«${{title}}» መጽሐፍ የተወሰደ\n✨ በ @bayabooks_bot ላይ ያንብቡ`;
            const shareUrl = 'https://t.me/share/url?url=' + encodeURIComponent('https://t.me/bayabooks_bot') + '&text=' + encodeURIComponent(shareBody);
            if (tg && tg.openTelegramLink) {{
                tg.openTelegramLink(shareUrl);
            }} else {{
                window.open(shareUrl, '_blank');
            }}
        }}

        // Determine User ID from query param, Telegram WebApp initData, or localStorage
        function getUserId() {{
            const params = new URLSearchParams(window.location.search);
            let uid = params.get('uid') || '';
            if (!uid && tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) {{
                uid = String(tg.initDataUnsafe.user.id);
            }}
            if (!uid && tg && tg.initData) {{
                try {{
                    const q = new URLSearchParams(tg.initData);
                    const u = q.get('user');
                    if (u) {{
                        const parsed = JSON.parse(u);
                        if (parsed && parsed.id) uid = String(parsed.id);
                    }}
                }} catch (e) {{}}
            }}
            if (uid) {{
                try {{ localStorage.setItem('baya_uid', uid); }} catch (e) {{}}
                return uid;
            }}
            try {{ return localStorage.getItem('baya_uid') || ''; }} catch (e) {{ return ''; }}
        }}

        const USER_ID = getUserId();

        async function loadUserBooks() {{
            updateHighlightsBadge();
            loadSavedReaderPrefs();
            if (USER_ID) {{
                try {{
                    const res = await fetch('/api/user_books?uid=' + encodeURIComponent(USER_ID));
                    const data = await res.json();
                    if (data && Array.isArray(data.books)) {{
                        ownedBooks = data.books;
                    }}
                    if (data && data.rentals) {{
                        rentedBooks = data.rentals;
                    }}
                    if (data && Array.isArray(data.expired)) {{
                        expiredBooks = data.expired;
                    }}
                }} catch (e) {{
                    console.error('Error loading user books:', e);
                }}
            }}
            renderStore();
        }}

        async function finishRental(bookKey) {{
            expiredBooks = expiredBooks.filter(k => k !== bookKey);
            renderStore();
            if (USER_ID) {{
                try {{
                    await fetch('/api/finish_rental?uid=' + encodeURIComponent(USER_ID) + '&book=' + encodeURIComponent(bookKey));
                }} catch (e) {{}}
            }}
        }}

        function createBookCardHTML(b, isOwned) {{
            const rentDays = rentedBooks[b.key];
            const isExpired = !isOwned && expiredBooks.includes(b.key);
            const badgeHTML = isOwned
                ? (rentDays
                    ? `<div class="book-badge owned" style="background: rgba(245, 158, 11, 0.16); color: #fbbf24; border-color: rgba(245, 158, 11, 0.35);">⏳ የተከራየ (ቀሪ ${{rentDays}} ቀናት) | ${{b.pages}}</div>`
                    : `<div class="book-badge owned">✅ የተገዛ (ሙሉ መጽሐፍ) | ${{b.pages}}</div>`)
                : (isExpired
                    ? `<div class="book-badge" style="background: rgba(239, 68, 68, 0.16); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35);">⏰ የ 10 ቀን ኪራይ ጊዜው አልቋል | ${{b.pages}}</div>`
                    : `<div class="book-badge" style="${{b.badge_style}}">${{b.badge}}</div>`);

            const prog = getReadingProgressMap()[b.key];
            const overallPct = isOwned ? getBookOverallPct(b.key) : 0;
            const resumeCh = (isOwned && prog && prog.ch >= 1) ? prog.ch : (isOwned ? 1 : 0);
            const chapters = LOADED_CHAPTERS[b.key] || [];
            const resumeLabel = (chapters[resumeCh] && chapters[resumeCh].label) ? chapters[resumeCh].label : ('ክፍል ' + resumeCh);

            let progressHTML = '';
            if (isOwned && (overallPct > 0 || (prog && prog.ch > 1))) {{
                progressHTML = `
                    <div class="book-progress-wrap">
                        <div class="book-progress-meta">
                            <span>📊 ${{overallPct}}% ተነቧል</span>
                            <span style="color: #a5b4fc; font-weight: 700;">${{resumeLabel}}</span>
                        </div>
                        <div class="book-progress-bar">
                            <div class="book-progress-fill" style="width: ${{Math.max(4, overallPct)}}%;"></div>
                        </div>
                    </div>`;
            }}

            let buttonsHTML = '';
            if (isOwned) {{
                const hasResume = prog && (prog.ch > 1 || (prog.pct && prog.pct > 5));
                const btnText = hasResume
                    ? `📖 ካቆሙበት ይቀጥሉ (${{resumeLabel}})`
                    : `📖 ሙሉውን መጽሐፍ አንብብ`;
                buttonsHTML = `<div class="btn-group">
                       <button class="btn btn-success" onclick="openReader('${{b.key}}', ${{resumeCh}}, true)">
                           <span>${{btnText}}</span>
                       </button>
                   </div>`;
            }} else if (isExpired) {{
                buttonsHTML = `
                   <div style="margin-top: 12px; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 10px 12px;">
                       <div style="font-size: 12px; font-weight: 700; color: #fbbf24; margin-bottom: 8px; text-align: center; line-height: 1.4;">
                           ⏰ የኪራይ ጊዜዎ ተጠናቋል! መጽሐፉን ጨርሰውታል ወይስ ቀን መጨመር ይፈልጋሉ?
                       </div>
                       <div class="btn-group" style="margin-top: 0;">
                           <button class="btn btn-outline" style="flex: 1; border-color: rgba(16, 185, 129, 0.45); color: #34d399; background: rgba(16, 185, 129, 0.1);" onclick="finishRental('${{b.key}}')">
                               <span>✅ ጨርሻለሁ</span>
                           </button>
                           <button class="btn btn-primary" style="flex: 1.35; background: linear-gradient(135deg, #f59e0b, #d97706); box-shadow: none;" onclick="openPayModal('${{b.key}}', 'extend')">
                               <span>➕ 5 ቀን ጨምር (49 ብር)</span>
                           </button>
                       </div>
                   </div>`;
            }} else {{
                buttonsHTML = `<div class="btn-group" style="flex-wrap: wrap;">
                       <button class="btn btn-primary" style="flex: 1 1 100%;" onclick="openReader('${{b.key}}', 0)">
                           <span>📖 ስለ መጽሐፉ</span>
                       </button>
                       <button class="btn btn-outline" style="flex: 1; flex-direction: column; gap: 2px; padding: 8px 6px; line-height: 1.25; border-color: rgba(245, 158, 11, 0.4); color: #fbbf24;" onclick="openPayModal('${{b.key}}', 'rent')">
                           <span style="font-size: 13px; font-weight: 800;">⏳ 149 ብር</span>
                           <span style="font-size: 11px; opacity: 0.9;">(10 ቀን ኪራይ)</span>
                       </button>
                       <button class="btn btn-outline" style="flex: 1; flex-direction: column; gap: 2px; padding: 8px 6px; line-height: 1.25;" onclick="openPayModal('${{b.key}}', 'buy')">
                           <span style="font-size: 13px; font-weight: 800;">💎 399 ብር</span>
                           <span style="font-size: 11px; opacity: 0.85;">(ግዢ)</span>
                       </button>
                   </div>`;
            }}

            return `
                <div class="featured-card" data-category="${{b.category}}" data-owned="${{isOwned ? 'true' : 'false'}}">
                    <div class="book-cover-wrap" onclick="openReader('${{b.key}}', ${{resumeCh}}, true)" style="cursor:pointer;">
                        <img src="${{b.cover}}" alt="${{b.title}}" class="book-cover">
                    </div>
                    <div class="book-details">
                        <div>
                            ${{badgeHTML}}
                            <h3 class="book-title">${{b.title}}</h3>
                            <p class="book-subtitle">${{b.subtitle}}</p>
                            <div class="book-meta">
                                <span>👤 ${{b.short_author}}</span>
                                <span>${{b.rating}}</span>
                            </div>
                            ${{progressHTML}}
                        </div>
                        ${{buttonsHTML}}
                    </div>
                </div>
            `;
        }}

        function renderStore() {{
            const myBookKeys = [...new Set([...ownedBooks, ...expiredBooks])];
            document.getElementById('mybooks-count').innerText = myBookKeys.length;
            updateHighlightsBadge();
            renderStreakGoalBar();

            // Top My Books Highlight Box (shown on 'all' view when user has owned or expired-rental books)
            const mySection = document.getElementById('my-books-section');
            const myList = document.getElementById('my-books-list');
            if (myBookKeys.length > 0 && currentCategory === 'all') {{
                mySection.style.display = 'block';
                myList.innerHTML = myBookKeys
                    .filter(k => BOOKS_META[k])
                    .map(k => createBookCardHTML(BOOKS_META[k], ownedBooks.includes(k)))
                    .join('');
            }} else {{
                mySection.style.display = 'none';
            }}

            // Main Catalog List
            const catalogList = document.getElementById('catalog-list');
            const emptyMyBooks = document.getElementById('empty-mybooks');
            const catalogHeader = document.getElementById('catalog-header');

            const allKeys = Object.keys(BOOKS_META);
            let filteredKeys = allKeys;

            if (currentCategory === 'mybooks') {{
                filteredKeys = allKeys.filter(k => myBookKeys.includes(k));
                catalogHeader.innerHTML = '<span>📖 የኔ መጻሕፍት እና ኪራይ (My Books & Rentals)</span>';
            }} else if (currentCategory !== 'all') {{
                filteredKeys = allKeys.filter(k => BOOKS_META[k].category === currentCategory);
                catalogHeader.innerHTML = '<span>📚 የሚገኙ መጻሕፍት (Available Books)</span>';
            }} else {{
                catalogHeader.innerHTML = '<span>📚 ሁሉም መጻሕፍት (All Books)</span>';
            }}

            if (currentCategory === 'mybooks' && filteredKeys.length === 0) {{
                catalogList.innerHTML = '';
                emptyMyBooks.style.display = 'block';
            }} else {{
                emptyMyBooks.style.display = 'none';
                catalogList.innerHTML = filteredKeys
                    .map(k => createBookCardHTML(BOOKS_META[k], ownedBooks.includes(k)))
                    .join('');
            }}
        }}

        function filterCategory(cat, el) {{
            currentCategory = cat;
            document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
            if (el) el.classList.add('active');
            renderStore();
        }}

        // ══════════════════════════════════════════
        // 2. SCROLL LISTENER: Progress Bar, Status Pill, Auto-Save & Zen Mode
        // ══════════════════════════════════════════
        window.addEventListener('scroll', () => {{
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = height > 0 ? Math.min(100, Math.max(0, (winScroll / height) * 100)) : 0;
            const bar = document.getElementById("readingProgress");
            if (bar) bar.style.width = scrolled + "%";

            const readerVisible = document.getElementById('view-reader').style.display === 'block';
            const pill = document.getElementById('readingStatusPill');
            if (!readerVisible) {{
                if (pill) pill.style.display = 'none';
                return;
            }}

            if (pill) {{
                pill.style.display = 'flex';
                pill.classList.remove('faded');
                const pctRound = Math.round(scrolled);
                const remMins = Math.max(1, Math.ceil(activeChapterMins * (1 - scrolled / 100)));
                document.getElementById('pillChapterPct').innerText = pctRound + '%';
                document.getElementById('pillTimeLeft').innerText = scrolled >= 94
                    ? '✓ ክፍሉ ተጠናቋል'
                    : `⏱ ቀሪ ~${{remMins}} ደቂቃ`;
                if (_pillFadeTimer) clearTimeout(_pillFadeTimer);
                _pillFadeTimer = setTimeout(() => pill.classList.add('faded'), 3000);
            }}

            // Auto-save reading progress & mark chapter completed at >= 85% scroll
            if (activeBookKey && activeChapterIdx > 0) {{
                const markDone = scrolled >= 85;
                saveBookProgress(activeBookKey, activeChapterIdx, scrolled, markDone);
            }}

            // Zen Mode: hide top header & chapter tabs when scrolling down, show when scrolling up
            const hdr = document.getElementById('readerHeader');
            const tabs = document.getElementById('chapterTabs');
            const delta = winScroll - lastScrollY;
            if (winScroll > 120 && delta > 9) {{
                if (hdr) hdr.classList.add('zen-hidden');
                if (tabs) tabs.classList.add('zen-hidden');
                closeTypoPopover();
            }} else if (delta < -7 || winScroll < 60) {{
                if (hdr) hdr.classList.remove('zen-hidden');
                if (tabs) tabs.classList.remove('zen-hidden');
            }}
            lastScrollY = winScroll;
        }}, {{ passive: true }});

        function handleReaderBodyTap() {{
            closeTypoPopover();
            const pill = document.getElementById('readingStatusPill');
            if (pill && document.getElementById('view-reader').style.display === 'block') {{
                pill.style.display = 'flex';
                pill.classList.remove('faded');
                if (_pillFadeTimer) clearTimeout(_pillFadeTimer);
                _pillFadeTimer = setTimeout(() => pill.classList.add('faded'), 3000);
            }}
        }}

        function ensureFullBookLoaded(bookKey) {{
            if (FULL_LOADED_FLAG[bookKey]) return Promise.resolve(LOADED_CHAPTERS[bookKey]);
            if (INFLIGHT_FETCHES[bookKey]) return INFLIGHT_FETCHES[bookKey];
            const meta = BOOKS_META[bookKey];
            if (!meta) return Promise.resolve([]);
            INFLIGHT_FETCHES[bookKey] = fetch(meta.data_url)
                .then(res => res.json())
                .then(data => {{
                    const prevMeta = LOADED_CHAPTERS[bookKey] || [];
                    const arr = (Array.isArray(data) ? data : (data.chapters || [])).map((c, idx) => ({{
                        ...c,
                        mins: (prevMeta[idx] && prevMeta[idx].mins) || c.mins || 5,
                        subtitle: (prevMeta[idx] && prevMeta[idx].subtitle) || c.subtitle || ''
                    }}));
                    LOADED_CHAPTERS[bookKey] = arr;
                    FULL_LOADED_FLAG[bookKey] = true;
                    delete INFLIGHT_FETCHES[bookKey];
                    return arr;
                }})
                .catch(err => {{
                    delete INFLIGHT_FETCHES[bookKey];
                    throw err;
                }});
            return INFLIGHT_FETCHES[bookKey];
        }}

        async function openReader(bookKey, chIdx, restoreScroll) {{
            const meta = BOOKS_META[bookKey];
            if (!meta) return;

            activeBookKey = bookKey;
            const isOwned = ownedBooks.includes(bookKey);
            let targetIdx = (typeof chIdx === 'number') ? chIdx : (isOwned ? 1 : 0);
            if (isOwned && targetIdx === 0) targetIdx = 1;

            // Immediately clear previous book DOM so another book's content is NEVER shown
            document.getElementById('readerBookTitle').innerText = meta.title + ' ▾';
            document.getElementById('paywallDesc').innerText = meta.paywall_desc;
            document.getElementById('chapterTabs').innerHTML = '';
            document.getElementById('readerChapterContent').innerHTML = '';
            document.getElementById('chapterNavFooter').innerHTML = '';
            document.getElementById('readerPaywall').style.display = 'none';

            document.getElementById('view-home').style.display = 'none';
            document.getElementById('view-reader').style.display = 'block';
            document.getElementById('readerHeader').classList.remove('zen-hidden');
            document.getElementById('chapterTabs').classList.remove('zen-hidden');

            // Kick off background fetch of full chapters immediately
            ensureFullBookLoaded(bookKey).catch(() => {{}});

            // Render requested chapter
            await renderChapter(targetIdx, restoreScroll);
        }}

        function attachHighlightBehavior(el, bookKey, chIdx, chLabel, textContent) {{
            if (isTextHighlighted(bookKey, chIdx, textContent)) {{
                el.classList.add('highlighted');
            }}

            // Long-press (500ms) to highlight & save quote (or long-press again to un-highlight)
            let _lpTimer = null;
            let _lpFired = false;

            function fireLongPress() {{
                _lpFired = true;
                try {{ navigator.vibrate(50); }} catch (e) {{}}
                const added = toggleHighlightItem(bookKey, chIdx, chLabel, textContent);
                el.classList.toggle('highlighted', added);
            }}

            function cancelLongPress() {{
                if (_lpTimer) {{ clearTimeout(_lpTimer); _lpTimer = null; }}
            }}

            el.addEventListener('touchstart', () => {{
                _lpFired = false;
                _lpTimer = setTimeout(fireLongPress, 500);
            }}, {{ passive: true }});

            el.addEventListener('touchmove', cancelLongPress, {{ passive: true }});
            el.addEventListener('touchend', (e) => {{
                cancelLongPress();
                if (_lpFired) {{ e.preventDefault(); }}
            }});
            el.addEventListener('touchcancel', cancelLongPress);

            // Fallback for desktop: double-click
            el.addEventListener('dblclick', (e) => {{
                e.preventDefault();
                const added = toggleHighlightItem(bookKey, chIdx, chLabel, textContent);
                el.classList.toggle('highlighted', added);
            }});
        }}

        async function renderChapter(idx, restoreScroll) {{
            const targetBookKey = activeBookKey;
            let chapters = LOADED_CHAPTERS[targetBookKey] || [];
            const isOwned = ownedBooks.includes(targetBookKey);
            let ch = chapters[idx];
            if (!ch) return;

            // If user clicked a locked chapter and doesn't own the book, trigger payment modal!
            if (!isOwned && !ch.free) {{
                openPayModal(targetBookKey);
                return;
            }}

            activeChapterIdx = idx;
            const prog = getReadingProgressMap()[targetBookKey] || {{ completed: [] }};
            const completedArr = prog.completed || [];

            // Render Chapter Tabs immediately (skip Chapter 0 overview for owned books)
            const tabsEl = document.getElementById('chapterTabs');
            tabsEl.innerHTML = '';

            // Quick utility pills in the chapter bar (keeps top title header 100% unobstructed)
            [
                {{ label: '📑 ማውጫ', action: () => openTocModal() }},
                {{ label: '🔍 ፈልግ', action: () => openSearchModal() }},
                {{ label: '🔖 ጥቅሶች', action: () => openHighlightsModal(targetBookKey) }}
            ].forEach(item => {{
                const uBtn = document.createElement('button');
                uBtn.className = 'ch-tab';
                uBtn.style.borderColor = 'rgba(99, 102, 241, 0.35)';
                uBtn.innerText = item.label;
                uBtn.onclick = item.action;
                tabsEl.appendChild(uBtn);
            }});

            chapters.forEach((c, i) => {{
                if (isOwned && i === 0) return;
                const unlocked = isOwned || c.free;
                const isDone = completedArr.includes(i);
                const btn = document.createElement('button');
                btn.className = 'ch-tab' + (i === idx ? ' active' : '') + (!unlocked ? ' locked' : '');
                btn.innerText = unlocked ? ((isDone ? '✓ ' : '') + c.name) : ('🔒 ' + c.label);
                btn.onclick = () => renderChapter(i, false);
                tabsEl.appendChild(btn);
                if (i === idx && idx > 1) {{
                    setTimeout(() => btn.scrollIntoView({{ behavior: 'smooth', inline: 'center', block: 'nearest' }}), 50);
                }}
            }});

            const contentEl = document.getElementById('readerChapterContent');

            // If this chapter's blocks haven't finished downloading yet, wait for background fetch
            if (!ch.blocks) {{
                contentEl.innerHTML = '<div style="text-align:center; padding: 60px 20px; color: var(--text-secondary);">⏳ ምዕራፉን በመክፈት ላይ...</div>';
                try {{
                    await ensureFullBookLoaded(targetBookKey);
                }} catch (e) {{
                    if (activeBookKey === targetBookKey) {{
                        contentEl.innerHTML = '<div style="text-align:center; padding: 60px 20px; color: #ef4444;">⚠️ መጽሐፉን መጫን አልተቻለም። እባክዎ እንደገና ይሞክሩ።</div>';
                    }}
                    return;
                }}
                if (activeBookKey !== targetBookKey || activeChapterIdx !== idx) return;
                chapters = LOADED_CHAPTERS[targetBookKey] || [];
                ch = chapters[idx];
                if (!ch || !ch.blocks) return;
            }}

            // Calculate estimated reading minutes
            const wordCount = ch.blocks.reduce((acc, b) => acc + ((b.text || '').split(/\\s+/).length), 0);
            activeChapterMins = ch.mins || Math.max(2, Math.round(wordCount / 135));

            // Save current chapter index
            if (idx > 0) {{
                const savedPct = (restoreScroll && prog && prog.ch === idx) ? (prog.pct || 0) : 0;
                saveBookProgress(targetBookKey, idx, savedPct, false);
            }}

            // Render Content Blocks
            contentEl.innerHTML = '';

            const headerCard = document.createElement('div');
            headerCard.className = 'ch-header-card';

            const badgeRow = document.createElement('div');
            badgeRow.style.cssText = 'display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:10px;';

            const badge = document.createElement('div');
            badge.className = 'ch-badge';
            badge.style.marginBottom = '0';
            badge.innerText = ch.label;
            badgeRow.appendChild(badge);

            const timePill = document.createElement('div');
            timePill.style.cssText = 'font-size:11.5px; font-weight:700; color:var(--text-secondary); background:rgba(255,255,255,0.05); padding:4px 10px; border-radius:20px; border:1px solid var(--border-light);';
            timePill.innerText = `⏱ ~${{activeChapterMins}} ደቂቃ ንባብ • 💡 ጥቅስ ለማስቀመጥ አንቀጹን ተጭነው ይቆዩ`;
            badgeRow.appendChild(timePill);

            headerCard.appendChild(badgeRow);

            let firstParaRendered = false;

            ch.blocks.forEach((b, bIdx) => {{
                if (b.type === 'subtitle') {{
                    const sub = document.createElement('h2');
                    sub.className = 'ch-main-subtitle';
                    sub.innerText = b.text;
                    headerCard.appendChild(sub);
                }} else if (b.type === 'quote') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const qBox = document.createElement('div');
                    qBox.className = 'reader-quote';
                    qBox.id = 'rblock-' + bIdx;
                    const qTxt = document.createElement('div');
                    qTxt.className = 'reader-quote-text';
                    qTxt.innerText = b.text;
                    qBox.appendChild(qTxt);
                    if (b.author) {{
                        const qAuth = document.createElement('div');
                        qAuth.className = 'reader-quote-author';
                        qAuth.innerText = '— ' + b.author;
                        qBox.appendChild(qAuth);
                    }}
                    attachHighlightBehavior(qBox, targetBookKey, idx, ch.label, b.text);
                    contentEl.appendChild(qBox);
                }} else if (b.type === 'h4') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const h4 = document.createElement('h4');
                    h4.className = 'reader-h4';
                    h4.id = 'rblock-' + bIdx;
                    h4.innerText = b.text;
                    contentEl.appendChild(h4);
                }} else if (b.type === 'li') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const li = document.createElement('div');
                    li.className = 'reader-li';
                    li.id = 'rblock-' + bIdx;
                    li.innerHTML = `<span class="reader-li-dot">✦</span><div>${{b.text}}</div>`;
                    attachHighlightBehavior(li, targetBookKey, idx, ch.label, b.text);
                    contentEl.appendChild(li);
                }} else if (b.type === 'divider') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const div = document.createElement('div');
                    div.className = 'reader-divider';
                    div.innerText = b.text;
                    contentEl.appendChild(div);
                }} else {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const p = document.createElement('p');
                    p.className = 'reader-p' + (!firstParaRendered ? ' lead-p' : '');
                    p.id = 'rblock-' + bIdx;
                    firstParaRendered = true;
                    p.innerText = b.text;
                    attachHighlightBehavior(p, targetBookKey, idx, ch.label, b.text);
                    contentEl.appendChild(p);
                }}
            }});

            // Render Bottom Navigation (hide Chapter 0 back link for owned books)
            const navFooter = document.getElementById('chapterNavFooter');
            navFooter.innerHTML = '';

            const minBackIdx = isOwned ? 1 : 0;
            if (idx > minBackIdx) {{
                const prevBtn = document.createElement('button');
                prevBtn.className = 'btn btn-outline';
                prevBtn.style.padding = '13px';
                prevBtn.innerText = '← ' + chapters[idx - 1].label;
                prevBtn.onclick = () => renderChapter(idx - 1, false);
                navFooter.appendChild(prevBtn);
            }}

            const nextCh = chapters[idx + 1];
            const pwExtBtn = document.getElementById('paywallBtnExtend');
            if (pwExtBtn) {{
                pwExtBtn.style.display = expiredBooks.includes(targetBookKey) ? 'inline-flex' : 'none';
            }}
            if (nextCh && (isOwned || nextCh.free)) {{
                const nextBtn = document.createElement('button');
                nextBtn.className = 'btn btn-primary';
                nextBtn.style.padding = '13px';
                nextBtn.innerText = 'ቀጣይ፦ ' + nextCh.label + ' →';
                nextBtn.onclick = () => {{
                    if (idx > 0) saveBookProgress(targetBookKey, idx, 100, true);
                    renderChapter(idx + 1, false);
                }};
                navFooter.appendChild(nextBtn);
                document.getElementById('readerPaywall').style.display = 'none';
            }} else if (!isOwned && nextCh && !nextCh.free) {{
                document.getElementById('readerPaywall').style.display = 'block';
            }} else {{
                document.getElementById('readerPaywall').style.display = 'none';
            }}

            if (restoreScroll && prog && prog.ch === idx && prog.pct > 5 && prog.pct < 92) {{
                setTimeout(() => {{
                    const docH = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                    window.scrollTo({{ top: Math.round((prog.pct / 100) * docH), behavior: 'smooth' }});
                    showToast(`📖 ካቆሙበት (${{prog.pct}}%) ቀጥሏል`);
                }}, 120);
            }} else {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }}
        }}

        function closeReader() {{
            document.getElementById('view-reader').style.display = 'none';
            document.getElementById('readingStatusPill').style.display = 'none';
            closeTypoPopover();
            document.getElementById('view-home').style.display = 'block';
            renderStore();
            window.scrollTo(0, 0);
        }}

        // ══════════════════════════════════════════
        // 3. TABLE OF CONTENTS DRAWER (📑 ማውጫ)
        // ══════════════════════════════════════════
        function openTocModal() {{
            const meta = BOOKS_META[activeBookKey];
            if (!meta) return;
            const chapters = LOADED_CHAPTERS[activeBookKey] || [];
            const isOwned = ownedBooks.includes(activeBookKey);
            const prog = getReadingProgressMap()[activeBookKey] || {{ completed: [] }};
            const completedArr = prog.completed || [];
            const overallPct = isOwned ? getBookOverallPct(activeBookKey) : 0;

            document.getElementById('tocBookTitle').innerText = '📑 ' + meta.title;
            document.getElementById('tocProgressSub').innerText = isOwned
                ? `${{overallPct}}% ተነቧል • ${{completedArr.length}} / ${{Math.max(1, chapters.length - 1)}} ክፍሎች ተጠናቀዋል`
                : '🔒 ሙሉውን ማውጫ ለመክፈት መጽሐፉን ይግዙ ወይም ይከራዩ';

            const listEl = document.getElementById('tocList');
            listEl.innerHTML = chapters.map((c, i) => {{
                if (isOwned && i === 0) return '';
                const unlocked = isOwned || c.free;
                const isDone = completedArr.includes(i);
                const isCurrent = i === activeChapterIdx;
                const mins = c.mins || 4;
                const sub = c.subtitle || c.name;
                const statusBadge = !unlocked
                    ? '<span style="font-size:12px; color:var(--text-muted);">🔒</span>'
                    : (isDone
                        ? '<span style="font-size:11px; color:#34d399; font-weight:800;">✓ ተነቧል</span>'
                        : (isCurrent ? '<span style="font-size:11px; color:#a5b4fc; font-weight:800;">📖 በማንበብ ላይ</span>' : `<span style="font-size:11px; color:var(--text-muted);">⏱ ~${{mins}} ደቂቃ</span>`));

                return `
                    <div class="toc-item ${{isCurrent ? 'active' : ''}} ${{!unlocked ? 'locked' : ''}}" onclick="closeTocModal(); renderChapter(${{i}}, false);">
                        <div style="min-width: 0; flex: 1; padding-right: 10px;">
                            <div style="font-size: 13px; font-weight: 800; color: var(--text-primary);">${{c.name}}</div>
                            ${{sub && sub !== c.name ? `<div style="font-size: 11.5px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${{sub}}</div>` : ''}}
                        </div>
                        <div style="flex-shrink: 0;">${{statusBadge}}</div>
                    </div>
                `;
            }}).join('');

            document.getElementById('modal-toc').style.display = 'flex';
        }}

        function closeTocModal() {{
            document.getElementById('modal-toc').style.display = 'none';
        }}

        // ══════════════════════════════════════════
        // 4. HIGHLIGHTS, NOTES & QUOTE IMAGE CARD (🔖 ጥቅሶች)
        // ══════════════════════════════════════════
        function openHighlightsModal(filterBookKey) {{
            const all = getSavedHighlights();
            const list = (filterBookKey && filterBookKey !== 'all')
                ? all.filter(h => h.bookKey === filterBookKey)
                : all;

            const container = document.getElementById('highlightsList');
            if (list.length === 0) {{
                container.innerHTML = `
                    <div style="text-align: center; padding: 36px 16px; color: var(--text-secondary);">
                        <div style="font-size: 34px; margin-bottom: 8px;">🔖</div>
                        <div style="font-size: 14px; font-weight: 800; color: var(--text-primary); margin-bottom: 6px;">ገና የተቀመጠ ጥቅስ የለም</div>
                        <div style="font-size: 12.5px; line-height: 1.6;">መጽሐፍ በሚያነቡበት ጊዜ የወደዱትን አንቀጽ ወይም ነጥብ <b>ተጭነው በመቆየት (Long-press)</b> በወርቃማ ቀለም ማስመር እና እዚህ ማስቀመጥ ይችላሉ!</div>
                    </div>
                `;
            }} else {{
                container.innerHTML = list.map(h => `
                    <div class="hl-card">
                        <div class="hl-text">“${{h.text}}”</div>
                        ${{h.note ? `<div class="hl-note-box">📝 <b>የግል ማስታወሻ፦</b> ${{h.note}}</div>` : ''}}
                        <div class="hl-meta" style="margin-top: 8px;">
                            <span style="cursor:pointer; color:#a5b4fc; font-weight:700;" onclick="closeHighlightsModal(); openReader('${{h.bookKey}}', ${{h.chIdx || 1}}, false)">
                                📖 ${{h.bookTitle}} (${{h.chLabel}})
                            </span>
                            <div style="display:flex; gap:5px; flex-wrap:wrap;">
                                <button class="block-act-btn" onclick="editHighlightNote('${{h.id}}', '${{filterBookKey || 'all'}}')">📝 ማስታወሻ</button>
                                <button class="block-act-btn" onclick="openQuoteCardById('${{h.id}}')">🖼️ ምስል</button>
                                <button class="block-act-btn" onclick="shareHighlightById('${{h.id}}')">📤 አጋራ</button>
                                <button class="block-act-btn" onclick="deleteHighlightById('${{h.id}}', '${{filterBookKey || 'all'}}')">🗑️</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            }}
            document.getElementById('modal-highlights').style.display = 'flex';
        }}

        function editHighlightNote(id, currentFilter) {{
            const list = getSavedHighlights();
            const item = list.find(h => h.id === id);
            if (!item) return;
            const note = window.prompt('📝 ለዚህ ጥቅስ የግል ማስታወሻዎን ይጻፉ፦', item.note || '');
            if (note === null) return;
            item.note = note.trim();
            setSavedHighlights(list);
            openHighlightsModal(currentFilter);
            showToast('✅ ማስታወሻዎ ተቀምጧል!');
        }}

        function openQuoteCardById(id) {{
            const item = getSavedHighlights().find(h => h.id === id);
            if (item) openQuoteCardModal(item.text, item.bookKey);
        }}

        function shareHighlightById(id) {{
            const item = getSavedHighlights().find(h => h.id === id);
            if (item) shareQuoteText(item.text, item.bookKey);
        }}

        function deleteHighlightById(id, currentFilter) {{
            const updated = getSavedHighlights().filter(h => h.id !== id);
            setSavedHighlights(updated);
            openHighlightsModal(currentFilter);
        }}

        function closeHighlightsModal() {{
            document.getElementById('modal-highlights').style.display = 'none';
        }}

        // ══════════════════════════════════════════
        // 4B. CANVAS QUOTE CARD GENERATOR (🖼️)
        // ══════════════════════════════════════════
        let _activeCardQuote = '';
        let _activeCardBookKey = '';

        function openQuoteCardModal(text, bookKey) {{
            _activeCardQuote = (text || '').trim();
            _activeCardBookKey = bookKey || activeBookKey;
            const meta = BOOKS_META[_activeCardBookKey] || {{}};
            const canvas = document.getElementById('quoteCanvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            const W = canvas.width, H = canvas.height;

            // Rich dark gradient background
            const grad = ctx.createLinearGradient(0, 0, W, H);
            grad.addColorStop(0, '#0f172a');
            grad.addColorStop(0.5, '#1e1b4b');
            grad.addColorStop(1, '#090d16');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, H);

            // Gold decorative border
            ctx.strokeStyle = 'rgba(245, 158, 11, 0.55)';
            ctx.lineWidth = 3;
            ctx.strokeRect(32, 32, W - 64, H - 64);

            // Top quote mark
            ctx.fillStyle = 'rgba(245, 158, 11, 0.35)';
            ctx.font = 'bold 90px serif';
            ctx.fillText('“', 64, 130);

            // Wrap & draw quote text
            ctx.fillStyle = '#f8fafc';
            const snippet = _activeCardQuote.length > 280 ? (_activeCardQuote.slice(0, 277) + '...') : _activeCardQuote;
            const fontSize = snippet.length > 170 ? 25 : 30;
            ctx.font = `600 ${{fontSize}}px "Noto Serif Ethiopic", "Plus Jakarta Sans", sans-serif`;

            const words = snippet.split(/\\s+/);
            const lines = [];
            let cur = '';
            const maxW = W - 140;
            words.forEach(w => {{
                const test = cur ? (cur + ' ' + w) : w;
                if (ctx.measureText(test).width > maxW && cur) {{
                    lines.push(cur);
                    cur = w;
                }} else {{
                    cur = test;
                }}
            }});
            if (cur) lines.push(cur);

            const lineH = fontSize * 1.65;
            const totalTextH = lines.length * lineH;
            let startY = Math.max(175, (H - totalTextH) / 2 - 10);
            lines.slice(0, 9).forEach(line => {{
                ctx.fillText(line, 70, startY);
                startY += lineH;
            }});

            // Footer book title & watermark
            ctx.fillStyle = '#fbbf24';
            ctx.font = 'bold 22px "Plus Jakarta Sans", sans-serif';
            ctx.fillText('📖 ' + (meta.title || 'Baya Books'), 70, H - 105);

            ctx.fillStyle = '#94a3b8';
            ctx.font = '600 18px "Plus Jakarta Sans", sans-serif';
            ctx.fillText('✨ የአዕምሮ ምግቦች • @bayabooks_bot', 70, H - 68);

            document.getElementById('modal-quote-card').style.display = 'flex';
        }}

        function closeQuoteCardModal() {{
            document.getElementById('modal-quote-card').style.display = 'none';
        }}

        function downloadQuoteCanvas() {{
            const canvas = document.getElementById('quoteCanvas');
            if (!canvas) return;
            try {{
                const link = document.createElement('a');
                link.download = 'baya-quote.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
                showToast('📥 የጥቅስ ምስሉ ወርዷል!');
            }} catch (e) {{
                shareQuoteText(_activeCardQuote, _activeCardBookKey);
            }}
        }}

        function shareCurrentQuoteCard() {{
            shareQuoteText(_activeCardQuote, _activeCardBookKey);
        }}

        // ══════════════════════════════════════════
        // 4C. IN-BOOK SEARCH (🔍 በመጽሐፉ ውስጥ ፈልግ)
        // ══════════════════════════════════════════
        async function openSearchModal() {{
            const meta = BOOKS_META[activeBookKey];
            if (!meta) return;
            const isOwned = ownedBooks.includes(activeBookKey);
            document.getElementById('searchBookSub').innerText = `በ«${{meta.title}}» ውስጥ ይፈልጉ`;
            document.getElementById('bookSearchInput').value = '';
            document.getElementById('searchResultsList').innerHTML = `
                <div style="text-align: center; padding: 28px 14px; color: var(--text-secondary); font-size: 12.5px;">
                    🔍 በመጽሐፉ ውስጥ የሚፈልጉትን ቃል ከላይ ይጻፉ...
                </div>
            `;
            document.getElementById('modal-search').style.display = 'flex';
            setTimeout(() => document.getElementById('bookSearchInput').focus(), 100);
            if (isOwned) {{
                ensureFullBookLoaded(activeBookKey).catch(() => {{}});
            }}
        }}

        function closeSearchModal() {{
            document.getElementById('modal-search').style.display = 'none';
        }}

        function runBookSearch(query) {{
            const q = (query || '').trim();
            const listEl = document.getElementById('searchResultsList');
            if (q.length < 2) {{
                listEl.innerHTML = `<div style="text-align: center; padding: 28px 14px; color: var(--text-secondary); font-size: 12.5px;">ቢያንስ 2 ፊደላትን ይጻፉ...</div>`;
                return;
            }}
            const isOwned = ownedBooks.includes(activeBookKey);
            const chapters = LOADED_CHAPTERS[activeBookKey] || [];
            const hits = [];
            const qLower = q.toLowerCase();

            chapters.forEach((ch, chIdx) => {{
                if (isOwned && chIdx === 0) return;
                if (!isOwned && !ch.free) return;
                (ch.blocks || []).forEach((b, bIdx) => {{
                    const txt = b.text || '';
                    const pos = txt.toLowerCase().indexOf(qLower);
                    if (pos !== -1) {{
                        const start = Math.max(0, pos - 40);
                        const end = Math.min(txt.length, pos + q.length + 65);
                        let excerpt = (start > 0 ? '...' : '') + txt.slice(start, end) + (end < txt.length ? '...' : '');
                        excerpt = excerpt.replace(new RegExp(q.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&'), 'gi'), m => `<span class="search-hit-mark">${{m}}</span>`);
                        hits.push({{ chIdx, bIdx, chName: ch.name, excerpt }});
                    }}
                }});
            }});

            if (hits.length === 0) {{
                listEl.innerHTML = `<div style="text-align: center; padding: 28px 14px; color: var(--text-secondary); font-size: 12.5px;">ምንም ውጤት አልተገኘም።${{!isOwned ? '<br><span style="color:#fbbf24;">(ሙሉውን መጽሐፍ ለመፈለግ መጽሐፉን ይግዙ ወይም ይከራዩ)</span>' : ''}}</div>`;
                return;
            }}

            listEl.innerHTML = hits.slice(0, 35).map(h => `
                <div class="toc-item" style="flex-direction: column; align-items: flex-start; gap: 4px;" onclick="jumpToSearchHit(${{h.chIdx}}, ${{h.bIdx}})">
                    <div style="font-size: 11.5px; font-weight: 800; color: #a5b4fc;">📖 ${{h.chName}}</div>
                    <div style="font-size: 12.5px; color: var(--text-primary); line-height: 1.55;">${{h.excerpt}}</div>
                </div>
            `).join('');
        }}

        async function jumpToSearchHit(chIdx, bIdx) {{
            closeSearchModal();
            await renderChapter(chIdx, false);
            setTimeout(() => {{
                const targetEl = document.getElementById('rblock-' + bIdx);
                if (targetEl) {{
                    targetEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    targetEl.style.transition = 'box-shadow 0.4s ease';
                    targetEl.style.boxShadow = '0 0 0 3px rgba(245, 158, 11, 0.6)';
                    setTimeout(() => {{ targetEl.style.boxShadow = ''; }}, 2200);
                }}
            }}, 180);
        }}

        // ══════════════════════════════════════════
        // 4D. DAILY READING GOAL & STREAK TRACKER (🔥)
        // ══════════════════════════════════════════
        const STORAGE_STATS_KEY = 'baya_stats_v1';

        function getReadingStats() {{
            const today = new Date().toISOString().slice(0, 10);
            try {{
                const s = JSON.parse(localStorage.getItem(STORAGE_STATS_KEY) || '{{}}');
                const goalMins = s.goalMins || 15;
                let streak = s.streak || 1;
                let todayMins = s.lastDate === today ? (s.todayMins || 0) : 0;
                if (s.lastDate && s.lastDate !== today) {{
                    const diffDays = Math.round((new Date(today) - new Date(s.lastDate)) / 86400000);
                    if (diffDays === 1 && (s.todayMins || 0) > 0) streak += 1;
                    else if (diffDays > 1) streak = 1;
                }}
                return {{ lastDate: today, todayMins, streak, goalMins }};
            }} catch (e) {{
                return {{ lastDate: today, todayMins: 0, streak: 1, goalMins: 15 }};
            }}
        }}

        function saveReadingStats(stats) {{
            try {{ localStorage.setItem(STORAGE_STATS_KEY, JSON.stringify(stats)); }} catch (e) {{}}
        }}

        function renderStreakGoalBar() {{
            const s = getReadingStats();
            saveReadingStats(s);
            const badge = document.getElementById('streakBadge');
            const statusTxt = document.getElementById('goalStatusText');
            const fill = document.getElementById('goalBarFill');
            if (badge) badge.innerText = `🔥 ${{s.streak}} ቀን ተከታታይ`;
            const minsRound = Math.round(s.todayMins);
            const pct = Math.min(100, Math.round((minsRound / s.goalMins) * 100));
            if (statusTxt) {{
                statusTxt.innerText = minsRound >= s.goalMins
                    ? `🎉 የዛሬ ግብ ተሳክቷል! (${{minsRound}} / ${{s.goalMins}} ደቂቃ)`
                    : `🎯 የዛሬ ንባብ፦ ${{minsRound}} / ${{s.goalMins}} ደቂቃ`;
            }}
            if (fill) fill.style.width = pct + '%';
        }}

        function cycleDailyGoal() {{
            const goals = [10, 15, 30];
            const s = getReadingStats();
            const nextGoal = goals[(goals.indexOf(s.goalMins) + 1) % goals.length] || 15;
            s.goalMins = nextGoal;
            saveReadingStats(s);
            renderStreakGoalBar();
            showToast(`🎯 ዕለታዊ የንባብ ግብ ወደ ${{nextGoal}} ደቂቃ ተቀይሯል`);
        }}

        // Increment active reading time by 0.5 min every 30s while reader is open
        setInterval(() => {{
            const readerOpen = document.getElementById('view-reader').style.display === 'block';
            if (readerOpen && !document.hidden) {{
                const s = getReadingStats();
                const prevReached = s.todayMins >= s.goalMins;
                s.todayMins = Number((s.todayMins + 0.5).toFixed(1));
                saveReadingStats(s);
                if (!prevReached && s.todayMins >= s.goalMins) {{
                    showToast('🎉 እንኳን ደስ አለዎት! የዛሬውን የንባብ ግብ አሳክተዋል!');
                }}
            }}
        }}, 30000);

        // ══════════════════════════════════════════
        // 5. TYPOGRAPHY & EYE-COMFORT SETTINGS
        // ══════════════════════════════════════════
        let currFontSize = 17.5;
        let currLineHeight = 2.0;
        const themes = ['dark', 'light-theme', 'sepia-theme'];
        let themeIdx = 0;

        function saveReaderPrefs() {{
            try {{
                localStorage.setItem(STORAGE_PREFS_KEY, JSON.stringify({{
                    fontSize: currFontSize,
                    lineHeight: currLineHeight,
                    theme: themes[themeIdx]
                }}));
            }} catch (e) {{}}
        }}

        function loadSavedReaderPrefs() {{
            try {{
                const p = JSON.parse(localStorage.getItem(STORAGE_PREFS_KEY) || '{{}}');
                if (p.fontSize) currFontSize = Number(p.fontSize) || 17.5;
                if (p.lineHeight) currLineHeight = Number(p.lineHeight) || 2.0;
                if (p.theme && themes.includes(p.theme)) {{
                    themeIdx = themes.indexOf(p.theme);
                }}
            }} catch (e) {{}}
            applyReaderPrefs();
        }}

        function applyReaderPrefs() {{
            const rb = document.getElementById('readerBody');
            if (rb) {{
                rb.style.fontSize = currFontSize + 'px';
                rb.style.lineHeight = String(currLineHeight);
            }}
            const fsDisp = document.getElementById('fontSizeDisplay');
            if (fsDisp) fsDisp.innerText = Math.round(currFontSize) + 'px';

            document.body.className = themes[themeIdx];

            // Sync active buttons in popover
            [1.75, 2, 2.3].forEach(v => {{
                const btn = document.getElementById('lh-' + v);
                if (btn) btn.classList.toggle('active', Math.abs(currLineHeight - v) < 0.05);
            }});
            themes.forEach(t => {{
                const btn = document.getElementById('th-' + t);
                if (btn) btn.classList.toggle('active', themes[themeIdx] === t);
            }});
        }}

        function toggleTypoPopover(e) {{
            if (e) e.stopPropagation();
            const pop = document.getElementById('typoPopover');
            if (pop) pop.classList.toggle('open');
        }}

        function closeTypoPopover() {{
            const pop = document.getElementById('typoPopover');
            if (pop) pop.classList.remove('open');
        }}

        function adjustFontSize(delta) {{
            currFontSize = Math.min(24, Math.max(14, currFontSize + delta));
            applyReaderPrefs();
            saveReaderPrefs();
        }}

        function setLineHeight(val) {{
            currLineHeight = val;
            applyReaderPrefs();
            saveReaderPrefs();
        }}

        function setThemeMode(themeName) {{
            const idx = themes.indexOf(themeName);
            if (idx >= 0) {{
                themeIdx = idx;
                applyReaderPrefs();
                saveReaderPrefs();
            }}
        }}

        function toggleTheme() {{
            themeIdx = (themeIdx + 1) % themes.length;
            applyReaderPrefs();
            saveReaderPrefs();
        }}

        function selectPayPlan(mode) {{
            activePayMode = (mode === 'rent' || mode === 'extend') ? mode : 'buy';
            const b = BOOKS_META[activePayBookKey] || BOOKS_META[activeBookKey];
            const btnBuy = document.getElementById('planBtnBuy');
            const btnRent = document.getElementById('planBtnRent');
            const btnExt = document.getElementById('planBtnExtend');
            const inst = document.getElementById('modalPayInstruction');

            const showExt = (activePayMode === 'extend') || (b && (expiredBooks.includes(b.key) || rentedBooks[b.key]));
            if (btnExt) {{
                btnExt.style.display = showExt ? 'block' : 'none';
            }}

            // Reset all styles
            [btnBuy, btnRent, btnExt].forEach(el => {{
                if (!el) return;
                el.style.border = '1.5px solid rgba(255,255,255,0.12)';
                el.style.background = 'rgba(255,255,255,0.04)';
                el.style.color = 'var(--text-secondary)';
            }});

            if (activePayMode === 'rent') {{
                btnRent.style.border = '1.5px solid #f59e0b';
                btnRent.style.background = 'rgba(245, 158, 11, 0.18)';
                btnRent.style.color = '#fff';
                inst.innerHTML = 'እባክዎ <b>149 ብር (ለ 10 ቀናት ኪራይ)</b> በሚከተሉት አማራጮች ያስገቡ፦';
                if (b) document.getElementById('modalBookTitle').innerText = '⏳ ' + b.title + ' — 149 ብር (10 ቀን ኪራይ)';
            }} else if (activePayMode === 'extend') {{
                if (btnExt) {{
                    btnExt.style.border = '1.5px solid #10b981';
                    btnExt.style.background = 'rgba(16, 185, 129, 0.18)';
                    btnExt.style.color = '#fff';
                }}
                inst.innerHTML = 'እባክዎ <b>49 ብር (ለተጨማሪ 5 ቀናት ኪራይ)</b> በሚከተሉት አማራጮች ያስገቡ፦';
                if (b) document.getElementById('modalBookTitle').innerText = '➕ ' + b.title + ' — 49 ብር (+5 ቀን)';
            }} else {{
                btnBuy.style.border = '1.5px solid #6366f1';
                btnBuy.style.background = 'rgba(99, 102, 241, 0.18)';
                btnBuy.style.color = '#fff';
                inst.innerHTML = 'እባክዎ <b>399 ብር (ለሙሉ ግዢ)</b> በሚከተሉት አማራጮች ያስገቡ፦';
                if (b) document.getElementById('modalBookTitle').innerText = '💎 ' + b.title + ' — 399 ብር (ግዢ)';
            }}

            if (b && USER_ID) {{
                fetch('/api/select_book?uid=' + encodeURIComponent(USER_ID) + '&book=' + encodeURIComponent(b.key) + '&mode=' + encodeURIComponent(activePayMode)).catch(() => {{}});
            }}
        }}

        function openPayModal(bookKey, mode) {{
            const b = BOOKS_META[bookKey] || BOOKS_META[activeBookKey];
            if (b) {{
                activePayBookKey = b.key;
            }}
            const defaultMode = mode || (b && expiredBooks.includes(b.key) ? 'extend' : 'buy');
            selectPayPlan(defaultMode);
            document.getElementById('modal-pay').style.display = 'flex';
        }}
        function closePayModal() {{
            document.getElementById('modal-pay').style.display = 'none';
        }}
        let _isReturningToBot = false;
        async function returnToBot() {{
            if (_isReturningToBot) return;
            _isReturningToBot = true;
            const b = BOOKS_META[activePayBookKey] || BOOKS_META[activeBookKey];
            const uid = getUserId();
            const btn = document.querySelector('#modal-pay .btn-primary');
            if (btn) {{
                btn.disabled = true;
                btn.innerHTML = '<span>⏳ ወደ ቦቱ በመላክ ላይ...</span>';
            }}
            if (b && uid) {{
                const url = '/api/select_book?uid=' + encodeURIComponent(uid) + '&book=' + encodeURIComponent(b.key) + '&mode=' + encodeURIComponent(activePayMode) + '&notify=1';
                try {{
                    await fetch(url, {{ keepalive: true, cache: 'no-store' }});
                }} catch (e) {{
                    console.error('select_book error:', e);
                }}
            }}
            setTimeout(() => {{
                _isReturningToBot = false;
                if (tg) tg.close();
                else closePayModal();
            }}, 150);
        }}

        // Initialize Store on Load
        loadUserBooks();
    </script>
</body>
</html>
'''

with open('webapp.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated new webapp.html! Size:", os.path.getsize('webapp.html'))
