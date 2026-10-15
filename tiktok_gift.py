"""
tiktok_gift.py — Daily Free Book Giveaway Game in collaboration with TikTok "የአዕምሮ ምግቦች"
Daily 5 free book winners from the library for first comers who guess the secret word announced on TikTok!
Cycle resets every morning at 10:00 AM EAT (ጠዋት 4:00 ሰዓት በኢትዮጵያ አቆጣጠር / UTC+3).
"""

from datetime import datetime, timezone, timedelta
import random
import database

# ══════════════════════════════════════════════════════════════════
#  CYCLE TIME MATH (Resets at 10:00 AM EAT / ጠዋት 4:00 ሰዓት)
# ══════════════════════════════════════════════════════════════════

def get_eat_now():
    """Returns current datetime in East Africa Time (UTC+3)."""
    return datetime.now(timezone.utc) + timedelta(hours=3)

def get_game_cycle_date():
    """
    Returns current game cycle date string 'YYYY-MM-DD'.
    The cycle resets daily at 10:00 AM (ጠዋት 4:00 ሰዓት በኢትዮጵያ አቆጣጠር / UTC+3).
    Times between 00:00 and 09:59 AM belong to the previous day's cycle.
    """
    eat_now = get_eat_now()
    if eat_now.hour < 10:
        cycle_dt = eat_now - timedelta(days=1)
    else:
        cycle_dt = eat_now
    return cycle_dt.strftime("%Y-%m-%d")

def get_next_reset_time_display():
    """Returns human-readable time remaining until next 10:00 AM (ጠዋት 4:00 ሰዓት) reset."""
    eat_now = get_eat_now()
    # Next reset is today at 10:00 AM if before 10am, else tomorrow at 10:00 AM
    if eat_now.hour < 10:
        next_reset = eat_now.replace(hour=10, minute=0, second=0, microsecond=0)
    else:
        next_reset = (eat_now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    diff = next_reset - eat_now
    total_seconds = max(0, int(diff.total_seconds()))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours} ሰዓት ከ {minutes} ደቂቃ"


# ══════════════════════════════════════════════════════════════════
#  POSITIVE AFFIRMATIONS & PSYCHOLOGICAL INSIGHTS BANK
# ══════════════════════════════════════════════════════════════════

