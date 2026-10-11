import os, json

books_meta = {
    "narcissist": {
        "key": "narcissist",
        "title": "የናርሲሲስቶች ወጥመድ",
        "subtitle": "ከመርዛማ ግንኙነት የማምለጫ ጥበብ",
        "author": "ዶ/ር ራማኒ ዱርቫሱላ | ትርጉም፦ የአዕምሮ ምግቦች & Baya Books",
        "short_author": "ዶ/ር ራማኒ",
        "cover": "/static/covers/narcissist_trap.jpg",
        "pages": "274 ገጾች",
        "rating": "⭐ 4.9 (1.2k)",
        "badge": "🔥 በጣም ተነባቢ | 274 ገጾች",
        "badge_style": "",
        "category": "psychology",
        "data_url": "/static/books_data/narcissist_full.json",
        "paywall_desc": "የመጀመሪያዎቹን 3 ክፍሎች በነፃ አንብበዋል። ሙሉውን 274 ገጽ መጽሐፍ (ከምዕራፍ 2 እስከ 9) ለመክፈት እና ከመርዛማ ግንኙነት ራስዎን ነጻ ለማውጣት አሁኑኑ ያግኙ።"
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
        "paywall_desc": "የመጀመሪያዎቹን 3 ክፍሎች በነፃ አንብበዋል። ሙሉውን 216 ገጽ መጽሐፍ (ሁሉንም 15 ምዕራፎች) ለመክፈት እና በሕይወትዎ ጤናማ ድንበር ለማበጀት አሁኑኑ ያግኙ።"
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
        "paywall_desc": "የመግቢያ እና የምዕራፍ 1 ክፍሎችን በነፃ አንብበዋል። ሙሉውን 213 ገጽ መጽሐፍ (ሁሉንም 14 ምዕራፎች) ለመክፈት፣ ጊዜህን ለማስመለስና ገቢህን በእጥፍ ለማሳደግ አሁኑኑ ያግኙ።"
    }
}