WORD_AFFIRMATIONS = {
    "w_winner": {
        "word": "አሸናፊ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም አሸናፊ ነህ!",
        "body": (
            "ማሸነፍ ማለት ሁሌም አንደኛ መውጣት ወይም ያለ ስህተት መኖር ሳይሆን፣ በወደቅክበት ሁሉ መልሰህ ለመነሳት "
            "ድፍረት ማግኘት ነው። እስካሁን ያለፍክባቸውን ከባድ ፈተናዎች እና የልብ ስብራቶች አስባቸው — እነዚያ ሁሉ "
            "አላቆሙህም፤ ይልቁንም ይበልጥ ጠንካራ አድርገውሃል። ዛሬም አንተ በህይወት አለህ፣ ወደፊት እየተራመድክ ነው፣ "
            "እናም በራስህ ህይወት ላይ ታላቁ አሸናፊ አንተ ነህ።"
        )
    },
    "w_hero": {
        "word": "ጀግና ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም ጀግና ነህ!",
        "body": (
            "እውነተኛ ጀግንነት ማለት ፍርሃት አለመሰማት ሳይሆን፣ ፍርሃት እና ውስጣዊ ድካም እያለህም ወደፊት መጓዝ ነው። "
            "ማንም ሳያይህ በውስጥህ የታገልክባቸውን ከባድ ቀናት፣ እንባህን አብሰህ ለሰዎች ፈገግ ያልህባቸውን ምሽቶች አስታውስ። "
            "በራስህ ላይ ተስፋ ባለመቁረጥህ አንተ ለራስህ ህይወት ትልቁ ጀግና ነህ።"
        )
    },
    "w_beautiful": {
        "word": "ቆንጆ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም እጅግ ውብ እና ቆንጆ ነህ!",
        "body": (
            "እውነተኛ ውበት በመስታወት የሚታይ ቅርፅ ብቻ ሳይሆን፣ ከልብህ የሚፈልቀው ቅንነት፣ የነፍስህ ንፅህና እና "
            "ራስህን በክብር የመቀበልህ ውበት ነው። አንተ በዚህች አለም ላይ የተፈጠርከው በተለየ ድንቅ ስሪት ነው። "
            "ማንም ሰው የአንተን ቦታ ሊተካው አይችልም። ውበትህን እወቅ፣ በራስህ ተማመን!"
        )
    },
    "w_capable": {
        "word": "እችላለሁ",
        "title": "✨ አዎ! አንተ በእርግጥም ትችላለህ!",
        "body": (
            "የአዕምሮህ አቅም ከምታስበው በላይ እጅግ ሰፊ ነው። አሁን የገጠመህ ተራራ ትልቅ ቢመስልም፣ አንተ ግን "
            "ያንን ተራራ የመውጣት ውስጣዊ ብርታት አለህ። ጥርጣሬ የውሸት ስሜት ነው፤ እምነት ደግሞ እውነተኛ ሃይል ነው። "
            "ዛሬ የምትፈልገውን ለማሳካት የሚያስፈልግህ ሙሉ ጥንካሬ በውስጥህ አለ።"
        )
    },
    "w_worthy": {
        "word": "ይገባኛል",
        "title": "✨ አዎ! ለአንተ ደስታ፣ ሰላም እና ስኬት በእርግጥም ይገባሃል!",
        "body": (
            "በህይወትህ የደረሱብህ በደሎች ወይም ያለፉ ስህተቶችህ ዋጋህን አይቀንሱትም። አንተ ያለምንም ቅድመ-ሁኔታ "
            "እንክብካቤ፣ ፍቅር እና እውነተኛ ክብር የሚገባህ ውድ ሰው ነህ። ለራስህ ዝቅተኛ ግምት አትስጥ፤ የህይወት "
            "ምርጡ ነገር ሁሉ ለአንተ ይገባሃል።"
        )
    },
    "w_strong": {
        "word": "ብርቱ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም እጅግ ብርቱ ነህ!",
        "body": (
            "ብርታትህ የሚመነጨው በህይወትህ ማዕበል ውስጥ ሁሉ ፀንተህ በመቆምህ ነው። ነፋሱ ሲበረታ እንዳትወድቅ "
            "ያደረገህ ጥልቅ የውስጥ ጥንካሬ አለህ። ድካም ቢሰማህ እንኳን ይህ ጊዜያዊ ነው፤ ብርታትህ ግን ሁሌም ከጎንህ ነው።"
        )
    },
    "w_free": {
        "word": "ነፃ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም ነፃ ነህ!",
        "body": (
            "የሰዎች ወሬ፣ ያለፈው ታሪክህ፣ ወይም የሌሎች ሰዎች ፍርድ በአንተ ላይ ስልጣን የላቸውም። ህይወትህን "
            "በራስህ ፍላጎት፣ በራስህ ምርጫ እና በፈጣሪህ ፍቃድ የመምራት ሙሉ ነፃነት አለህ። ከአሉታዊ አስተሳሰብ "
            "ዛሬ ራስህን ነፃ አውጥተሃል።"
        )
    },
    "w_hopeful": {
        "word": "ተስፈኛ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም ባለ ሙሉ ተስፋ ነህ!",
        "body": (
            "ተስፋ ማለት በጨለማው መሃል የንጋቱን ብርሃን ማየት መቻል ነው። ነገ ዛሬ አይደለም፤ ነገ አዳዲስ በሮች፣ "
            "አዳዲስ እድሎች እና ያልታሰቡ በረከቶች ይዞልህ ይመጣል። በልብህ ውስጥ ያለው የተስፋ ጭላንጭል ነገ ትልቅ "
            "ፋና ሆኖ ያበራል።"
        )
    },
    "w_patient": {
        "word": "ታጋሽ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም ታጋሽ ነህ!",
        "body": (
            "ትዕግስት ዝም ብሎ መቀመጥ ሳይሆን፣ ጊዜው ሲደርስ የሚዘራው ሁሉ እንደሚያፈራ በፅናት ማመን ነው። "
            "በህይወትህ የምትመኘው ትልቅ ነገር ሁሉ በጊዜ ሂደት በጥበብ ይገነባል። ትዕግስትህ ወደማይናወጥ ታላቅ ስኬት እየመራህ ነው።"
        )
    },
    "w_god_with_me": {
        "word": "ፈጣሪ ከኔ ጋር ነው",
        "title": "✨ አዎ! ፈጣሪ ሁልጊዜም ከአንተ ጋር ነው!",
        "body": (
            "ማንም በተወህ፣ ዓለም ሁሉ ጀርባውን በሰጠህ ሰዓት እንኳን እርሱ ፈጽሞ አይጥልህም። ብቻህን አይደለህም፤ "
            "በምትሄድበት መንገድ ሁሉ ጥበቃው፣ ምህረቱ እና ሰላሙ ከአንተ ጋር አለ። ልብህን አሳርፈው፣ ከእርሱ ጋር ሁሉ ነገር ይቻላል።"
        )
    },
    "w_forgiving": {
        "word": "ይቅር ባይ ነኝ",
        "title": "✨ አዎ! አንተ ይቅር ባይ እና ልበ-ሰፊ ነህ!",
        "body": (
            "ይቅርታ ማድረግ ሰዎችን ከጥፋታቸው ነፃ ማውጣት ሳይሆን፣ ራስህን ከቂም እና ከክብደት ሰንሰለት ነፃ ማውጣት ነው። "
            "ቂምን ስትተው ልብህ በሰላም ይሞላል። ዛሬ ራስህን እና ሌሎችን ይቅር በማለት ወደ ታላቅ መንፈሳዊ ከፍታ ተሸጋግረሃል።"
        )
    },
    "w_loved": {
        "word": "ተወዳጅ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም እጅግ ተወዳጅ ነህ!",
        "body": (
            "ምናልባት በአካባቢህ ካሉ ሰዎች ፍቅር አጥተህ ይሆናል፣ ነገር ግን የአንተ መኖር ለዚህች አለም ትልቅ ስጦታ ነው። "
            "አንተን የሚወድህ፣ የሚያደንቅህ እና ለአንተ የሚጨነቅ ታላቅ ሃይል አለ። የፍቅር ምንጭ በውስጥህ አለ።"
        )
    },
    "w_blessed": {
        "word": "የተባረክሁ ነኝ",
        "title": "✨ አዎ! አንተ በእርግጥም የተባረክህ ሰው ነህ!",
        "body": (
            "ዛሬ በህይወት መኖርህ፣ የምትተነፍሰው አየር፣ አዕምሮህ እና በውስጥህ ያሉ ድብቅ ተሰጥኦዎች ታላቅ በረከቶች ናቸው። "
            "በረከትህን ስታይ ይበልጥ ይበዛልሃል። ዛሬ በአንተ ዙሪያ ያሉ በጎ ነገሮችን በምስጋና ተመልከታቸው።"
        )
    },
    "w_wise": {
        "word": "አስተዋይ ነኝ",
        "title": "✨ አዎ! አንተ ጥልቅ አእምሮ ያለህ አስተዋይ ሰው ነህ!",
        "body": (
            "ከስህተቶችህ ተምረሃል፣ ከህይወት ውጣ ውረዶች ጥበብን ቀስመሃል። ውሳኔዎችህን በብስለት የምትወስንበት፣ "
            "እውነተኛውን ከውሸቱ የምትለይበት ልዩ ማስተዋል አለህ። በውስጣዊ ድምፅህ እመን።"
        )
    },
    "w_peaceful": {
        "word": "ሰላማዊ ነኝ",
        "title": "✨ አዎ! በውስጥህ ማንም ሊነጥቀው የማይችል ታላቅ ሰላም አለ!",
        "body": (
            "ውጫዊው አለም ቢረበሽም፣ የአንተ ውስጣዊ መረጋጋት ግን የፀና ነው። ጭንቀትን አስወግድ፤ በጥልቀት ተንፍስ። "
            "ሰላም ምርጫ ነው፣ አንተም ዛሬ ሰላምን መርጠሃል።"
        )
    },
    "w_unique": {
        "word": "ልዩ ነኝ",
        "title": "✨ አዎ! አንተ በዚህች ዓለም ላይ ተወዳዳሪ የሌለህ ልዩ ሰው ነህ!",
        "body": (
            "በቢሊዮን ከሚቆጠሩ ሰዎች መሃል እንደ አንተ ያለ ማንም የለም። የጣት አሻራህ፣ የልብህ ስሜት እና የአስተሳሰብህ ቅኝት "
            "ሙሉ በሙሉ ልዩ ነው። ዓለም የአንተን ልዩ ስጦታ ትፈልገዋለች። ራስህን ከማንም ጋር አታወዳድር።"
        )
    },
    "w_fortunate": {
        "word": "እድለኛ ነኝ",
        "title": "✨ አዎ! አንተ በብዙ መልኩ እጅግ እድለኛ ነህ!",
        "body": (
            "እድል ማለት ዝም ብሎ የሚመጣ ሳይሆን፣ በአዎንታዊ አይን ለሚመለከት ሰው በየቀኑ የሚከፈት በር ነው። "
            "በህይወትህ ያገኘሃቸው ትምህርቶች እና አጋጣሚዎች ሁሉ ለትልቅ ከፍታ እያዘጋጁህ ነው። መልካም ነገር ሁሌም ወደ አንተ እየሳበ ነው።"
        )
    },
    "w_never_give_up": {
        "word": "አልሸነፍም",
        "title": "✨ አዎ! አንተ ፈጽሞ የማትሸነፍ ብርቱ ሰው ነህ!",
        "body": (
            "ማዕበል ሊመታህ፣ መሬት ሊንቀጠቀጥ ይችላል፤ አንተ ግን አትሰበርም። የውድቀትህ ብዛት ሳይሆን የመነሳትህ ፅናት "
            "ነው ማንነትህን የሚወስነው። ዛሬም ቆመሃል፤ ነገም ታሸንፋለህ።"
        )
    },
    "w_precious": {
        "word": "ውድ ነኝ",
        "title": "✨ አዎ! የአንተ ዋጋ በማንም ሰው ሚዛን የማይለካ ውድ ነው!",
        "body": (
            "የሰው ልጅ ዋጋ በገንዘብ፣ በልብስ ወይም በሌሎች ሰዎች አድናቆት አይለካም። አንተ በፈጣሪ እጅ የተሰራህ፣ "
            "በዋጋ የማትተመን ውድ ፍጥረት ነህ። ማንም ሰው ዋጋህን ሊያሳጣው አይችልም።"
        )
    },
    "w_voice": {
        "word": "ተደማጭ ነኝ",
        "title": "✨ አዎ! የአንተ ድምፅ እና መኖር ትልቅ ዋጋ አለው!",
        "body": (
            "የምትናገረው ቃል፣ የምታሳየው ፍቅር እና በውስጥህ ያለው ሀሳብ ሰዎችን የመለወጥ ሃይል አለው። "
            "ዝም አትበል፤ ድምፅህን በቅንነት እና በእውነት አሰማ። ዓለም አንተን ለማዳመጥ ዝግጁ ናት።"
        )
    },
    "w_wonderfully_made": {
        "word": "ፈጣሪ ልዩ አድርጎ ፈጥሮኛል",
        "title": "✨ አዎ! ፈጣሪ አንተን ልዩ እና ድንቅ አድርጎ ፈጥሮሃል!",
        "body": (
            "የፈጣሪ እጅ በአንተ ህይወት ላይ ታላቅ አሻራ አሳርፏል። የተፈጠርከው ለታላቅ አላማ፣ ለበረከት እና ለብርሃን ነው። "
            "በአንተ ውስጥ የተተከለው ልዩ ችሎታ በጊዜው ያብባል፤ ፈጣሪህን እመነው።"
        )
    },
    "w_true_to_self": {
        "word": "ለራሴ ታማኝ ነኝ",
        "title": "✨ አዎ! አንተ ለራስህ እውነተኛ እና ታማኝ ነህ!",
        "body": (
            "ሌሎችን ለማስደሰት ስትል ራስህን አትሰውም። የራስህን እሴቶች፣ የውስጥህን እውነት እና ስሜትህን ታከብራለህ። "
            "ለራስህ እውነተኛ ስትሆን መላው ህይወትህ በታላቅ ቅንነት እና ሰላም ይሞላል።"
        )
    },
    "w_new_person": {
        "word": "አዲስ ሰው ነኝ",
        "title": "✨ አዎ! ዛሬ አንተ አዲስ እና ዳግም የበቀልክ ሰው ነህ!",
        "body": (
            "ያለፈው ትላንት አብቅቷል። ዛሬ አዲስ ቀን፣ አዲስ ገፅ፣ አዲስ እድል ነው። ያለፈውን ሸክም አራግፈህ ጣል፤ "
            "ዛሬ የተሻለውን ራስህን የምትፈጥርበት ድንቅ የጅማሮ ቀንህ ነው።"
        )
    },
    "w_self_love": {
        "word": "እራሴን እወዳለሁ",
        "title": "✨ አዎ! ራስህን ያለምንም ቅድመ-ሁኔታ መውደድ ጀምረሃል!",
        "body": (
            "ራስህን መውደድ ራስ ወዳድነት ሳይሆን፣ ለሌሎች ፍቅር ለመስጠት የሚያስፈልግህ የመጀመሪያው መሰረት ነው። "
            "ድክመቶችህን እና ጥንካሬዎችህን በሙሉ በይቅርታ እና በእቅፍ ተቀበል። ራስህን ስትወደው አለምም ትወድሃለች።"
        )
    }
}


# ══════════════════════════════════════════════════════════════════
#  SECRET WORD & CHOICES LOGIC
# ══════════════════════════════════════════════════════════════════

def get_word_by_key(key):
    """Returns word item dict for a key."""
    return WORD_AFFIRMATIONS.get(key)

def find_key_by_word(word_text):
    """Finds word key matching word text."""
    if not word_text:
        return None
    wt = word_text.strip()
    for k, v in WORD_AFFIRMATIONS.items():
        if v["word"] == wt:
            return k
    return None

def get_today_secret_word():
    """
    Retrieves the current cycle's secret word.
    If not set manually by Admin for this cycle, auto-selects a stable word based on cycle date.
    """
    cycle_date = get_game_cycle_date()
    saved_word = database.get_setting("daily_gift_secret_word")
    saved_date = database.get_setting("daily_gift_secret_word_date")

    if saved_date == cycle_date and saved_word:
        return saved_word

    # Auto-seed a word deterministically from the bank based on date hash
    all_keys = sorted(list(WORD_AFFIRMATIONS.keys()))
    date_hash = sum(ord(c) for c in cycle_date)
    seeded_key = all_keys[date_hash % len(all_keys)]
    seeded_word = WORD_AFFIRMATIONS[seeded_key]["word"]

    database.set_setting("daily_gift_secret_word", seeded_word)
    database.set_setting("daily_gift_secret_word_date", cycle_date)
    return seeded_word