books_meta_js = json.dumps(books_meta, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="am">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
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

        .brand {{ display: flex; align-items: center; gap: 10px; }}
        .brand-icon {{
            width: 34px; height: 34px; border-radius: 10px;
            background: var(--accent-gradient);
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
        }}
        .brand-text h1 {{ font-size: 16px; font-weight: 700; letter-spacing: -0.2px; }}
        .brand-text p {{ font-size: 11px; color: var(--text-muted); }}

        .btn-icon {{
            background: var(--bg-secondary); border: 1px solid var(--border);
            color: var(--text-primary); width: 36px; height: 36px;
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
            flex-shrink: 0; width: 112px; align-self: flex-start; border-radius: 10px;
            overflow: hidden; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.12); background: transparent;
        }}
        .book-cover {{ width: 100%; height: auto; object-fit: contain; display: block; }}

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
        }}
        body.light-theme .reader-header {{ background: rgba(248, 250, 252, 0.95); }}
        body.sepia-theme .reader-header {{ background: rgba(246, 239, 226, 0.95); }}

        .progress-bar-container {{ position: fixed; top: 0; left: 0; width: 100%; height: 3px; z-index: 100; }}
        .progress-bar-fill {{ height: 100%; width: 0%; background: var(--accent-gradient); transition: width 0.15s ease; }}

        .reader-top-title {{
            font-size: 13px; font-weight: 700; color: var(--text-primary);
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px;
        }}
        .reader-controls {{ display: flex; align-items: center; gap: 6px; }}

        /* Chapter Tabs Bar */
        .chapter-tabs {{
            display: flex; gap: 8px; padding: 12px 16px;
            background: var(--bg-secondary); border-bottom: 1px solid var(--border);
            overflow-x: auto; scrollbar-width: none; position: sticky; top: 57px; z-index: 55;
        }}
        .chapter-tabs::-webkit-scrollbar {{ display: none; }}
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
        }}

        .ch-header-card {{
            margin-bottom: 30px;
            padding-bottom: 22px;
            border-bottom: 2px solid var(--border);
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
            margin-bottom: 10px;
        }}
        .ch-main-subtitle {{
            font-size: 1.38em;
            font-weight: 800;
            line-height: 1.4;
            color: var(--text-primary);
        }}

        .reader-p {{
            margin-bottom: 1.35em;
            text-align: left;
            letter-spacing: 0.01em;
            word-spacing: 0.04em;
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
            padding: 18px 20px;
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
                <div class="brand-icon">📚</div>
                <div class="brand-text">
                    <h1>Baya Library</h1>
                    <p>ዲጂታል መጽሐፍት ቤት</p>
                </div>
            </div>
            <button class="btn-icon" onclick="toggleTheme()" title="Theme">🌓</button>
        </header>

        <div class="container">
            <div class="hero-banner">
                <div class="hero-tag">✨ የዕለቱ ምርጥ ስጦታ</div>
                <h2 class="hero-title">የዓለማችን ተፅዕኖ ፈጣሪ የስነ-ልቦና መጽሐፍት</h2>
                <p class="hero-desc">ጥልቅ ግንዛቤ፣ የተግባር መመሪያ እና የህይወት ለውጥ የሚያመጡ መጽሐፍትን በደቂቃዎች ውስጥ ያንብቡ።</p>
            </div>

            <!-- Dedicated My Books Section (Auto-shows when customer owns >= 1 book) -->
            <div id="my-books-section">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="font-size: 15px; font-weight: 800; color: #34d399; display: flex; align-items: center; gap: 6px;">
                        <span>📖 የኔ መጽሐፍት (My Purchased Books)</span>
                    </div>
                </div>
                <div class="book-list" id="my-books-list" style="margin-bottom: 0;"></div>
            </div>

            <!-- Filter Pills -->
            <div class="filter-scroll">
                <div class="filter-pill active" id="pill-all" onclick="filterCategory('all', this)">🔥 ሁሉም (All)</div>
                <div class="filter-pill" id="pill-mybooks" onclick="filterCategory('mybooks', this)">
                    <span>📖 የኔ መጽሐፍት</span>
                    <span class="count-badge" id="mybooks-count">0</span>
                </div>
                <div class="filter-pill" onclick="filterCategory('psychology', this)">🧠 ግንኙነት & ስነ-ልቦና</div>
                <div class="filter-pill" onclick="filterCategory('productivity', this)">⏱️ ጊዜ & ቢዝነስ</div>
            </div>

            <div class="section-header" id="catalog-header" style="margin-bottom: 12px; font-size: 15px; font-weight: 700;">
                <span>📚 የሚገኙ መጽሐፍት (Available Books)</span>
            </div>

            <!-- Dynamic Catalog List -->
            <div class="book-list" id="catalog-list"></div>

            <!-- Empty state when user taps 'My Books' tab but hasn't purchased any yet -->
            <div class="empty-mybooks" id="empty-mybooks">
                <div style="font-size: 36px; margin-bottom: 10px;">📚</div>
                <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 6px;">ገና የገዙት መጽሐፍ የለም</h3>
                <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">
                    ከመጽሐፍት መደብሩ ውስጥ የሚፈልጉትን መጽሐፍ በ 299 ብር ሲገዙ፣ ሙሉው መጽሐፍ እዚህ <b>«የኔ መጽሐፍት»</b> ስር ለዘላለም ይቀመጥልዎታል።
                </p>
                <button class="btn btn-primary" onclick="filterCategory('all', document.getElementById('pill-all'))">
                    <span>🔥 መጽሐፍትን ተመልከት</span>
                </button>
            </div>
        </div>
    </div>


    <!-- ══════════════════════════════════════════
         VIEW 2: PUBLICATION-GRADE READER
    ══════════════════════════════════════════ -->
    <div id="view-reader">
        <div class="reader-header">
            <button class="btn-icon" onclick="closeReader()" title="Back">‹</button>
            <div class="reader-top-title" id="readerBookTitle">የመጽሐፍ ርዕስ</div>
            <div class="reader-controls">
                <button class="btn-icon" onclick="adjustFontSize(-1)">A-</button>
                <button class="btn-icon" onclick="adjustFontSize(1)">A+</button>
                <button class="btn-icon" onclick="toggleTheme()">🌓</button>
            </div>
        </div>

        <!-- Chapter Switcher Bar -->
        <div class="chapter-tabs" id="chapterTabs"></div>

        <div class="reader-content" id="readerBody">
            <!-- Dynamic Chapter Content -->
            <div id="readerChapterContent"></div>

            <!-- Next / Previous Chapter Buttons -->
            <div class="ch-nav-footer" id="chapterNavFooter"></div>

            <!-- Paywall Card (shown on last free chapter if not owned) -->
            <div class="paywall-box" id="readerPaywall" style="display: none;">
                <div class="paywall-icon">🔒</div>
                <h3 class="paywall-title">ቀጣዮቹን ምዕራፎች ማንበብ ይፈልጋሉ?</h3>
                <p class="paywall-desc" id="paywallDesc"></p>
                <button class="btn btn-primary" style="width: 100%; padding: 13px; font-size: 14px;" onclick="openPayModal(activeBookKey)">
                    <span>💎 ሙሉውን መጽሐፍ በ 299 ብር ክፈት</span>
                </button>
            </div>
        </div>
    </div>


    <!-- ══════════════════════════════════════════
         MODAL: PAYMENT (299 Birr)
    ══════════════════════════════════════════ -->
    <div id="modal-pay" class="modal-overlay" onclick="closePayModal(event)">
        <div class="modal-card" onclick="event.stopPropagation()">
            <div class="modal-header" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                <h3 class="modal-title" id="modalBookTitle">📱 የክፍያ መረጃ — 299 ብር</h3>
                <button class="btn-icon" onclick="closePayModal()">✕</button>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 14px;">
                እባክዎ <b>299 ብር</b> በሚከተሉት አማራጮች ያስገቡ፦
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
                ✅ <b>ከከፈሉ በኋላ፦</b> የከፈሉበትን ደረሰኝ (Screenshot) በቀጥታ በቦቱ ላይ ይላኩልን። ሲስተማችን በሰከንዶች ውስጥ አረጋግጦ ሙሉውን መጽሐፍ <b>«📖 የኔ መጽሐፍት»</b> ውስጥ ይከፍትልዎታል!
            </div>

            <button class="btn btn-primary" style="width: 100%;" onclick="returnToBot()">
                <span>💬 ወደ ቦቱ ተመልሰህ ደረሰኝ ላክ</span>
            </button>
        </div>
    </div>


    <script>
        const WEBAPP_VERSION = "__WEBAPP_VERSION__";
        const BOOKS_META = {books_meta_js};
        const LOADED_CHAPTERS = {{}};
        let ownedBooks = [];
        let activeBookKey = 'narcissist';
        let activeChapterIdx = 0;
        let currentCategory = 'all';

        const tg = window.Telegram ? window.Telegram.WebApp : null;
        if (tg) {{ tg.ready(); tg.expand(); }}

        // Determine User ID from query param or Telegram WebApp initData
        function getUserId() {{
            const params = new URLSearchParams(window.location.search);
            if (params.get('uid')) return params.get('uid');
            if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) {{
                return String(tg.initDataUnsafe.user.id);
            }}
            return '';
        }}

        const USER_ID = getUserId();

        async function loadUserBooks() {{
            try {{
                const res = await fetch('/api/user_books?uid=' + encodeURIComponent(USER_ID) + '&_t=' + Date.now(), {{ cache: 'no-store' }});
                const data = await res.json();
                if (data && data.version && WEBAPP_VERSION !== '__WEBAPP_VERSION__' && data.version !== WEBAPP_VERSION) {{
                    const nextUrl = '/app?_v=' + encodeURIComponent(data.version) + (USER_ID ? '&uid=' + encodeURIComponent(USER_ID) : '');
                    window.location.replace(nextUrl);
                    return;
                }}
                if (data && Array.isArray(data.books)) {{
                    ownedBooks = data.books;
                }}
            }} catch (e) {{
                console.error('Error loading user books:', e);
            }}
            renderStore();
            if (document.getElementById('view-reader').style.display === 'block') {{
                renderChapter(activeChapterIdx);
            }}
        }}

        function createBookCardHTML(b, isOwned) {{
            const badgeHTML = isOwned
                ? `<div class="book-badge owned">✅ የተገዛ (ሙሉ መጽሐፍ) | ${{b.pages}}</div>`
                : `<div class="book-badge" style="${{b.badge_style}}">${{b.badge}}</div>`;

            const buttonsHTML = isOwned
                ? `<div class="btn-group">
                       <button class="btn btn-success" onclick="openReader('${{b.key}}', 0)">
                           <span>📖 ሙሉውን መጽሐፍ አንብብ</span>
                       </button>
                   </div>`
                : `<div class="btn-group">
                       <button class="btn btn-primary" onclick="openReader('${{b.key}}', 0)">
                           <span>📖 በነፃ አንብብ</span>
                       </button>
                       <button class="btn btn-outline" onclick="openPayModal('${{b.key}}')">
                           <span>💎 299 ብር</span>
                       </button>
                   </div>`;

            return `
                <div class="featured-card" data-category="${{b.category}}" data-owned="${{isOwned ? 'true' : 'false'}}">
                    <div class="book-cover-wrap" onclick="openReader('${{b.key}}', 0)" style="cursor:pointer;">
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
                        </div>
                        ${{buttonsHTML}}
                    </div>
                </div>
            `;
        }}

        function renderStore() {{
            document.getElementById('mybooks-count').innerText = ownedBooks.length;

            // Top My Books Highlight Box (shown on 'all' view when user owns at least 1 book)
            const mySection = document.getElementById('my-books-section');
            const myList = document.getElementById('my-books-list');
            if (ownedBooks.length > 0 && currentCategory === 'all') {{
                mySection.style.display = 'block';
                myList.innerHTML = ownedBooks
                    .filter(k => BOOKS_META[k])
                    .map(k => createBookCardHTML(BOOKS_META[k], true))
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
                filteredKeys = allKeys.filter(k => ownedBooks.includes(k));
                catalogHeader.innerHTML = '<span>📖 የገዟቸው መጽሐፍት (My Purchased Books)</span>';
            }} else if (currentCategory !== 'all') {{
                filteredKeys = allKeys.filter(k => BOOKS_META[k].category === currentCategory);
                catalogHeader.innerHTML = '<span>📚 የሚገኙ መጽሐፍት (Available Books)</span>';
            }} else {{
                catalogHeader.innerHTML = '<span>📚 ሁሉም መጽሐፍት (All Books)</span>';
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

        window.addEventListener('scroll', () => {{
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
            const bar = document.getElementById("readingProgress");
            if (bar) bar.style.width = scrolled + "%";
        }});

        async function openReader(bookKey, chIdx) {{
            activeBookKey = bookKey;
            const meta = BOOKS_META[bookKey];
            if (!meta) return;

            document.getElementById('readerBookTitle').innerText = meta.title;
            document.getElementById('paywallDesc').innerText = meta.paywall_desc;

            document.getElementById('view-home').style.display = 'none';
            document.getElementById('view-reader').style.display = 'block';

            if (!LOADED_CHAPTERS[bookKey]) {{
                document.getElementById('readerChapterContent').innerHTML = '<div style="text-align:center; padding: 60px 20px; color: var(--text-secondary);">⏳ መጽሐፉን በመክፈት ላይ...</div>';
                try {{
                    const res = await fetch(meta.data_url + '?_t=' + Date.now(), {{ cache: 'no-store' }});
                    LOADED_CHAPTERS[bookKey] = await res.json();
                }} catch (e) {{
                    document.getElementById('readerChapterContent').innerHTML = '<div style="text-align:center; padding: 60px 20px; color: #ef4444;">⚠️ መጽሐፉን መጫን አልተቻለም። እባክዎ እንደገና ይሞክሩ።</div>';
                    return;
                }}
            }}

            renderChapter(chIdx || 0);
        }}

        function renderChapter(idx) {{
            const chapters = LOADED_CHAPTERS[activeBookKey] || [];
            const isOwned = ownedBooks.includes(activeBookKey);
            const ch = chapters[idx];
            if (!ch) return;

            // If user clicked a locked chapter and doesn't own the book, trigger payment modal!
            if (!isOwned && !ch.free) {{
                openPayModal(activeBookKey);
                return;
            }}

            activeChapterIdx = idx;

            // Render Chapter Tabs
            const tabsEl = document.getElementById('chapterTabs');
            tabsEl.innerHTML = '';
            chapters.forEach((c, i) => {{
                const unlocked = isOwned || c.free;
                const btn = document.createElement('button');
                btn.className = 'ch-tab' + (i === idx ? ' active' : '') + (!unlocked ? ' locked' : '');
                btn.innerText = unlocked ? c.name : ('🔒 ' + c.label);
                btn.onclick = () => renderChapter(i);
                tabsEl.appendChild(btn);
            }});

            // Render Content Blocks
            const contentEl = document.getElementById('readerChapterContent');
            contentEl.innerHTML = '';

            const headerCard = document.createElement('div');
            headerCard.className = 'ch-header-card';
            const badge = document.createElement('div');
            badge.className = 'ch-badge';
            badge.innerText = ch.label;
            headerCard.appendChild(badge);

            let firstParaRendered = false;

            ch.blocks.forEach(b => {{
                if (b.type === 'subtitle') {{
                    const sub = document.createElement('h2');
                    sub.className = 'ch-main-subtitle';
                    sub.innerText = b.text;
                    headerCard.appendChild(sub);
                }} else if (b.type === 'quote') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const qBox = document.createElement('div');
                    qBox.className = 'reader-quote';
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
                    contentEl.appendChild(qBox);
                }} else if (b.type === 'h4') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const h4 = document.createElement('h4');
                    h4.className = 'reader-h4';
                    h4.innerText = b.text;
                    contentEl.appendChild(h4);
                }} else if (b.type === 'li') {{
                    if (headerCard.parentNode !== contentEl) contentEl.appendChild(headerCard);
                    const li = document.createElement('div');
                    li.className = 'reader-li';
                    li.innerHTML = `<span class="reader-li-dot">✦</span><div>${{b.text}}</div>`;
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
                    firstParaRendered = true;
                    p.innerText = b.text;
                    contentEl.appendChild(p);
                }}
            }});

            // Render Bottom Navigation
            const navFooter = document.getElementById('chapterNavFooter');
            navFooter.innerHTML = '';

            if (idx > 0) {{
                const prevBtn = document.createElement('button');
                prevBtn.className = 'btn btn-outline';
                prevBtn.style.padding = '13px';
                prevBtn.innerText = '← ' + chapters[idx - 1].label;
                prevBtn.onclick = () => renderChapter(idx - 1);
                navFooter.appendChild(prevBtn);
            }}

            const nextCh = chapters[idx + 1];
            if (nextCh && (isOwned || nextCh.free)) {{
                const nextBtn = document.createElement('button');
                nextBtn.className = 'btn btn-primary';
                nextBtn.style.padding = '13px';
                nextBtn.innerText = 'ቀጣይ፦ ' + nextCh.label + ' →';
                nextBtn.onclick = () => renderChapter(idx + 1);
                navFooter.appendChild(nextBtn);
                document.getElementById('readerPaywall').style.display = 'none';
            }} else if (!isOwned && nextCh && !nextCh.free) {{
                document.getElementById('readerPaywall').style.display = 'block';
            }} else {{
                document.getElementById('readerPaywall').style.display = 'none';
            }}

            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function closeReader() {{
            document.getElementById('view-reader').style.display = 'none';
            document.getElementById('view-home').style.display = 'block';
            window.scrollTo(0, 0);
        }}

        let currFontSize = 17.5;
        function adjustFontSize(delta) {{
            currFontSize = Math.min(24, Math.max(14, currFontSize + delta));
            document.getElementById('readerBody').style.fontSize = currFontSize + 'px';
        }}

        const themes = ['dark', 'light-theme', 'sepia-theme'];
        let themeIdx = 0;
        function toggleTheme() {{
            themeIdx = (themeIdx + 1) % themes.length;
            document.body.className = themes[themeIdx];
        }}

        function openPayModal(bookKey) {{
            const b = BOOKS_META[bookKey] || BOOKS_META[activeBookKey];
            if (b) {{
                document.getElementById('modalBookTitle').innerText = '📱 ' + b.title + ' — 299 ብር';
                if (USER_ID) {{
                    fetch('/api/select_book?uid=' + encodeURIComponent(USER_ID) + '&book=' + encodeURIComponent(b.key)).catch(() => {{}});
                }}
            }}
            document.getElementById('modal-pay').style.display = 'flex';
        }}
        function closePayModal() {{
            document.getElementById('modal-pay').style.display = 'none';
        }}
        function returnToBot() {{
            if (tg) tg.close();
            else closePayModal();
        }}

        // Initialize Store on Load & Auto-Refresh on Re-Focus / Visibility
        loadUserBooks();
        window.addEventListener('focus', loadUserBooks);
        document.addEventListener('visibilitychange', () => {{
            if (!document.hidden) loadUserBooks();
        }});
    </script>
</body>
</html>
'''

with open('webapp.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Generated new webapp.html! Size:", os.path.getsize('webapp.html'))