def set_today_secret_word(word_text):
    """Sets today's secret word (used by Admin to match TikTok video)."""
    cycle_date = get_game_cycle_date()
    database.set_setting("daily_gift_secret_word", word_text.strip())
    database.set_setting("daily_gift_secret_word_date", cycle_date)

def get_today_choices():
    """
    Generates 4 distinct choices for today:
    1 correct secret word + 3 randomized distractors from the bank.
    Returns list of tuples: [(key, word_text), ...] shuffled.
    """
    secret_word = get_today_secret_word()
    secret_key = find_key_by_word(secret_word)
    if not secret_key:
        secret_key = "w_custom"
    
    other_keys = [k for k in WORD_AFFIRMATIONS.keys() if k != secret_key]
    
    # Deterministic sample based on user cycle date so choices don't jump around
    cycle_date = get_game_cycle_date()
    rnd = random.Random(cycle_date + "_choices")
    distractors = rnd.sample(other_keys, min(3, len(other_keys)))
    
    choices = [(secret_key, secret_word)]
    for dk in distractors:
        choices.append((dk, WORD_AFFIRMATIONS[dk]["word"]))
    
    # Shuffle stably for this cycle
    rnd.shuffle(choices)
    return choices

def get_tiktok_channel_url():
    """Returns the brother's TikTok account URL."""
    return database.get_setting("daily_gift_tiktok_url", "https://www.tiktok.com/@yeaemromgboch")

def get_tiktok_channel_name():
    """Returns the brother's TikTok account name."""
    return database.get_setting("daily_gift_tiktok_name", "የአዕምሮ ምግቦች")
