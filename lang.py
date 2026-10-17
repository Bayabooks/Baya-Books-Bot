# lang.py — Multi-language strings for Baya Psychology Bot
# Languages: am=Amharic, en=English, ti=Tigrinya, om=Afaan Oromoo
# Strict Rule: No language in another language (Pure vocabulary per language)

STRINGS = {
    "lang_select_prompt": {
        "am": "🌍 <b>እባክዎ ቋንቋዎን ይምረጡ</b>",
        "en": "🌍 <b>Please choose your language</b>",
        "ti": "🌍 <b>በጃኹም ቋንቋኹም ምረጹ</b>",
        "om": "🌍 <b>Maaloo afaan keessan filadhaa</b>"
    },
    
    "join_channel_title": {
        "am": "📢 <b>ቦቱን ለመጠቀም በመጀመሪያ ቻናላችንን ይቀላቀሉ!</b>",
        "en": "📢 <b>Please join our channel first to use the bot!</b>",
        "ti": "📢 <b>ነዚ ቦት ንምጥቃም ቅድም ብትሕትና ቻናልና ተጸንበሩ!</b>",
        "om": "📢 <b>Bootii kana fayyadamuuf dursitanii chaanaalii keenyatti makamaa!</b>"
    },
    "join_channel_hint": {
        "am": "👇 ከታች ያለውን ይጫኑ",
        "en": "👇 Click below",
        "ti": "👇 ኣብ ታሕቲ ዘሎ ጠውቑ",
        "om": "👇 Isa armaan gadii tuqaa"
    },
    "join_channel_btn": {
        "am": "📢 ቻናሉን ተቀላቀል",
        "en": "📢 Join Channel",
        "ti": "📢 ቻናል ተጸንበር",
        "om": "📢 Chaanaalii Makami"
    },
    "joined_check_btn": {
        "am": "✅ ተቀላቅያለሁ",
        "en": "✅ I've Joined",
        "ti": "✅ ተጸንቢረ ኣለኹ",
        "om": "✅ Makameera"
    },
    "joined_success": {
        "am": "✅ ተቀላቅለዋል!",
        "en": "✅ You have successfully joined!",
        "ti": "✅ ብዓወት ተጸንቢርኩም!",
        "om": "✅ Milkiin makamtaniittu!"
    },
    "joined_fail": {
        "am": "❌ ገና አልተቀላቀሉም!",
        "en": "❌ You haven't joined yet!",
        "ti": "❌ ዛጊት ኣይተጸንበርኩምን!",
        "om": "❌ Amma iyyuu hin makamne!"
    },

    "onboard_privacy": {
        "am": "🔒 ውይይታችን 100% ሚስጥራዊ ነው። መረጃዎን በ '👤 የእኔ ገፅ' ውስጥ በፈለጉት ጊዜ ማጽዳት ይችላሉ።",
        "en": "🔒 Our conversation is 100% confidential. You can clear your data anytime from 👤 My Page.",
        "ti": "🔒 ዕላልና 100% ምስጢራዊ እዩ። ሓበሬታኹም ኣብ ዝኾነ እዋን ካብ 👤 ገጸይ ምጽራይ ትኽእሉ ኢኹም።",
        "om": "🔒 Marii keenya 100% iccitii dha. Odeeffannoo keessan yeroo kamiyyuu 👤 Fuula koo irraa haquu dandeessu."
    },
    "onboard_age_gender_prompt": {
        "am": "🔒 በዚህ 100% ሚስጥራዊ በሆነ የውይይት ገፅ፣ ይህ AI ሰዎችን ለማስደሰት አይሞክርም። መስማት የሚፈልጉትን ሳይሆን፣ <b>አሁን ላይ ሊሰሙት የሚገባዎትን እውነት</b> ነው የሚነግርዎት።\n\nውይይታችንን ለመጀመር...\n<b>እባክዎ ጾታዎን ይምረጡ 👇</b>\n<i>(ዕድሜያቸው ከ18 ዓመት በላይ ለሆኑ ብቻ)</i>",
        "en": "🔒 In this 100% confidential space, this AI doesn't try to please anyone. It won't tell you what you want to hear, but <b>the truth you need to hear right now</b>.\n\nTo start our conversation...\n<b>Please select your gender 👇</b>\n<i>(For adults 18+ only)</i>",
        "ti": "🔒 ኣብዚ 100% ምስጢራዊ ዝኾነ ዕላል፡ እዚ AI ንሰባት ንምሕጓስ ኣይፍተንን እዩ። ክትሰምዖ ዝደለኻዮ ሳይኮን፡ <b>ሕጂ ክትሰምዖ ዝግባእ ሓቂ</b> እዩ ዝነግረካ።\n\nዕላልና ንምጅማር...\n<b>በጃኹም ጾታኹም ምረጹ 👇</b>\n<i>(ካብ 18 ዓመት ንላዕሊ ጥራይ)</i>",
        "om": "🔒 Marii 100% iccitii ta'e kana keessatti, AI kun namoota gammachiisuuf hin yaalu. Waan dhagahuu barbaaddu osoo hin taane, <b>dhugaa ammaa dhagahuu qabdu</b> sitti hima.\n\nMarii keenya jalqabuuf...\n<b>Maaloo saala keessan filadhaa 👇</b>\n<i>(Waggaa 18 ol qofaaf)</i>"
    },
    "onboard_age_btn": {
        "am": "✅ ዕድሜዬ ከ18 ዓመት በላይ ነው",
        "en": "✅ I am over 18 years old",
        "ti": "✅ ኣነ ልዕሊ 18 ዓመት እየ",
        "om": "✅ Ani waggaa 18 oli"
    },
    "onboard_gender_prompt": {
        "am": "እባክዎ ጾታዎን ይምረጡ (ለአነጋገር እንዲመች):",
        "en": "Please select your gender (to tailor our conversation):",
        "ti": "በጃኹም ጾታኹም ምረጹ (ንኣዘራርባ ምእንቲ ክጥዕም):",
        "om": "Maaloo saala keessan filadhaa (haasaa keenyaaf akka mijatutti):"
    },
    "onboard_skip_btn": {
        "am": "⚡ ዝለል እና ቀጥታ ጀምር",
        "en": "⚡ Skip & Start Now",
        "ti": "⚡ ሕለፎ እሞ ብቐጥታ ጀምር",
        "om": "⚡ Utaliitii Kallattiin Jalqabi"
    },
    "autofree_welcome": {
        "am": "👋 <b>እንኳን ወደ ባያ ቡክስ በደህና መጡ!</b>\n<i>(የታችኛው ዋና ሜኑ ተከፍቶልዎታል፤ ጥያቄዎን በማስተናገድ ላይ ነኝ...)</i>",
        "en": "👋 <b>Welcome to Baya Books!</b>\n<i>(Your main menu is unlocked below; processing your question...)</i>",
        "ti": "👋 <b>ናብ ባያ ቡክስ ብደሓን መጻእኹም!</b>\n<i>(ናይ ታሕቲ ቀንዲ ሜኑ ተኸፊቱልኩም ኣሎ፤ ንሕቶኹም እናተቐበልኩ እየ...)</i>",
        "om": "👋 <b>Gara Baya Books tti baga nagaan dhuftan!</b>\n<i>(Meeun gadii banameera; gaaffii keessan qophaa'aa jira...)</i>"
    },
    "gender_male": {
        "am": "👨 ወንድ",
        "en": "👨 Male",
        "ti": "👨 ተባዕታይ",
        "om": "👨 Dhiira"
    },
    "gender_female": {
        "am": "👩 ሴት",
        "en": "👩 Female",
        "ti": "👩 ኣንስተይቲ",
        "om": "👩 Dubartii"
    },
    "gender_confirm_title": {
        "am": "🔍 <b>የጾታ ማረጋገጫ</b>",
        "en": "🔍 <b>Gender Confirmation</b>",
        "ti": "🔍 <b>ናይ ጾታ ምርግጋጽ</b>",
        "om": "🔍 <b>Mirkaneessa Saalaa</b>"
    },
    "gender_confirm_body": {
        "am": "በመልዕክትዎ ውስጥ የጾታ ለውጥ አስተውያለሁ። የ AI አማካሪው ለእርስዎ በሚስማማ አነጋገር እና ትክክለኛ ምክር እንዲያናግርዎት፣ እባክዎ ጾታዎን ያረጋግጡ፦",
        "en": "I noticed a change in gender reference in your message. To ensure the AI counselor addresses you properly and provides accurate guidance, please confirm your gender:",
        "ti": "ኣብ መልእኽትኹም ናይ ጾታ ለውጢ ኣስተብሂለ ኣለኹ። እቲ ናይ AI ኣማኻሪ ብትክክለኛ ኣዘራርባ ክዛረበኩምን ግቡእ ምኽሪ ክህበኩምን፡ በጃኹም ጾታኹም ኣረጋግጹ፦",
        "om": "Ergaa keessan keessatti jijjiirama saalaa hubadheera. Gorsaan AI akkaataa sirriin akka isin haasofsiisuuf fi gorsa sirrii akka isiniif kennuuf, maaloo saala keessan mirkaneessaa:"
    },
    "gender_updated_alert": {
        "am": "✅ ጾታ ተስተካክሏል",
        "en": "✅ Gender updated",
        "ti": "✅ ጾታ ተኣሪሙ ኣሎ",
        "om": "✅ Saalli sirreeffameera"
    },
    "gender_updated_msg": {
        "am": "✅ <b>ጾታዎ ወደ {gender} ተስተካክሏል!</b>\n\nአሁን ውይይታችንን መቀጠል እንችላለን። እባክዎ ጥያቄዎን ወይም ሀሳብዎን ይቀጥሉ 👇",
        "en": "✅ <b>Your gender has been updated to {gender}!</b>\n\nWe can now continue our session. Please continue sharing your thoughts 👇",
        "ti": "✅ <b>ጾታኹም ናብ {gender} ተኣሪሙ ኣሎ!</b>\n\nሕጂ ዕላልና ክንቅጽል ንኽእል ኢና። በጃኹም ሓሳብኩም ወይ ሕቶኹም ቀጽሉ 👇",
        "om": "✅ <b>Saalli keessan gara {gender} tti sirreeffameera!</b>\n\nAmma marii keenya itti fufuu ni dandeenya. Maaloo yaada keessan itti fufaa 👇"
    },

    "welcome_text": {
        "am": "<b>ሰላም {name}። ወደ ባያ ቡክስ በደህና መጡ!</b>\n\nእኔ እዚህ ያለሁት እርስዎ መስማት የሚፈልጉትን ልነግርዎት አይደለም። እኔ ወደ ኋላ የሚጎትቱዎትን ድብቅ አስተሳሰቦች እና ልማዶች እንዲሰብሩ የምረዳዎት የኤአይ (AI) የስነ-ልቦና አማካሪ ነኝ። ያለምንም ፍርድ አዳምጥዎታለሁ፤ እውነተኛውን ለውጥ ለማምጣት ግን እውነታውን ፊት ለፊት እንነጋገራለን።\n\n🎁 <b>ቦቱ ላይ የሚያገኟቸው ልዩ ጥቅሞች እና ስጦታዎች፦</b>\n• <b>🎁 የዕለቱ ነፃ መጽሐፍ ስጦታ፡</b> በየቀኑ በቲክቶክ የሚለቀቀውን ሚስጥራዊ ቃል በመመለስ በነፃ መጽሐፍ ወይም 25 ነፃ መልዕክቶችን ይሸለሙ!\n• <b>💰 ጓደኛ ጋብዘው ገንዘብ ያግኙ፡</b> የራስዎን መጋበዣ ሊንክ ለጓደኞች በማጋራት የ <b>30% ፈጣን ኮሚሽን</b> ያግኙ፤ በቀላሉ በቴሌብር ወይም በንግድ ባንክ ያውጡ!\n• <b>📚 የዲጂታል ቤተ-መጽሐፍት፡</b> ከታች '📚 የኔ መጻሕፍት' የሚለውን በመጫን ምርጥ የስነ-ልቦና እና የህይወት መጻሕፍትን በማንኛውም ሰዓት ማንበብ ይችላሉ።\n\n💡 <b>እስኪ በቀጥታ ወደ ውይይታችን እንግባ... አሁን ላይ ውስጠዎን እየበላው፣ ግን ደግሞ ሆን ብለው እየሸሹት ያለው ትልቁ ነገር ምንድን ነው?</b> (በነፃነት ፅፈው ይላኩልኝ...)",
        "en": "<b>Welcome, {name}! Welcome to Baya Books.</b>\n\nI am not here to tell you what you want to hear. I am a psychological strategist and AI counselor designed to help you decode the patterns keeping you stuck. I will listen without judgment, but I will also tell you the fierce truths you might be avoiding.\n\n🎁 <b>Exclusive Perks & Opportunities on this Bot:</b>\n• <b>🎁 Daily Free Book Giveaway:</b> Crack the daily secret word from TikTok to win free full books or 25 free messages!\n• <b>💰 Invite Friends & Earn Cash:</b> Share your referral link and earn an instant <b>30% cash commission</b>, withdrawable via Telebirr or CBE Bank!\n• <b>📚 In-App Digital Library:</b> Tap '📚 My Books' below to explore and read premier psychology and personal growth titles anytime.\n\n💡 <b>Now, let's get straight to work... What is the one major issue currently weighing on you that you've been avoiding?</b> (Feel free to write to me below...)",
        "ti": "<b>ሰላም {name}። ናብ ባያ ቡክስ ብደሓን መጻእኹም!</b>\n\nኣነ ንንድሕሪት ዝስሕቡኹም ሕቡኣት ኣተሓሳስባታትን ልምድታትን ንክትሰብሩ ዝሕግዝ ናይ AI ስነ-ኣእምሮ ኣማኻሪ እየ። ብዘይ ገለ ፍርዲ ክሰምዓኩም እየ፤ ናይ ብሓቂ ለውጢ ንምምጻእ ድማ ነቲ ሓቂ ገጽ ንገጽ ክንዛረበሉ ኢና።\n\n🎁 <b>ኣብዚ ቦት ዝረኽብዎም ፍሉያት ረብሓታትን ሽልማታትን፦</b>\n• <b>🎁 ናይ ሎሚ ነጻ መጽሓፍ ሽልማት፡</b> መዓልታዊ ኣብ ቲክቶክ ዝልቀቕ ምስጢራዊ ቃል ብምምላስ ነጻ መጽሓፍ ወይ 25 ናጻ መልእኽትታት ተሸለሙ!\n• <b>💰 መሓዛኹም ዓዲምኩም ገንዘብ ርኸቡ፡</b> ናይ ምዕዳም መላግቦኹም ንመሓዙትኩም ብምክፋል <b>30% ቅጽበታዊ ኮሚሽን</b> ርኸቡ፤ ብቴሌብር ወይ ንግዲ ባንክ ብቐሊሉ ኣውጽኡ!\n• <b>📚 ናይ መጻሕፍቲ ቤት፡</b> ኣብ ታሕቲ ዘሎ '📚 ናተይ መጻሕፍቲ' ብምጥዋቕ ዝበለጹ ናይ ስነ-ልቦና መጻሕፍቲ ኣብ ዝኾነ ሰዓት ከተንብቡ ትኽእሉ ኢኹም።\n\n💡 <b>እስኪ ብቐጥታ ናብ ጉዳይና ንእቶ... ሕዚ ንውሽጥኹም እናበልዖ፡ ግን ድማ ብፍላጥ ትሃድሙሉ ዘለኹም ዓቢ ነገር እንታይ እዩ?</b> (ብነጻነት ጽሒፍኩም ስደዱለይ...)",
        "om": "<b>Baga nagaan dhuftan {name}! Gara Baya Books tti baga nagaan dhuftan.</b>\n\nAni ilaalcha fi amala duubatti si harkisan akka cabsitu kan si gargaaru gorsaa xiin-sammuu AI ti. Osoo sitti hin murteessin sin dhaggeeffadha; jijjiirama dhugaa fiduuf garuu dhugaa ifatti waliin haasofna.\n\n🎁 <b>Faayidaalee fi Badhaasota Boottii kana irraa argattan:</b>\n• <b>🎁 Badhaasa Kitaaba Har'aa:</b> Jecha iccitii TikTok irraa deebisuun kitaaba bilisaa ykn ergaawwan 25 bilisaan badhaafamaa!\n• <b>💰 Hiriyyaa Afeeraa Maallaqa Argadhaa:</b> Liinkii keessan hiriyyootaaf qooduun <b>komishinii 30% battalumatti</b> argadhaa; Telebirr ykn Baankii Daldalaatiin salphaatti baafadhaa!\n• <b>📚 Mana Dubbisaa Dijitaalaa:</b> Asumaan '📚 Kitaabota Koo' kan jedhu tuquun kitaabota xiin-sammuu filatamoo yeroo hunda dubbisuu dandeessu.\n\n💡 <b>Mee kallattiin gara dhimma keenyaatti haa gallu... Wanti yeroo ammaa kana keessa kee nyaachaa jiru, garuu immoo beekaa jalaa baqachaa jirtu inni guddaan maali?</b> (Bilisummaan barreessii naaf ergi...)"
    },

    "menu_daily_gift": {
        "am": "🎁 የዕለቱ ነፃ መጽሐፍ",
        "en": "🎁 Today's Free Book Gift",
        "ti": "🎁 ናይ ሎሚ ነጻ መጽሓፍ",
        "om": "🎁 Kennaa Kitaaba Har'aa"
    },
    "menu_continue": {
        "am": "🧠 ምክክራችንን እንቀጥል",
        "en": "🧠 Continue Chat",
        "ti": "🧠 ምይይጥና ንቐጽል",
        "om": "🧠 Marii keenya itti haa fufnu"
    },
    "menu_mypage": {
        "am": "👤 የእኔ ገፅ",
        "en": "👤 My Page",
        "ti": "👤 ገጸይ",
        "om": "👤 Fuula koo"
    },
    "menu_invite": {
        "am": "🎁 ጓደኛ ይጋብዙ",
        "en": "🎁 Invite Friend",
        "ti": "🎁 መሓዛ ዕደሙ",
        "om": "🎁 Hiriyyaa afeeraa"
    },
    "menu_support": {
        "am": "☕ ቡድናችንን ያበረታቱ",
        "en": "☕ Support Team",
        "ti": "☕ ጉጅለና ኣበራትዑ",
        "om": "☕ Garee jajjabeessaa"
    },
    "menu_lang": {
        "am": "🌐 ቋንቋ ቀይር",
        "en": "🌐 Change Language",
        "ti": "🌐 ቋንቋ ቀይር",
        "om": "🌐 Afaan jijjiiruu"
    },
    "menu_feedback": {
        "am": "💬 አስተያየትዎን ይስጡ",
        "en": "💬 Give Feedback",
        "ti": "💬 ርእይቶኹም ሃቡ",
        "om": "💬 Yaada keessan kennaa"
    },
    "menu_library": {
        "am": "📚 የኔ መጻሕፍት",
        "en": "📚 My Books",
        "ti": "📚 ናተይ መጻሕፍቲ",
        "om": "📚 Kitaabota Koo"
    },

    "feedback_prompt": {
        "am": "💬 <b>አስተያየትዎን ይስጡ!</b>\n\nበዚህ ቦት ስላገኙት አገልግሎት ምን ያስባሉ? ምንስ ቢሻሻል ይወዳሉ? አስተያየትዎን ያካፍሉን!\n\n<i>(ሀሳብዎ በቻናላችን ላይ ስምዎ ሳይጠቀስ ሊለጠፍ ይችላል)</i>",
        "en": "💬 <b>Give Your Feedback!</b>\n\nWhat do you think about your experience with this bot? What would you like to see improved? Share your thoughts with us!\n\n<i>(Your feedback will be posted anonymously on our channel)</i>",
        "ti": "💬 <b>ርእይቶኹም ሃቡ!</b>\n\nብዛዕባ ልምድኹም ኣብዚ ቦት እንታይ ትሓስቡ? እንታይ ዝሻሻል ምደለኹም? ርእይቶኹም ምስና ኣካፍሉ!\n\n<i>(ርእይቶኹም ስምኹም ከይተጠቕሰ ኣብ ቻናልና ክለጠፍ እዩ)</i>",
        "om": "💬 <b>Yaada keessan kennaa!</b>\n\nKana bootiitiin muuxannoo keessan irratti maal yaaddu? Maal fooyyaa'uu akka qabu barbaaddu? Yaada keessan nuuf qoodaa!\n\n<i>(Yaada keessan maqaa keessan osoo hin eeriin chaanaalii keenya irratti maxxanfama)</i>"
    },
    "feedback_thanks": {
        "am": "✅ <b>አስተያየትዎ ደርሶናል!</b>\n\nጊዜዎን ወስደው ሀሳብዎን ስላካፈሉን ከልብ እናመሰግናለን። አገልግሎታችንን ይበልጥ ለማሻሻል እንጠቀምበታለን! 🙏",
        "en": "✅ <b>Feedback Received!</b>\n\nThank you so much for taking the time to share your thoughts. We will keep working to improve the bot! 🙏",
        "ti": "✅ <b>ርእይቶኹም ተቐቢልናዮ!</b>\n\nግዜኹም ወሲድኩም ርእይቶኹም ስለዘካፈልኩምና ካብ ልቢ ነመስግነኩም። ቦቱ ንምሻሻል ክንቅጽል ኢና! 🙏",
        "om": "✅ <b>Yaadni keessan nu gaheera!</b>\n\nYaada keessan nuuf qooduu keessaniitiif yeroo fudhattaniif galatoomaa. Booticha fooyyessuuf itti fayyadamna! 🙏"
    },

    "mypage_title": {
        "am": "👤 <b>የእርስዎ ገፅ</b>",
        "en": "👤 <b>Your Page</b>",
        "ti": "👤 <b>ገጽኩም</b>",
        "om": "👤 <b>Fuula Keessan</b>"
    },
    "mypage_msgs_left": {
        "am": "🎫 ቀሪ ነጻ መልዕክቶች: {msgs}",
        "en": "🎫 Remaining free messages: {msgs}",
        "ti": "🎫 ዝተረፈ ናጻ መልእኽትታት: {msgs}",
        "om": "🎫 Ergaawwan bilisaa hafan: {msgs}"
    },
    "mypage_referrals": {
        "am": "👥 የጋበዟቸው ጓደኞች: <b>{started}</b> የገቡ | <b>{chatted}</b> ማውራት የጀመሩ\n💰 የኮሚሽን ቀሪ ሂሳብ: <b>{balance:.2f} ብር</b>",
        "en": "👥 Invited Friends: <b>{started}</b> Joined | <b>{chatted}</b> Started Chatting\n💰 Commission Balance: <b>{balance:.2f} ETB</b>",
        "ti": "👥 ዝዓደምኩምዎም መሓዙት: <b>{started}</b> ዝኣተዉ | <b>{chatted}</b> ምይይጥ ዝጀመሩ\n💰 ናይ ኮሚሽን ቀሪ ሕሳብ: <b>{balance:.2f} ብር</b>",
        "om": "👥 Hiriyyoota Afeertan: <b>{started}</b> kan seenan | <b>{chatted}</b> kan marii eegalan\n💰 Haftee Komishinii: <b>{balance:.2f} Birrii</b>"
    },
    "mypage_referral_hint": {
        "am": "<i>(5 ጓደኛ ማውራት ሲጀምር 1 ነፃ መጽሐፍ ወይም 25 መልዕክት ያገኛሉ። ማንኛውንም ፓኬጅ ሲገዙ 30% ኮሚሽን ያገኛሉ!)</i>",
        "en": "<i>(When 5 friends start chatting, get 1 free book or 25 messages. Earn 30% commission whenever they buy any package!)</i>",
        "ti": "<i>(5 መሓዙት ምይይጥ ክጅምሩ ከለዉ 1 ናጻ መጽሓፍ ወይ 25 መልእኽቲ ትረኽቡ። ዝኾነ ፓኬጅ ምስ ዝገዝኡ ድማ 30% ኮሚሽን ይረኽቡ!)</i>",
        "om": "<i>(Hiriyyoonni 5 marii yoo eegalan kitaaba bilisaa 1 ykn ergaa 25 argattu. Paakeejii kamiyyuu yoo bitan immoo komishinii 30% argattu!)</i>"
    },
    "mypage_reset_info": {
        "am": "🧹 <b>ማህደር አጽዳ:</b> ይህን ሲጫኑ እስካሁን ያደረግነው ሚስጥራዊ ውይይት ከሲስተማችን ሙሉ በሙሉ ይሰረዛል።",
        "en": "🧹 <b>Clear History:</b> By clicking this, our confidential conversation history so far will be completely deleted from our system.",
        "ti": "🧹 <b>መዝገብ ኣጽሪ:</b> ነዚ ምስ ትጥውቑ ክሳብ ሕጂ ዝገበርናዮ ምስጢራዊ ዕላል ካብ ስርዓትና ብምሉእ ክድምሰስ እዩ።",
        "om": "🧹 <b>Kuusaa Qulleessi:</b> Kana yoo tuqtan mariin iccitii hanga ammaa goone sirna keenya irraa guutumaan guutuutti ni haqama."
    },
    "mypage_reset_warn": {
        "am": "⚠️ <b>ማሳሰቢያ:</b> በምክክር መሃል ከሆኑ ይህን አይጫኑት! ምክንያቱም AIው ያለፈውን ውይይት ስለሚረሳ የጀመሩትን ምክክር መቀጠል አይችልም።",
        "en": "⚠️ <b>Note:</b> Do not click this if you are in the middle of a session! The AI will forget past conversations and won't be able to continue the ongoing counseling.",
        "ti": "⚠️ <b>መተሓሳሰቢ:</b> ኣብ ማእከል ምኽሪ እንተኾንኩም ነዚ ኣይትጠውቑዎ! ምኽንያቱ እቲ AI ንዝሓለፈ ዕላል ስለዝርስዖ ነቲ ዝጀመርኩምዎ ምይይጥ ክቕጽሎ ኣይክእልን እዩ።",
        "om": "⚠️ <b>Akeekkachiisa:</b> Yoo gorsa jidduu jirtu ta'e kana hin tuqinaa! Sababni isaas AI'n marii darbe waan irraanfatuuf gorsa jalqabdan itti fufuu hin danda'u."
    },
    "mypage_topup_hint": {
        "am": "ፓኬጅ ለመግዛት /topup ይጫኑ።",
        "en": "Click /topup to buy a package.",
        "ti": "ፓኬጅ ንምግዛእ /topup ጠውቑ።",
        "om": "Paakeejii bituuf /topup tuqaa."
    },

    "btn_topup": {
        "am": "💳 ክሬዲት ይግዙ",
        "en": "💳 Top Up Credit",
        "ti": "💳 ክሬዲት ግዝኡ",
        "om": "💳 Kireediitii Bitaa"
    },
    "btn_reset": {
        "am": "🧹 ማህደር አጽዳ",
        "en": "🧹 Reset Data",
        "ti": "🧹 መዝገብ ኣጽሪ",
        "om": "🧹 Kuusaa Qulleessi"
    },
    "btn_claim": {
        "am": "🎁 ነፃ መልዕክቶችን ውሰድ",
        "en": "🎁 Claim Free Messages",
        "ti": "🎁 ናጻ መልእኽትታት ውሰዱ",
        "om": "🎁 Ergaawwan Bilisaa Fudhadhu"
    },
    "btn_pay_now": {
        "am": "💳 አሁን ይክፈሉ",
        "en": "💳 Pay Now",
        "ti": "💳 ሕጂ ኽፈሉ",
        "om": "💳 Amma Kaffalaa"
    },

    "reset_confirm": {
        "am": "⚠️ <b>እርግጠኛ ነዎት?</b>\n\nማህደርዎን ካፀዱ እስካሁን ያደረግነው ሚስጥራዊ ውይይት ሙሉ በሙሉ ይሰረዛል፣ እናም AI-ው ያለፈውን አያስታውስም።",
        "en": "⚠️ <b>Are you sure?</b>\n\nIf you reset your data, our confidential conversation so far will be completely deleted, and the AI will not remember the past.",
        "ti": "⚠️ <b>ርግጸኛ ዲኹም?</b>\n\nመዝገብኩም እንተኣጽሪኹም ክሳብ ሕጂ ዝገበርናዮ ምስጢራዊ ዕላል ብምሉእ ክድምሰስ እዩ፣ ከምኡ'ውን እቲ AI ንዝሓለፈ ኣይክዝክሮን እዩ።",
        "om": "⚠️ <b>Mirkaneeffattaniittuu?</b>\n\nKuusaa keessan yoo qulleessitan mariin iccitii hanga ammaa goone guutumaan guutuutti ni haqama, akkasumas AI'n waan darbe hin yaadatu."
    },
    "reset_yes": {
        "am": "✅ አዎ፣ አጽዳ",
        "en": "✅ Yes, reset",
        "ti": "✅ እወ፣ ኣጽሪ",
        "om": "✅ Eeyyee, qulleessi"
    },
    "reset_no": {
        "am": "❌ ተመለስ",
        "en": "❌ Go back",
        "ti": "❌ ተመለስ",
        "om": "❌ Deebi'i"
    },
    "reset_cancelled": {
        "am": "❌ ተሰርዟል። ማህደርዎ አልተሰረዘም።",
        "en": "❌ Cancelled. Your data was not deleted.",
        "ti": "❌ ተሰሪዙ ኣሎ። መዝገብኩም ኣይተደምሰሰን።",
        "om": "❌ Haqameera. Kuusaan keessan hin haqamne."
    },
    "reset_done": {
        "am": "✅ ማህደርዎ ፀድቷል! አዲስ ውይይት እንጀምራለን።",
        "en": "✅ Your data is reset! We will start a new conversation.",
        "ti": "✅ መዝገብኩም ጸርዩ ኣሎ! ሓድሽ ዕላል ክንጅምር ኢና።",
        "om": "✅ Kuusaan keessan qulqullaa'eera! Marii haaraa jalqabna."
    },

    "topup_title": {
        "am": "⚠️ <b>የአማካሪ ፓኬጅ ግዢ</b>",
        "en": "⚠️ <b>Advice Package Purchase</b>",
        "ti": "⚠️ <b>ናይ ኣማኻሪ ፓኬጅ ዕድጊ</b>",
        "om": "⚠️ <b>Bittaa Paakeejii Gorsaa</b>"
    },
    "topup_body": {
        "am": "የጀመርነውን ጥልቅ ውይይት ለመቀጠል እና ወደ ተግባር የሚቀየሩ መፍትሄዎችን ለማግኘት እባክዎ አካውንትዎን ይሙሉ (ክሬዲት ይግዙ)።",
        "en": "To continue our deep conversation and find actionable solutions, please top up your account.",
        "ti": "ዝጀመርናዮ ዕሙቕ ዝበለ ዕላል ንምቕጻልን ናብ ተግባር ዝቕየሩ ፍታሓት ንምርካብን በጃኹም ኣካውንትኩም ምልኡ።",
        "om": "Marii gadi fago jalqabne itti fufuuf fi fala gara hojiitti jijjiiramu argachuuf maaloo herrega keessan guutadhaa."
    },
    "topup_choose": {
        "am": "ከታች ካሉት አማራጮች አንዱን ይምረጡ፦",
        "en": "Choose one of the options below:",
        "ti": "ካብዞም ኣብ ታሕቲ ዘለዉ ኣማራጺታት ሓደ ምረጹ፦",
        "om": "Filannoowwan armaan gadii keessaa tokko filadhaa:"
    },
    "topup_starter": {
        "am": "🔹 <b>Starter: 200 ብር</b> (25 መልዕክቶች) - ለአጭር ውይይት የሚበቃ።",
        "en": "🔹 <b>Starter: 200 Birr</b> (25 Messages) - Enough for a brief conversation.",
        "ti": "🔹 <b>Starter: 200 ብር</b> (25 መልእኽትታት) - ንሓጺር ዕላል ዝኣክል እዩ።",
        "om": "🔹 <b>Starter: Birrii 200</b> (Ergaawwan 25) - Marii gabaabaaf kan ga'u."
    },
    "topup_pro": {
        "am": "🔹 <b>Pro: 400 ብር</b> (75 መልዕክቶች) - [ተመራጭ] ለተሻለ ጥልቅ ውይይት።",
        "en": "🔹 <b>Pro: 400 Birr</b> (75 Messages) - [Recommended] For a better, deeper conversation.",
        "ti": "🔹 <b>Pro: 400 ብር</b> (75 መልእኽትታት) - [ዝምረጽ] ንዝሓሸ ዕሙቕ ዝበለ ዕላል።",
        "om": "🔹 <b>Pro: Birrii 400</b> (Ergaawwan 75) - [Kan filatamu] Marii gadi fagoof kan ta'u."
    },
    "topup_heavy": {
        "am": "🔹 <b>Heavy: 1200 ብር</b> (225 መልዕክቶች) - ለረጅም ጊዜ አገልግሎት ፈላጊዎች።",
        "en": "🔹 <b>Heavy: 1200 Birr</b> (225 Messages) - For long-term service seekers.",
        "ti": "🔹 <b>Heavy: 1200 ብር</b> (225 መልእኽትታት) - ንነዊሕ ግዜ ኣገልግሎት ንዝደልዩ።",
        "om": "🔹 <b>Heavy: Birrii 1200</b> (Ergaawwan 225) - Tajaajila yeroo dheeraa kanneen barbaadaniif."
    },
    "topup_unlimited": {
        "am": "♾️ <b>Unlimited: 1800 ብር</b> (ያለ ገደብ ለ1 ሳምንት) - ምንም ገደብ የሌለው ሙሉ መዳረሻ።",
        "en": "♾️ <b>Unlimited: 1800 Birr</b> (Unlimited for 1 week) - Full access with no restrictions.",
        "ti": "♾️ <b>Unlimited: 1800 ብር</b> (ብዘይ ደረት ን1 ሰሙን) - ዝኾነ ደረት ዘይብሉ ምሉእ ተበጻሕነት።",
        "om": "♾️ <b>Unlimited: Birrii 1800</b> (Daangaa malee torbee 1f) - Daangaa tokko malee guutumaan guutuutti argachuu."
    },
    "topup_unlimited_month": {
        "am": "♾️ <b>Unlimited Monthly: 4900 ብር</b> (ያለ ገደብ ለ1 ወር) - ለአንድ ሙሉ ወር ምንም ገደብ የሌለው መዳረሻ።",
        "en": "♾️ <b>Unlimited Monthly: 4900 Birr</b> (Unlimited for 1 month) - Full access with no restrictions for an entire month.",
        "ti": "♾️ <b>Unlimited Monthly: 4900 ብር</b> (ብዘይ ደረት ን1 ወርሒ) - ንሓደ ምሉእ ወርሒ ዝኾነ ደረት ዘይብሉ ተበጻሕነት።",
        "om": "♾️ <b>Unlimited Monthly: Birrii 4900</b> (Daangaa malee ji'a 1f) - Daangaa tokko malee ji'a guutuu argachuu."
    },
    "topup_cta": {
        "am": "ወዲያውኑ ክፍያ ፈፅመው የጀመርነውን ውይይት ለመቀጠል ከታች ያለውን የክፍያ አማራጭ ይጫኑ። 👇",
        "en": "To make a payment immediately and continue our conversation, click on a payment option below. 👇",
        "ti": "ብቕልጡፍ ክፍሊት ፈጺምኩም ነቲ ዝጀመርናዮ ዕላል ንምቕጻል ኣብ ታሕቲ ዘሎ ናይ ክፍሊት ኣማራጺ ጠውቑ። 👇",
        "om": "Daffitanii kaffaltii raawwattanii marii jalqabne itti fufuuf filannoo kaffaltii armaan gadii tuqaa. 👇"
    },
    "topup_btn_starter": {
        "am": "🔹 Starter: 200 ብር (25 መልዕክቶች)",
        "en": "🔹 Starter: 200 Birr (25 Messages)",
        "ti": "🔹 Starter: 200 ብር (25 መልእኽቲ)",
        "om": "🔹 Starter: Birrii 200 (Ergaa 25)"
    },
    "topup_btn_pro": {
        "am": "🔹 Pro: 400 ብር (75 መልዕክቶች)",
        "en": "🔹 Pro: 400 Birr (75 Messages)",
        "ti": "🔹 Pro: 400 ብር (75 መልእኽቲ)",
        "om": "🔹 Pro: Birrii 400 (Ergaa 75)"
    },
    "topup_btn_heavy": {
        "am": "🔹 Heavy: 1200 ብር (225 መልዕክቶች)",
        "en": "🔹 Heavy: 1200 Birr (225 Messages)",
        "ti": "🔹 Heavy: 1200 ብር (225 መልእኽቲ)",
        "om": "🔹 Heavy: Birrii 1200 (Ergaa 225)"
    },
    "topup_btn_unlimited": {
        "am": "♾️ Unlimited: 1800 ብር (ለ1 ሳምንት)",
        "en": "♾️ Unlimited: 1800 Birr (For 1 Week)",
        "ti": "♾️ Unlimited: 1800 ብር (ን1 ሰሙን)",
        "om": "♾️ Unlimited: Birrii 1800 (Torbee 1f)"
    },
    "topup_btn_unlimited_month": {
        "am": "♾️ Unlimited: 4900 ብር (ለ1 ወር)",
        "en": "♾️ Unlimited: 4900 Birr (For 1 Month)",
        "ti": "♾️ Unlimited: 4900 ብር (ን1 ወርሒ)",
        "om": "♾️ Unlimited: Birrii 4900 (Ji'a 1f)"
    },
    
    "paywall_title": {
        "am": "⚠️ <b>ነፃ የሙከራ ጊዜዎ አልቋል።</b>",
        "en": "⚠️ <b>Your free trial period has ended.</b>",
        "ti": "⚠️ <b>ናጻ ናይ መፈተኒ ግዜኹም ተወዲኡ ኣሎ።</b>",
        "om": "⚠️ <b>Yeroon yaalii bilisaa keessanii xumurameera.</b>"
    },
    "paywall_body": {
        "am": "እስካሁን ጥሩ ቆይታ አድርገናል፤ ነገር ግን ትክክለኛው ለውጥ አሁን ነው የሚጀምረው። የጀመርነውን ጥልቅ ውይይት ለመቀጠል እና ወደ ተግባር የሚቀየሩ መፍትሄዎችን ለማግኘት እባክዎ አካውንትዎን ይሙሉ (ክሬዲት ይግዙ)።",
        "en": "We've had a great time so far; but the real change starts now. To continue our deep conversation and find actionable solutions, please top up your account.",
        "ti": "ክሳብ ሕጂ ጽቡቕ ጻንሒት ጌርና ኢና፤ ግናኸ እቲ ናይ ሓቂ ለውጢ ሕጂ እዩ ዝጅምር። ነቲ ዝጀመርናዮ ዕሙቕ ዝበለ ዕላል ንምቕጻልን ናብ ተግባር ዝቕየሩ ፍታሓት ንምርካብን በጃኹም ኣካውንትኩም ምልኡ።",
        "om": "Hanga ammaa turtoo gaarii dabarsineerra; garuu jijjiiramni dhugaa ammadha kan eegalu. Marii gadi fago jalqabne itti fufuuf fi fala gara hojiitti jijjiiramu argachuuf maaloo herrega keessan guutadhaa."
    },

    "payment_title": {
        "am": "📱 <b>ክፍያ</b>",
        "en": "📱 <b>Payment</b>",
        "ti": "📱 <b>ክፍሊት</b>",
        "om": "📱 <b>Kaffaltii</b>"
    },
    "payment_instructions": {
        "am": "እባክዎ ከታች ያለውን <b>አሁን ይክፈሉ</b> ቁልፍ በመጫን <b>{amount} ብር</b> ይክፈሉ።\nክፍያዎ እንደተጠናቀቀ ሲስተሙ በራስ-ሰር ይከፈትልዎታል!\n\n⚠️ <i>ማሳሰቢያ: ይህ የክፍያ ሊንክ ለአንድ ጊዜ ብቻ የሚያገለግል ነው። ክፍያዎ ካልተሳካ ወይም ገጹን ከዘጉት፣ አዲስ ሊንክ ለማግኘት እባክዎ ፓኬጅዎን እንደገና ይምረጡ።</i>",
        "en": "Please click the <b>Pay Now</b> button below to pay <b>{amount} Birr</b>.\nOnce your payment is complete, the system will automatically unlock for you!\n\n⚠️ <i>Note: This checkout link is for one-time use. If your payment fails or you close the page, please select your package again to generate a new link.</i>",
        "ti": "በጃኹም ኣብ ታሕቲ ዘሎ <b>ሕጂ ኽፈሉ</b> ዝብል መርገጺ ብምጥዋቕ <b>{amount} ብር</b> ክፈሉ ።\nክፍሊትኩም ምስ ተዛዘመ እቲ ስርዓት ብኣውቶማቲክ ክኽፈተልኩም እዩ!\n\n⚠️ <i>መተሓሳሰቢ: እዚ ናይ ክፍሊት ሊንክ ንሓደ ግዜ ጥራይ ዘገልግል እዩ። ክፍሊትኩም እንተዘይተዓዊቱ ወይ ነቲ ገጽ እንተዓጺኹሞ፡ ሓዱሽ ሊንክ ንምርካብ በጃኹም ፓኬጅኩም እንደገና ምረጹ።</i>",
        "om": "Maaloo cuqqaallii <b>Amma Kaffalaa</b> armaan gadii tuquun <b>Birrii {amount}</b> kaffalaa.\nKaffaltiin keessan akkuma xumurameen sirnichii of-umaan isiniif banama!\n\n⚠️ <i>Hubachiisa: Liinkiin kaffaltii kun yeroo tokkoof qofa kan tajaajiludha. Kaffaltiin keessan yoo milkaa'uu baate ykn fuulicha yoo cuftani, liinkii haaraa argachuuf maaloo paakeejii keessan irra deebi'uun filadhaa.</i>"
    },
    "payment_preparing": {
        "am": "እየተዘጋጀ ነው...",
        "en": "Preparing...",
        "ti": "ይዳሎ ኣሎ...",
        "om": "Qophaa'aa jira..."
    },
    "payment_error": {
        "am": "❌ የክፍያ ሊንክ ማመንጨት አልተቻለም።\n<b>ምክንያት:</b> {err}",
        "en": "❌ Failed to generate payment link.\n<b>Reason:</b> {err}",
        "ti": "❌ ናይ ክፍሊት መላግቦ ምፍጣር ኣይተኻእለን።\n<b>ምኽንያት:</b> {err}",
        "om": "❌ Liinkii kaffaltii uumuu hin dandeenye.\n<b>Sababni isaa:</b> {err}"
    },
    "payment_success_msgs": {
        "am": "✅ <b>ክፍያዎ ተረጋግጧል!</b>\n{msgs} መልዕክቶች ወደ አካውንትዎ ገብተዋል።\nውይይታችንን መቀጠል እንችላለን...",
        "en": "✅ <b>Payment Confirmed!</b>\n{msgs} messages have been added to your account.\nWe can now continue our conversation...",
        "ti": "✅ <b>ክፍሊትኩም ተረጋጊጹ ኣሎ!</b>\n{msgs} መልእኽትታት ናብ ኣካውንትኩም ኣትዩ ኣሎ።\nዕላልና ክንቅጽል ንኽእል ኢና...",
        "om": "✅ <b>Kaffaltiin keessan mirkanaa'eera!</b>\nErgaawwan {msgs} gara herrega keessaniitti galaniiru.\nMarii keenya itti fufuu ni dandeenya..."
    },
    "payment_success_unlimited": {
        "am": "✅ <b>ክፍያዎ ተረጋግጧል!</b>\nለ1 ሳምንት ያህል ያልተገደበ ሙሉ መዳረሻ አግኝተዋል።\nውይይታችንን መቀጠል እንችላለን...",
        "en": "✅ <b>Payment Confirmed!</b>\nYou have gained unlimited access for 1 week.\nWe can now continue our conversation...",
        "ti": "✅ <b>ክፍሊትኩም ተረጋጊጹ ኣሎ!</b>\nን1 ሰሙን ዝኣክል ዘይተደረተ ምሉእ ተበጻሕነት ረኺብኩም ኣለኹም።\nዕላልና ክንቅጽል ንኽእል ኢና...",
        "om": "✅ <b>Kaffaltiin keessan mirkanaa'eera!</b>\nTorbee 1f argannoo daangaa hin qabne argattaniittu.\nMarii keenya itti fufuu ni dandeenya..."
    },
    "payment_success_unlimited_month": {
        "am": "✅ <b>ክፍያዎ ተረጋግጧል!</b>\nለ1 ወር ያህል ያልተገደበ ሙሉ መዳረሻ አግኝተዋል።\nውይይታችንን መቀጠል እንችላለን...",
        "en": "✅ <b>Payment Confirmed!</b>\nYou have gained unlimited access for 1 month.\nWe can now continue our conversation...",
        "ti": "✅ <b>ክፍሊትኩም ተረጋጊጹ ኣሎ!</b>\nን1 ወርሒ ዝኣክል ዘይተደረተ ምሉእ ተበጻሕነት ረኺብኩም ኣለኹም።\nዕላልና ክንቅጽል ንኽእል ኢና...",
        "om": "✅ <b>Kaffaltiin keessan mirkanaa'eera!</b>\nJi'a 1f argannoo daangaa hin qabne argattaniittu.\nMarii keenya itti fufuu ni dandeenya..."
    },
    "receipt_verifying": {
        "am": "⏳ ደረሰኝዎን በማረጋገጥ ላይ ነን...",
        "en": "⏳ Verifying your payment receipt...",
        "ti": "⏳ ደረሰኝኩም እናረጋገጽና ኢና...",
        "om": "⏳ Nagahee kaffaltii keessan mirkaneessaa jirra..."
    },
    "receipt_used": {
        "am": "❌ ይህ የክፍያ ደረሰኝ ከዚህ በፊት ጥቅም ላይ ውሏል! እባክዎ አዲስ የክፍያ ደረሰኝ ይላኩ።",
        "en": "❌ This payment receipt has already been used! Please send a new receipt screenshot.",
        "ti": "❌ እዚ ናይ ክፍሊት ደረሰኝ ኣቐዲሙ ተጠቒምኩምሉ ኢኹም! በጃኹም ሓድሽ ደረሰኝ ስደዱ።",
        "om": "❌ Nagaheen kaffaltii kun kanaan dura itti fayyadameera! Maaloo nagahee haaraa ergaa."
    },
    "receipt_forwarded_to_admin": {
        "am": "📩 <b>ደረሰኝዎ ደርሶናል!</b>\n━━━━━━━━━━━━━━━━━━━━\nየክፍያ ደረሰኝዎ ለፈጣን ማረጋገጫ በቀጥታ ለአስተዳዳሪ ተልኳል። በጥቂት ደቂቃዎች ውስጥ ተረጋግጦ ይከፈትልዎታል! 🙏",
        "en": "📩 <b>Receipt Received!</b>\n━━━━━━━━━━━━━━━━━━━━\nYour payment receipt has been forwarded to our admin team for verification. It will be reviewed and activated shortly! 🙏",
        "ti": "📩 <b>ደረሰኝኩም በጺሑና ኣሎ!</b>\n━━━━━━━━━━━━━━━━━━━━\nናይ ክፍሊት ደረሰኝኩም ብቕልጡፍ ንምርግጋጽ ናብ ኣመሓዳሪ ተላኢኹ ኣሎ። ኣብ ውሽጢ ሒደት ደቓይቕ ተረጋጊጹ ክኽፈተልኩም እዩ! 🙏",
        "om": "📩 <b>Nagaheen keessan nu gaheera!</b>\n━━━━━━━━━━━━━━━━━━━━\nNagaheen kaffaltii keessan akka mirkanaa'uuf gara maanaajeriitti ergamera. Daqiiqaa muraasa keessatti mirkanaa'ee isiniif banama! 🙏"
    },
    "receipt_rejected_user": {
        "am": "❌ <b>የክፍያ ደረሰኝዎ አልተረጋገጠም።</b>\n━━━━━━━━━━━━━━━━━━━━\nያስገቡት ደረሰኝ ግልጽ ስላልሆነ ወይም መጠኑ ስለማይዛመድ አልተቀበልነውም። እባክዎ ትክክለኛውን ደረሰኝ በድጋሚ ይላኩ ወይም አስተዳዳሪን ያነጋግሩ።",
        "en": "❌ <b>Receipt Not Verified</b>\n━━━━━━━━━━━━━━━━━━━━\nThe receipt image was unclear or the details did not match. Please send a clearer screenshot of your payment receipt or contact our admin.",
        "ti": "❌ <b>ናይ ክፍሊት ደረሰኝኩም ኣይተረጋገጸን።</b>\n━━━━━━━━━━━━━━━━━━━━\nእቲ ዝለኣኽኩምዎ ደረሰኝ ንጹር ስለዘይኮነ ወይ መጠን ገንዘብ ስለዘይተዛመደ ኣይተቐበልናዮን። በጃኹም ንጹር ደረሰኝ ዳግማይ ስደዱ።",
        "om": "❌ <b>Nagaheen kaffaltii hin mirkanoofne.</b>\n━━━━━━━━━━━━━━━━━━━━\nNagaheen ergitan ifa waan hin taaneef ykn guddinni kaffaltii waan wal hin simneef hin fudhatamne. Maaloo nagahee ifa ta'e irra deebi'aa ergaa."
    },
    "tip_received": {
        "am": "💖 <b>ስጦታዎ ደርሶናል!</b>\nከልብ እናመሰግናለን! ቡድናችንን በጣም አበረታተውታል።",
        "en": "💖 <b>We received your gift!</b>\nThank you from the bottom of our hearts! You have greatly encouraged our team.",
        "ti": "💖 <b>ውህብቶኹም በጺሑና ኣሎ!</b>\nካብ ልቢ ነመስግን! ንጉጅለና ብጣዕሚ ኣበራቲዕኩምዎ ኢኹም።",
        "om": "💖 <b>Kennaan keessan nu gaheera!</b>\nGuddaa galatoomaa! Garee keenya baay'ee jajjabeessitaniittu."
    },

    "invite_title": {
        "am": "🎁 <b>ጓደኛዎን ይጋብዙ እና ገንዘብ ያግኙ!</b>",
        "en": "🎁 <b>Invite Friends & Earn Money!</b>",
        "ti": "🎁 <b>መሓዛኹም ዕደሙን ገንዘብ ርኸቡን!</b>",
        "om": "🎁 <b>Hiriyyaa Afeeraa Maallaqa Argadhaa!</b>"
    },
    "invite_stats": {
        "am": "📊 <b>የእርስዎ የመጋበዝ ውጤት:</b>\n• ቦቱን የተቀላቀሉ: <b>{started}</b>\n• ማውራት የጀመሩ: <b>{chatted}</b>\n• ላልተወሰደ ሽልማት የቀረቡ: <b>{uncredited}</b>/5\n\n💰 <b>የኮሚሽን ቀሪ ሂሳብ:</b> <b>{balance:.2f} ብር</b>",
        "en": "📊 <b>Your Referral Performance:</b>\n• Started the bot: <b>{started}</b>\n• Started chatting: <b>{chatted}</b>\n• Progress to next reward: <b>{uncredited}</b>/5\n\n💰 <b>Commission Balance:</b> <b>{balance:.2f} ETB</b>",
        "ti": "📊 <b>ናይ ምዕዳም ውጽኢትኩም:</b>\n• ቦት ዝኣተዉ: <b>{started}</b>\n• ምይይጥ ዝጀመሩ: <b>{chatted}</b>\n• ንሽልማት ዝቐረቡ: <b>{uncredited}</b>/5\n\n💰 <b>ናይ ኮሚሽን ቀሪ ሕሳብ:</b> <b>{balance:.2f} ብር</b>",
        "om": "📊 <b>Raawwii Afeerraa Keessanii:</b>\n• Boottii kan seenan: <b>{started}</b>\n• Marii kan eegalan: <b>{chatted}</b>\n• Badhaasa itti aanuuf: <b>{uncredited}</b>/5\n\n💰 <b>Haftee Komishinii:</b> <b>{balance:.2f} Birrii</b>"
    },
    "invite_rules": {
        "am": "💡 <b>ህጎች እና ሽልማቶች:</b>\n1️⃣ <b>5 ጓደኞች ማውራት ሲጀምሩ፦</b> ማንኛውንም 1 ነፃ መጽሐፍ ወይም 25 ነፃ መልዕክቶች ይሸለማሉ!\n2️⃣ <b>ጓደኛዎ ማንኛውንም ፓኬጅ ሲገዛ፦</b> ወዲያውኑ <b>30% ኮሚሽን</b> ወደ ቀሪ ሂሳብዎ ገቢ ይሆናል!\n3️⃣ <b>ገንዘብ ማውጣት:</b> ዝቅተኛው 100 ብር ሲሆን በቴሌብር ወይም በንግድ ባንክ ማውጣት ይችላሉ።",
        "en": "💡 <b>Rules & Rewards:</b>\n1️⃣ <b>When 5 friends start chatting:</b> Choose ANY 1 free book or 25 free messages!\n2️⃣ <b>When an invited friend buys ANY package:</b> You earn an instant <b>30% commission</b>!\n3️⃣ <b>Withdrawal:</b> Minimum payout is 100 Birr via Telebirr or CBE Bank.",
        "ti": "💡 <b>ሕግታትን ሽልማታትን:</b>\n1️⃣ <b>5 መሓዙት ምይይጥ ክጅምሩ ከለዉ:</b> ዝደለኹምዎ 1 ናጻ መጽሓፍ ወይ 25 ናጻ መልእኽትታት ትሸለሙ!\n2️⃣ <b>ዝዓደምኩምዎ ሰብ ዝኾነ ፓኬጅ ምስ ዝገዝእ:</b> ብቕጽበት <b>30% ኮሚሽን</b> ይኣትወልኩም!\n3️⃣ <b>ገንዘብ ምውጻእ:</b> ትሑት 100 ብር ኮይኑ ብቴሌብር ወይ ንግዲ ባንክ ከተውጽኡ ትኽእሉ ኢኹም።",
        "om": "💡 <b>Seerotaa fi Badhaasota:</b>\n1️⃣ <b>Hiriyyoonni 5 marii yoo eegalan:</b> Kitaaba bilisaa 1 kamiyyuu ykn ergaawwan 25 badhaafamtu!\n2️⃣ <b>Hiriyyaan keessan paakeejii kamiyyuu yoo bite:</b> Battalumatti <b>komishinii 30%</b> argattu!\n3️⃣ <b>Baasii baafachuu:</b> Gadi aanaan Birrii 100 yoo ta'u Telebirr ykn Baankii Daldalaatiin baafachuu dandeessu."
    },
    "invite_link": {
        "am": "🔗 <b>የእርስዎ መጋበዣ ሊንክ:</b>",
        "en": "🔗 <b>Your Invitation Link:</b>",
        "ti": "🔗 <b>ናይ መጋበዝያ መላግቦኹም:</b>",
        "om": "🔗 <b>Liinkii Afeerraa Keessanii:</b>"
    },
    "btn_claim_milestone": {
        "am": "🎁 ሽልማትዎን ይውሰዱ",
        "en": "🎁 Claim Milestone Reward",
        "ti": "🎁 ሽልማትኩም ውሰዱ",
        "om": "🎁 Badhaasa Keessan Fudhadhaa"
    },
    "btn_request_payout": {
        "am": "💸 ሂሳብ አውጣ",
        "en": "💸 Request Payout",
        "ti": "💸 ገንዘብ ኣውጽእ",
        "om": "💸 Baasii Baafadhaa"
    },
    "btn_payout_history": {
        "am": "📜 የክፍያ ታሪክ",
        "en": "📜 Payout History",
        "ti": "📜 ናይ ክፍሊት ታሪኽ",
        "om": "📜 Seenaa Kaffaltii"
    },
    "claim_choose_reward": {
        "am": "🎁 <b>እንኳን ደስ አሎት!</b> 5 ያጋበዟቸው ጓደኞች ማውራት ጀምረዋል!\n\nየሚፈልጉትን ሽልማት ይምረጡ፦",
        "en": "🎁 <b>Congratulations!</b> 5 invited friends started chatting!\n\nChoose your preferred reward:",
        "ti": "🎁 <b>እንኳዕ ደስ በለኩም!</b> 5 ዝዓደምኩምዎም መሓዙት ምይይጥ ጀሚሮም ኣለዉ!\n\nዝደለኹምዎ ሽልማት ምረጹ፦",
        "om": "🎁 <b>Baga gammaddan!</b> Hiriyyoonni afeertan 5 marii eegalaniiru!\n\nBadhaasa barbaaddan filadhaa:"
    },
    "btn_reward_msgs": {
        "am": "💬 25 ነፃ መልዕክቶች",
        "en": "💬 25 Free Messages",
        "ti": "💬 25 ናጻ መልእኽትታት",
        "om": "💬 Ergaawwan Bilisaa 25"
    },
    "btn_reward_book": {
        "am": "📚 1 ነፃ መጽሐፍ ምረጥ",
        "en": "📚 Pick 1 Free Book",
        "ti": "📚 1 ናጻ መጽሓፍ ምረጽ",
        "om": "📚 Kitaaba Bilisaa 1 Filadhu"
    },
    "claim_msgs_success": {
        "am": "🎉 <b>እንኳን ደስ አሎት!</b> 25 ነፃ መልዕክቶች ወደ አካውንትዎ ገቢ ሆነዋል!",
        "en": "🎉 <b>Congratulations!</b> 25 free messages have been added to your account!",
        "ti": "🎉 <b>እንኳዕ ደስ በለኩም!</b> 25 ናጻ መልእኽትታት ኣብ ሕሳብኩም ተወሲኹ ኣሎ!",
        "om": "🎉 <b>Baga gammaddan!</b> Ergaawwan bilisaa 25 herrega keessanitti dabalameera!"
    },
    "claim_book_success": {
        "am": "🎉 <b>እንኳን ደስ አሎት!</b> '<b>{title}</b>' የተሰኘው መጽሐፍ በነፃ ተከፍቶልዎታል!\nአሁኑኑ በ '📚 የኔ መጻሕፍት' ገፅ ውስጥ ገብተው ማንበብ ይችላሉ።",
        "en": "🎉 <b>Congratulations!</b> The book '<b>{title}</b>' has been unlocked for free!\nYou can read it now under '📚 My Books'.",
        "ti": "🎉 <b>እንኳዕ ደስ በለኩም!</b> መጽሓፍ '<b>{title}</b>' ብናጻ ተኸፊቱልኩም ኣሎ!\nሕጂ ኣብ '📚 ናተይ መጻሕፍቲ' ኣቲኹም ከተንብቡ ትኽእሉ ኢኹም።",
        "om": "🎉 <b>Baga gammaddan!</b> Kitaabni '<b>{title}</b>' jedhamu bilisaan isiniif banameera!\nAmma '📚 Kitaabota Koo' keessatti dubbisuu dandeessu."
    },
    "claim_fail_5": {
        "am": "❌ ገና 5 ማውራት የጀመሩ ጓደኞች አልሞሉም!",
        "en": "❌ You have not reached 5 chatting friends yet!",
        "ti": "❌ ዛጊት ምይይጥ ዝጀመሩ 5 መሓዙት ኣይመልኡን!",
        "om": "❌ Hiriyyoonni marii eegalan 5 hin guunne!"
    },
    "claim_success": {
        "am": "🎉 እንኳን ደስ አለዎት! 25 ነፃ መልዕክቶች ተሰጥቶዎታል!",
        "en": "🎉 Congratulations! You have been awarded 25 free messages!",
        "ti": "🎉 እንኳዕ ደስ በለኩም! 25 ናጻ መልእኽትታት ተዋሂቡኩም ኣሎ!",
        "om": "🎉 Baga gammaddan! Ergaawwan bilisaa 25 isiniif kennamaniiru!"
    },
    "claim_fail": {
        "am": "❌ ገና 5 ማውራት የጀመሩ ጓደኞች አልሞሉም!",
        "en": "❌ You haven't reached 5 chatting friends yet!",
        "ti": "❌ ዛጊት ምይይጥ ዝጀመሩ 5 መሓዙት ኣይመልኡን!",
        "om": "❌ Ammayyuu marii eegalan nama 5 hin guunne!"
    },

    "payout_min_error": {
        "am": "❌ ዝቅተኛው የማውጣት መጠን 100 ብር ነው። አሁን ያለዎት ቀሪ ሂሳብ {balance:.2f} ብር ነው።",
        "en": "❌ Minimum payout is 100 Birr. Your current balance is {balance:.2f} ETB.",
        "ti": "❌ ትሑት ናይ ምውጻእ መጠን 100 ብር እዩ። ሕጂ ዘለኩም ቀሪ ሕሳብ {balance:.2f} ብር እዩ።",
        "om": "❌ Gadi aanaan baasii baafachuu Birrii 100 dha. Hafteen keessan ammaa Birrii {balance:.2f} dha."
    },
    "payout_choose_method": {
        "am": "💸 <b>የገንዘብ ማውጫ መንገድ ይምረጡ</b>\n━━━━━━━━━━━━━━━━━━━━\nያለዎት ቀሪ ሂሳብ: <b>{balance:.2f} ብር</b>\nዝቅተኛው መጠን: <b>100 ብር</b>\n\nክፍያ የሚቀበሉበትን ዘዴ ይምረጡ፦",
        "en": "💸 <b>Choose Payout Method</b>\n━━━━━━━━━━━━━━━━━━━━\nYour Balance: <b>{balance:.2f} ETB</b>\nMinimum Payout: <b>100 ETB</b>\n\nSelect your preferred payment method:",
        "ti": "💸 <b>መንገዲ ምውጻእ ገንዘብ ምረጹ</b>\n━━━━━━━━━━━━━━━━━━━━\nዘለኩም ቀሪ ሕሳብ: <b>{balance:.2f} ብር</b>\nትሑት መጠን: <b>100 ብር</b>\n\nክፍሊት እትቕበሉሉ መገዲ ምረጹ፦",
        "om": "💸 <b>Mala Baasii Baafachuu Filadhaa</b>\n━━━━━━━━━━━━━━━━━━━━\nHaftee Keessan: <b>{balance:.2f} Birrii</b>\nGadi aanaa: <b>Birrii 100</b>\n\nMala kaffaltiin ittiin isiniif ergamu filadhaa:"
    },
    "btn_method_telebirr": {
        "am": "📱 ቴሌብር",
        "en": "📱 Telebirr",
        "ti": "📱 ቴሌብር",
        "om": "📱 Telebirr"
    },
    "btn_method_cbe": {
        "am": "🏦 የኢትዮጵያ ንግድ ባንክ",
        "en": "🏦 Commercial Bank of Ethiopia (CBE)",
        "ti": "🏦 ንግዲ ባንክ ኢትዮጵያ",
        "om": "🏦 Baankii Daldala Itoophiyaa"
    },
    "payout_prompt_telebirr": {
        "am": "📱 <b>ቴሌብር የክፍያ መጠየቂያ</b>\n━━━━━━━━━━━━━━━━━━━━\nያለዎት ቀሪ ሂሳብ: <b>{balance:.2f} ብር</b>\n\nእባክዎ የሚከተሉትን መረጃዎች በኮማ (,) ወይም በመስመር ለይተው ይላኩልን፦\n1️⃣ <b>የቴሌብር ስልክ ቁጥር</b>\n2️⃣ <b>ሙሉ ስም</b>\n3️⃣ <b>የብር መጠን (ዝቅተኛ 100)</b>\n\n📝 <b>ምሳሌ፦</b>\n<code>0912345678, አበበ ከበደ, 150</code>\n\n<i>ለመሰረዝ /cancel ብለው ይፃፉ።</i>",
        "en": "📱 <b>Telebirr Payout Request</b>\n━━━━━━━━━━━━━━━━━━━━\nYour Balance: <b>{balance:.2f} ETB</b>\n\nPlease reply with your details separated by comma or new lines:\n1️⃣ <b>Telebirr Phone Number</b>\n2️⃣ <b>Full Name</b>\n3️⃣ <b>Amount to withdraw (min 100)</b>\n\n📝 <b>Example:</b>\n<code>0912345678, Abebe Kebede, 150</code>\n\n<i>Type /cancel to abort.</i>",
        "ti": "📱 <b>ናይ ቴሌብር ክፍሊት ሕቶ</b>\n━━━━━━━━━━━━━━━━━━━━\nዘለኩም ቀሪ ሕሳብ: <b>{balance:.2f} ብር</b>\n\nበጃኹም ዝስዕቡ ሓበሬታታት ብኮማ (,) ፈሊኹም ስደዱልና፦\n1️⃣ <b>ናይ ቴሌብር ቁጽሪ ስልኪ</b>\n2️⃣ <b>ምሉእ ስም</b>\n3️⃣ <b>መጠን ገንዘብ (ትሑት 100 ብር)</b>\n\n📝 <b>ኣብነት፦</b>\n<code>0912345678, ኣበበ ከበደ, 150</code>\n\n<i>ንምስራዝ /cancel ኢልኩም ጸሓፉ።</i>",
        "om": "📱 <b>Gaaffii Baasii Telebirr</b>\n━━━━━━━━━━━━━━━━━━━━\nHaftee Keessan: <b>{balance:.2f} Birrii</b>\n\nMallattoolee armaan gadii koman (,) addaan baasaatii ergaa:\n1️⃣ <b>Lakkoofsa Bilbilaa Telebirr</b>\n2️⃣ <b>Maqaa Guutuu</b>\n3️⃣ <b>Hamma Maallaqaa (yoo xiqqaate 100)</b>\n\n📝 <b>Fakkeenya:</b>\n<code>0912345678, Abebe Kebede, 150</code>\n\n<i>Haqsuuf /cancel jedhaa barreessaa.</i>"
    },
    "payout_prompt_cbe": {
        "am": "🏦 <b>ንግድ ባንክ የክፍያ መጠየቂያ</b>\n━━━━━━━━━━━━━━━━━━━━\nያለዎት ቀሪ ሂሳብ: <b>{balance:.2f} ብር</b>\n\nእባክዎ የሚከተሉትን መረጃዎች በኮማ (,) ወይም በመስመር ለይተው ይላኩልን፦\n1️⃣ <b>የንግድ ባንክ ሂሳብ ቁጥር</b>\n2️⃣ <b>ሙሉ ስም</b>\n3️⃣ <b>የብር መጠን (ዝቅተኛ 100)</b>\n\n📝 <b>ምሳሌ፦</b>\n<code>1000123456789, አበበ ከበደ, 200</code>\n\n<i>ለመሰረዝ /cancel ብለው ይፃፉ።</i>",
        "en": "🏦 <b>CBE Bank Payout Request</b>\n━━━━━━━━━━━━━━━━━━━━\nYour Balance: <b>{balance:.2f} ETB</b>\n\nPlease reply with your details separated by comma or new lines:\n1️⃣ <b>CBE Account Number</b>\n2️⃣ <b>Full Name</b>\n3️⃣ <b>Amount to withdraw (min 100)</b>\n\n📝 <b>Example:</b>\n<code>1000123456789, Abebe Kebede, 200</code>\n\n<i>Type /cancel to abort.</i>",
        "ti": "🏦 <b>ናይ ንግዲ ባንክ ክፍሊት ሕቶ</b>\n━━━━━━━━━━━━━━━━━━━━\nዘለኩም ቀሪ ሕሳብ: <b>{balance:.2f} ብር</b>\n\nበጃኹም ዝስዕቡ ሓበሬታታት ብኮማ (,) ፈሊኹም ስደዱልና፦\n1️⃣ <b>ናይ ንግዲ ባንክ ቁጽሪ ሕሳብ</b>\n2️⃣ <b>ምሉእ ስም</b>\n3️⃣ <b>መጠን ገንዘብ (ትሑት 100 ብር)</b>\n\n📝 <b>ኣብነት፦</b>\n<code>1000123456789, ኣበበ ከበደ, 200</code>\n\n<i>ንምስራዝ /cancel ኢልኩም ጸሓፉ።</i>",
        "om": "🏦 <b>Gaaffii Baasii Baankii Daldalaa</b>\n━━━━━━━━━━━━━━━━━━━━\nHaftee Keessan: <b>{balance:.2f} Birrii</b>\n\nMallattoolee armaan gadii koman (,) addaan baasaatii ergaa:\n1️⃣ <b>Lakkoofsa Herregaa Baankii Daldalaa</b>\n2️⃣ <b>Maqaa Guutuu</b>\n3️⃣ <b>Hamma Maallaqaa (yoo xiqqaate 100)</b>\n\n📝 <b>Fakkeenya:</b>\n<code>1000123456789, Abebe Kebede, 200</code>\n\n<i>Haqsuuf /cancel jedhaa barreessaa.</i>"
    },
    "payout_request_submitted": {
        "am": "✅ <b>የክፍያ ጥያቄዎ ቀርቧል!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 መጠን: <b>{amount:.2f} ብር</b>\n🏦 ዘዴ: <b>{method}</b>\n👤 ስም: <b>{name}</b>\n🔢 ቁጥር: <code>{account}</code>\n\n<i>አስተዳዳሪው ክፍያውን ሲፈጽም ማረጋገጫ ይደርስዎታል። እናመሰግናለን!</i>",
        "en": "✅ <b>Payout Request Submitted!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 Amount: <b>{amount:.2f} ETB</b>\n🏦 Method: <b>{method}</b>\n👤 Name: <b>{name}</b>\n🔢 Account/Phone: <code>{account}</code>\n\n<i>You will receive a notification once the admin processes and approves your payout. Thank you!</i>",
        "ti": "✅ <b>ናይ ክፍሊት ሕቶኹም ቀሪቡ ኣሎ!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 መጠን: <b>{amount:.2f} ብር</b>\n🏦 መገዲ: <b>{method}</b>\n👤 ስም: <b>{name}</b>\n🔢 ቁጽሪ: <code>{account}</code>\n\n<i>ኣመሓዳሪ ነቲ ክፍሊት ምስ ፈጸሞ ማረጋገጺ ክበጽሓኩም እዩ። ነመስግን!</i>",
        "om": "✅ <b>Gaaffiin Kaffaltii Dhiyaateera!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 Hamma: <b>{amount:.2f} Birrii</b>\n🏦 Mala: <b>{method}</b>\n👤 Maqaa: <b>{name}</b>\n🔢 Lakkoofsa: <code>{account}</code>\n\n<i>Kaffaltiin kun yeroo raawwatamu beeksisni isiniif ergama. Galatoomaa!</i>"
    },
    "payout_cancelled": {
        "am": "❌ የክፍያ ጥያቄ ተሰርዟል።",
        "en": "❌ Payout request cancelled.",
        "ti": "❌ ናይ ክፍሊት ሕቶ ተሰሪዙ።",
        "om": "❌ Gaaffiin kaffaltii haqameera."
    },
    "payout_history_empty": {
        "am": "📜 <b>እስካሁን ምንም የክፍያ ታሪክ የለዎትም።</b>\n\nቀሪ ሂሳብዎ 100 ብር ሲሞላ ማውጣት ይችላሉ!",
        "en": "📜 <b>You do not have any payout history yet.</b>\n\nYou can request a payout once your balance reaches 100 ETB!",
        "ti": "📜 <b>ክሳብ ሕጂ ዝኾነ ናይ ክፍሊት ታሪኽ የብልኩምን።</b>\n\nቀሪ ሕሳብኩም 100 ብር ምስ በጽሐ ከተውጽኡ ትኽእሉ ኢኹም!",
        "om": "📜 <b>Hanga ammaatti seenaa kaffaltii hin qabdan.</b>\n\nHafteen keessan Birrii 100 yoo ga'u baasii baafachuu dandeessu!"
    },
    "payout_history_title": {
        "am": "📜 <b>የእርስዎ የክፍያ ታሪክ፦</b>",
        "en": "📜 <b>Your Payout History:</b>",
        "ti": "📜 <b>ናይ ክፍሊት ታሪኽኩም፦</b>",
        "om": "📜 <b>Seenaa Kaffaltii Keessanii:</b>"
    },
    "payout_status_pending": {
        "am": "⏳ በመጠባበቅ ላይ",
        "en": "⏳ Pending",
        "ti": "⏳ እናተጸበየ ዝርከብ",
        "om": "⏳ Eeggachaa kan jiru"
    },
    "payout_status_approved": {
        "am": "✅ የተከፈለ",
        "en": "✅ Paid",
        "ti": "✅ ዝተኸፍለ",
        "om": "✅ Kan kaffalame"
    },
    "payout_status_rejected": {
        "am": "❌ ውድቅ የተደረገ",
        "en": "❌ Rejected",
        "ti": "❌ ውድቂ ዝኾነ",
        "om": "❌ Kan kufaa ta'e"
    },
    "payout_approved_notif": {
        "am": "🎉 <b>ክፍያዎ ተፈጽሟል!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 መጠን: <b>{amount:.2f} ብር</b>\n🏦 ዘዴ: <b>{method}</b> ({account})\n👤 ስም: <b>{name}</b>\n\n<i>ገንዘቡ ወደ አካውንትዎ ገቢ ተደርጓል። ከእኛ ጋር ስለሰሩ እናመሰግናለን!</i>",
        "en": "🎉 <b>Payout Processed!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 Amount: <b>{amount:.2f} ETB</b>\n🏦 Method: <b>{method}</b> ({account})\n👤 Name: <b>{name}</b>\n\n<i>The funds have been transferred to your account. Thank you for partnering with us!</i>",
        "ti": "🎉 <b>ክፍሊትኩም ተፈጺሙ ኣሎ!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 መጠን: <b>{amount:.2f} ብር</b>\n🏦 መገዲ: <b>{method}</b> ({account})\n👤 ስም: <b>{name}</b>\n\n<i>እቲ ገንዘብ ናብ ሕሳብኩም ኣትዩ ኣሎ። ምሳና ስለዝሰራሕኩም ነመስግን!</i>",
        "om": "🎉 <b>Kaffaltiin keessan raawwatameera!</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 Hamma: <b>{amount:.2f} Birrii</b>\n🏦 Mala: <b>{method}</b> ({account})\n👤 Maqaa: <b>{name}</b>\n\n<i>Maallaqni herrega keessanitti dabalameera. Nu wajjin hojjechuu keessaniif galatoomaa!</i>"
    },
    "payout_rejected_notif": {
        "am": "⚠️ <b>የክፍያ ጥያቄዎ ውድቅ ተደርጓል</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 የተጠየቀው <b>{amount:.2f} ብር</b> ወደ ኮሚሽን ቀሪ ሂሳብዎ ተመልሷል።\n\n<i>እባክዎ ትክክለኛ የቴሌብር ወይም የባንክ መረጃ ማቅረብዎን አረጋግጠው እንደገና ይጠይቁ።</i>",
        "en": "⚠️ <b>Payout Request Rejected</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 The requested <b>{amount:.2f} ETB</b> has been refunded to your commission balance.\n\n<i>Please ensure your Telebirr or bank details are completely accurate before submitting again.</i>",
        "ti": "⚠️ <b>ናይ ክፍሊት ሕቶኹም ውድቂ ኮይኑ ኣሎ</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 ዝተሓተተ <b>{amount:.2f} ብር</b> ናብ ናይ ኮሚሽን ቀሪ ሕሳብኩም ተመሊሱ ኣሎ።\n\n<i>በጃኹም ትክክለኛ ናይ ቴሌብር ወይ ናይ ባንክ ሓበሬታ ምዃኑ ኣረጋጊጽኩም ዳግማይ ሕተቱ።</i>",
        "om": "⚠️ <b>Gaaffiin kaffaltii keessanii kufaa ta'eera</b>\n━━━━━━━━━━━━━━━━━━━━\n💰 Maallaqni gaafatame <b>{amount:.2f} Birrii</b> gara haftee komishinii keessaniitti deebi'eera.\n\n<i>Maaloo odeeffannoo Telebirr ykn baankii sirrii ta'uu mirkaneeffachuun irra deebi'aatii gaafadhaa.</i>"
    },

    "gift_game_title": {
        "am": "🎁 <b>የዕለቱ ነፃ መጽሐፍ ስጦታ</b>",
        "en": "🎁 <b>Daily Free Book Giveaway</b>",
        "ti": "🎁 <b>ናይ ሎሚ ነጻ መጽሓፍ ሽልማት</b>",
        "om": "🎁 <b>Badhaasa Kitaaba Har'aa</b>"
    },
    "gift_how_it_works": {
        "am": "🔥 <b>ውድድሩ እንዴት ይሰራል?</b>\nበየቀኑ በቲክቶክ ቪዲዮ ላይ አንድ ሚስጥራዊ አዎንታዊ ቃል ይተላለፋል። ቃሉን በትክክል ቀድመው የመለሱ <b>5 ፈጣኖች</b> ከቤተ-መጽሐፍታችን የፈለጉትን መጽሐፍ ወይም <b>25 ነፃ መልዕክቶች</b> በነፃ ይሸለማሉ!\n\n🏆 <b>የዛሬ ቀሪ የአሸናፊዎች ቦታ፦</b> <b>{remaining} / 5</b>\n\n💡 <i>(ምርጫዎ የተሳሳተ ቢሆንም እንኳን ለመረጡት ቃል ልብ የሚነካ ጥልቅ የስነ-ልቦና ትንታኔ ያገኛሉ!)</i>\n\n👇 <b>በቲክቶክ የተላለፈው የዛሬው ቃል የትኛው ነው? ይምረጡ፦</b>",
        "en": "🔥 <b>How the giveaway works:</b>\nA daily secret positive affirmation word is revealed in our TikTok video. The first <b>5 fast participants</b> who select the correct word win ANY book from our library or <b>25 free messages</b> completely free!\n\n🏆 <b>Remaining winner spots today:</b> <b>{remaining} / 5</b>\n\n💡 <i>(Even if your guess is wrong, you will receive an uplifting psychological analysis for the word you chose!)</i>\n\n👇 <b>Which secret word was featured on TikTok today? Choose below:</b>",
        "ti": "🔥 <b>እቲ ውድድር ከመይ ይሰርሕ?</b>\nመዓልታዊ ኣብ ናይ ቲክቶክ ቪድዮ ሓደ ምስጢራዊ ኣዎንታዊ ቃል ይልቀቕ። ነቲ ቃል ቀዲሞም ብትኽክል ዝመለሱ <b>5 ቅልጡፋት</b> ካብ መጻሕፍቲ ቤትና ዝደለይዎ መጽሓፍ ወይ <b>25 ናጻ መልእኽትታት</b> ብናጻ ይሸለሙ!\n\n🏆 <b>ናይ ሎሚ ዝተረፈ ናይ ተዓወቲ ቦታ፦</b> <b>{remaining} / 5</b>\n\n💡 <i>(ምርጫኹም እንተተጋገየ'ኳ ንዝመረጽኩምዎ ቃል ልቢ ዝትንክፍ ዕሙቕ ናይ ስነ-ኣእምሮ ትንታነ ክትረኽቡ ኢኹም!)</i>\n\n👇 <b>ሎሚ ኣብ ቲክቶክ ዝተሓላለፈ ምስጢራዊ ቃል ኣየናይ እዩ? ምረጹ፦</b>",
        "om": "🔥 <b>Dorgommiin kun akkamitti hojjeta?</b>\nGuyyaa guyyaan viidiyoo TikTok irratti jechi iccitii jajjabeessaa ta'e ni darba. Namoonni dafanii deebisan <b>5 ariifattoonni</b> kitaabota keenya keessaa kitaaba barbaadan ykn <b>ergaawwan bilisaa 25</b> badhaafamu!\n\n🏆 <b>Bakki mo'attootaa har'aa kan hafe:</b> <b>{remaining} / 5</b>\n\n💡 <i>(Filannoon keessan dogoggora yoo ta'ellee jecha filattaniif qaaccessa xiin-sammuu gadi fago argattu!)</i>\n\n👇 <b>Jechi iccitii har'aa TikTok irratti darbe isa kami? Filadhaa:</b>"
    },
    "gift_already_won": {
        "am": "🏆 <b>እርስዎ ቀደም ሲል የ{reward} አሸናፊ ሆነዋል!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nያሸነፉት ሽልማት ወደ አካውንትዎ ገቢ ሆኗል።\n\nውድድሩ ለሁሉም ወገኖች እኩል ዕድል ለመስጠት በአንድ ሰው <b>1 ጊዜ ብቻ</b> የሚፈቀድ ነው።\n\nየዕለቱን አነቃቂ የስነ-ልቦና ምክር በቲክቶክ መከታተልዎን ይቀጥሉ! ✨",
        "en": "🏆 <b>You have already won {reward}!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nYour reward has been credited to your account.\n\nTo ensure fair opportunity for everyone, this giveaway is limited to <b>once per user</b>.\n\nKeep following our daily psychological insights on TikTok! ✨",
        "ti": "🏆 <b>ንስኹም ኣቐዲምኩም ናይ {reward} ተዓዋቲ ኮይንኩም ኢኹም!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nዝተዓወትኩምዎ ሽልማት ኣብ ሕሳብኩም ኣትዩ ኣሎ።\n\nእዚ ውድድር ንኹሉ ማዕረ ዕድል ንምሃብ ንሓደ ሰብ <b>1 ግዜ ጥራይ</b> ዝፍቀድ እዩ።\n\nመዓልታዊ ናይ ስነ-ኣእምሮ ምኽሪ ኣብ ቲክቶክ ምክትታልኩም ቀጽሉ! ✨",
        "om": "🏆 <b>Kanaan dura {reward} mo'attaniittu!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nBadhaasni keessan herrega keessanitti galeera.\n\nNamoota hundaaf carraa wal-qixa kennuuf dorgommiin kun nama tokkoof <b>yeroo 1 qofa</b> hayyamama.\n\nGorsa xiin-sammuu guyyaa guyyaa TikTok irratti hordofuu keessan itti fufaa! ✨"
    },
    "gift_already_attempted": {
        "am": "⏳ <b>ለዛሬ ተሳትፈዋል!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nበዛሬው ዙር <b>«{word}»</b> በማለት {status}።\n\nውድድሩ በቀን አንድ ጊዜ ብቻ የሚሞከር ሲሆን፣ አዲስ ዙር <b>ነገ ጠዋት 4:00 ሰዓት</b> ላይ ይጀመራል!\n\n⏳ <b>ለቀጣዩ ዙር የቀረው ጊዜ፦</b> {time_left}\n\n💡 <b>የነገውን ሚስጥራዊ ቃል ቀድመው ለማወቅ፦</b>\nቲክቶክ ቻናላችንን ይከታተሉ! 👇",
        "en": "⏳ <b>You have already participated today!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nIn today's round you selected <b>«{word}»</b> ({status}).\n\nEach participant gets one attempt per day. A new cycle begins <b>tomorrow at 10:00 AM EAT</b>!\n\n⏳ <b>Time left until next round:</b> {time_left}\n\n💡 <b>To catch tomorrow's secret word early:</b>\nFollow our TikTok channel! 👇",
        "ti": "⏳ <b>ንሎሚ ተሳቲፍኩም ኢኹም!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nኣብ ናይ ሎሚ ዙር <b>«{word}»</b> ብምባል {status}።\n\nእዚ ውድድር ኣብ መዓልቲ ሓደ ግዜ ጥራይ ዝፍተን ኮይኑ፡ ሓድሽ ዙር <b>ጽባሕ ንግሆ ሰዓት 4:00</b> ይጅምር!\n\n⏳ <b>ንዝቕጽል ዙር ዝተረፈ ግዜ፦</b> {time_left}\n\n💡 <b>ናይ ጽባሕ ምስጢራዊ ቃል ኣቐዲምኩም ንምፍላጥ፦</b>\nናይ ቲክቶክ ቻናልና ተኸታተሉ! 👇",
        "om": "⏳ <b>Har'aaf hirmaattaniittu!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nMarsaa har'aa keessatti <b>«{word}»</b> jechuun {status}።\n\nDorgommiin kun guyyaatti yeroo tokko qofa kan yaalamu yoo ta'u, marsaan haaraan <b>bor ganama sa'aatii 4:00 (10:00 AM)</b> eegala!\n\n⏳ <b>Yeroon marsaa itti aanuuf hafe:</b> {time_left}\n\n💡 <b>Jecha iccitii borii dursitanii beekuuf:</b>\nChaanaalii TikTok keenya hordofaa! 👇"
    },
    "gift_status_correct": {
        "am": "ትክክለኛውን ቃል መርጠው ነበር",
        "en": "which was the correct word",
        "ti": "ትኽክለኛ ቃል መሪጽኩም ኔርኩም",
        "om": "jechi filattan sirrii ture"
    },
    "gift_status_wrong": {
        "am": "የተሳሳተ ቃል መርጠው ነበር",
        "en": "which was incorrect",
        "ti": "ግጉይ ቃል መሪጽኩም ኔርኩም",
        "om": "jechi filattan dogoggora ture"
    },
    "gift_alert_already_attempted": {
        "am": "ለዛሬ ተሳትፈዋል! በቀን 1 ጊዜ ብቻ ነው የሚፈቀደው።",
        "en": "You have already participated today! Only 1 attempt per day is allowed.",
        "ti": "ንሎሚ ተሳቲፍኩም ኢኹም! ኣብ መዓልቲ 1 ግዜ ጥራይ እዩ ዝፍቀድ።",
        "om": "Har'aaf hirmaattaniittu! Guyyaatti yeroo 1 qofa hayyamama."
    },
    "gift_alert_already_won": {
        "am": "ቀደም ሲል ሽልማት ወስደዋል!",
        "en": "You have already claimed your reward!",
        "ti": "ኣቐዲምኩም ሽልማት ወሲድኩም ኢኹም!",
        "om": "Kanaan dura badhaasa fudhattaniittu!"
    },
    "gift_alert_spots_filled": {
        "am": "ይቅርታ፣ የዛሬ 5 ቦታዎች ሞልተዋል!",
        "en": "Sorry, all 5 spots are filled for today!",
        "ti": "ይቕሬታ፣ ናይ ሎሚ 5 ቦታታት መሊኦም እዮም!",
        "om": "Dhiifama, bakkeewwan 5 har'aa guutamaniiru!"
    },
    "gift_win_congrats": {
        "am": "🎉🎉 <b>ድንቅ ነው! በትክክል መልሰዋል!</b>\n\n🏆 ዛሬ በቲክቶክ የተላለፈውን ሚስጥራዊ ቃል ቀድመው ከመለሱት ውስጥ <b>{rank}</b> በመሆን አሸንፈዋል! 🥇\n\n🎁 <b>የእርስዎ ሽልማት፦</b>\nከታች ካሉት አማራጮች <b>25 ነፃ መልዕክቶች</b> ወይም የፈለጉትን <b>1 ነፃ መጽሐፍ</b> ይምረጡ፤ ወዲያውኑ ይሰጥዎታል! 👇",
        "en": "🎉🎉 <b>Brilliant! You guessed correctly!</b>\n\n🏆 You are among today's first correct guessers, finishing in <b>rank {rank}</b>! 🥇\n\n🎁 <b>Your Reward:</b>\nChoose either <b>25 free messages</b> or ANY <b>1 free book</b> below to claim it immediately! 👇",
        "ti": "🎉🎉 <b>ብሉጽ! ብትኽክል መሊስኩም!</b>\n\n🏆 ሎሚ ኣብ ቲክቶክ ዝተሓላለፈ ምስጢራዊ ቃል ቀዲሞም ካብ ዝመለሱ <b>{rank}</b> ብምዃን ተዓዊትኩም ኣለኹም! 🥇\n\n🎁 <b>ናይ ሽልማትኩም ምርጫ፦</b>\nካብዞም ኣብ ታሕቲ ዘለዉ ኣማራጺታት <b>25 ናጻ መልእኽትታት</b> ወይ ዝደለኹምዎ <b>1 ናጻ መጽሓፍ</b> ምረጹ፤ ብቕጽበት ክወሃበኩም እዩ! 👇",
        "om": "🎉🎉 <b>Baga gammaddan! Sirriitti deebistaniittu!</b>\n\n🏆 Jecha iccitii TikTok irratti darbe warra dafanii deebisan keessaa <b>sadarkaa {rank}ffaa</b> ta'uun mo'attaniittu! 🥇\n\n🎁 <b>Filannoo Badhaasa Keessanii:</b>\nFilannoowwan armaan gadii keessaa <b>ergaawwan bilisaa 25</b> ykn <b>kitaaba bilisaa 1</b> filadhaa; battalumatti isiniif kennama! 👇"
    },
    "gift_late_congrats": {
        "am": "✅ <b>በትክክል መልሰዋል!</b>\n\nየዛሬው ሚስጥራዊ ቃል በእርግጥም <b>«{word}»</b> ነበር!\n\n🏃‍♂️ <b>ነገር ግን...</b> የዛሬዎቹ <b>5 ፈጣን አሸናፊዎች</b> ቀድመው ቦታውን ሞልተዋል!\n\n⏰ <b>ተስፋ አይቁረጡ!</b> አዲስ ዙር <b>ነገ ጠዋት 4:00 ሰዓት</b> ላይ ይጀመራል፤ ቀድመው በመመለስ የነፃ መጽሐፍ ወይም የ25 መልዕክት አሸናፊ ይሁኑ! 👇",
        "en": "✅ <b>You answered correctly!</b>\n\nToday's secret word was indeed <b>«{word}»</b>!\n\n🏃‍♂️ <b>However...</b> all <b>5 winner spots</b> have already been claimed for today!\n\n⏰ <b>Don't give up!</b> A brand new round begins <b>tomorrow at 10:00 AM EAT</b>. Be the first to answer and win a free book or 25 messages! 👇",
        "ti": "✅ <b>ብትኽክል መሊስኩም!</b>\n\nናይ ሎሚ ምስጢራዊ ቃል ብሓቂ <b>«{word}»</b> ነይሩ!\n\n🏃‍♂️ <b>ይኹን እምበር...</b> ናይ ሎሚ <b>5 ቅልጡፋት ተዓወቲ</b> ኣቐዲሞም ነቲ ቦታ መሊኦምዎ ኣለዉ!\n\n⏰ <b>ተስፋ ኣይትቑረጹ!</b> ሓድሽ ዙር <b>ጽባሕ ንግሆ ሰዓት 4:00</b> ይጅምር። ቀዲምኩም ብምምላስ ናይ ነጻ መጽሓፍ ወይ 25 መልእኽቲ ተዓዋቲ ኩኑ! 👇",
        "om": "✅ <b>Sirriitti deebistaniittu!</b>\n\nJechi iccitii har'aa dhugumayyuu <b>«{word}»</b> ture!\n\n🏃‍♂️ <b>Haa ta'u malee...</b> bakkeewwan <b>mo'attoota 5</b> har'aa kanaan dura guutamaniiru!\n\n⏰ <b>Abdi hin kutatinaa!</b> Marsaan haaraan <b>bor ganama sa'aatii 4:00 (10:00 AM)</b> eegala. Dursitanii deebisuun kitaaba bilisaa ykn ergaawwan 25 mo'adhaa! 👇"
    },
    "gift_wrong_answer": {
        "am": "❌ <b>የዛሬው የቲክቶክ ሚስጥራዊ ቃል አልነበረም!</b>\n\nየዛሬው ትክክለኛ ቃል፦ <b>«{word}»</b> ነበር።\n\nአይዞዎት! ቃልዎ ለውድድሩ ባይሆንም፣ መልዕክቱ ግን ለእርስዎ የተላከ እውነተኛ ጥንካሬ ነው።\n\n⏰ <b>ቀጣይ ዕድል፦</b> አዲስ ዙር <b>ነገ ጠዋት 4:00 ሰዓት</b> ላይ ይጀመራል። የነገውን ቃል እንዳያመልጥዎ ቲክቶክ ቻናላችንን ይከታተሉ! 👇",
        "en": "❌ <b>That was not today's secret word!</b>\n\nToday's correct word was: <b>«{word}»</b>.\n\nTake heart! Even if your word wasn't the secret answer, its message is true strength for you today.\n\n⏰ <b>Next Chance:</b> A new round begins <b>tomorrow at 10:00 AM EAT</b>. Don't miss tomorrow's word on our TikTok channel! 👇",
        "ti": "❌ <b>ናይ ሎሚ ናይ ቲክቶክ ምስጢራዊ ቃል ኣይነበረን!</b>\n\nናይ ሎሚ ትኽክለኛ ቃል፦ <b>«{word}»</b> ነይሩ።\n\nኣይትጨነቑ! እቲ ቃል ንውድድር እንተዘይኮነ፡ መልእኽቱ ግን ንዓኹም ናይ ሓቂ ብርታት እዩ።\n\n⏰ <b>ቀጻሊ ዕድል፦</b> ሓድሽ ዙር <b>ጽባሕ ንግሆ ሰዓት 4:00</b> ይጅምር። ናይ ጽባሕ ቃል ከየምልጠኩም ናይ ቲክቶክ ቻናልና ተኸታተሉ! 👇",
        "om": "❌ <b>Kun jecha iccitii TikTok har'aa hin turre!</b>\n\nJechi sirriin har'aa: <b>«{word}»</b> ture.\n\nJabaadhaa! Jechi kun dorgommiif ta'uu baatus, dhaamsi isaa garuu humna dhugaa isiniif ta'a.\n\n⏰ <b>Carraa Itti Aanu:</b> Marsaan haaraan <b>bor ganama sa'aatii 4:00 (10:00 AM)</b> eegala. Jechi borii akka isin hin dabarre chaanaalii TikTok keenya hordofaa! 👇"
    },
    "gift_claim_msgs_success": {
        "am": "🎊🎊 <b>እንኳን ደስ አለዎት!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n💬 <b>25 ነፃ መልዕክቶች</b> ወደ አካውንትዎ ገቢ ሆነዋል! 🏆\n\nአሁን ከኤአይ አማካሪው ጋር በነፃ ማውራት፣ ማንኛውንም ጥያቄ መጠየቅ እና መወያየት ይችላሉ። መልካም ቆይታ! 🌟",
        "en": "🎊🎊 <b>Congratulations!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n💬 <b>25 free messages</b> have been credited to your account! 🏆\n\nYou can now continue chatting with the AI counselor, ask any questions, and explore solutions freely. Welcome! 🌟",
        "ti": "🎊🎊 <b>እንኳዕ ደስ በለኩም!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n💬 <b>25 ናጻ መልእኽትታት</b> ናብ ኣካውንትኩም ኣትዩ ኣሎ! 🏆\n\nሕጂ ምስቲ ናይ AI ኣማኻሪ ብነጻ ክትዛረቡ፣ ዝኾነ ሕቶ ክትሓቱ ትኽእሉ ኢኹም። ጽቡቕ ጻንሒት! 🌟",
        "om": "🎊🎊 <b>Baga gammaddan!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n💬 <b>Ergaawwan bilisaa 25</b> gara herrega keessaniitti dabalameera! 🏆\n\nAmma gorsaa AI wajjin bilisaan mari'achuu fi gaaffii kamiyyuu gaafachuu dandeessu. Turtii gaarii! 🌟"
    },
    "gift_claim_book_success": {
        "am": "🎊🎊 <b>እንኳን ደስ አለዎት!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n📖 <b>«{title}»</b> የተሰኘው ሙሉ መጽሐፍ በስጦታ <b>ለዘላለም በነፃ</b> ተከፍቶልዎታል! 🏆\n\nከታች ያለውን ቁልፍ ተጭነው ማንበብ መጀመር ይችላሉ። መልካም ንባብ! 🌟",
        "en": "🎊🎊 <b>Congratulations!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n📖 The full book <b>«{title}»</b> has been unlocked for you <b>permanently for free</b>! 🏆\n\nTap the button below to start reading. Enjoy your reading! 🌟",
        "ti": "🎊🎊 <b>እንኳዕ ደስ በለኩም!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n📖 እቲ ምሉእ መጽሓፍ <b>«{title}»</b> ብውህብቶ <b>ንዘለኣለም ብናጻ</b> ተኸፊቱልኩም ኣሎ! 🏆\n\nኣብ ታሕቲ ዘሎ ቁልፊ ብምጥዋቕ ምንባብ ክትጅምሩ ትኽእሉ ኢኹም። ጽቡቕ ንባብ! 🌟",
        "om": "🎊🎊 <b>Baga gammaddan!</b>\n━━━━━━━━━━━━━━━━━━━━\n\n📖 Kitaabni guutuun <b>«{title}»</b> jedhamu kennaadhaan <b>bara baraan bilisaan</b> isiniif banameera! 🏆\n\nQabduu armaan gadii tuquun dubbisuu jalqabuu dandeessu. Dubbisa gaarii! 🌟"
    },
    "btn_gift_tiktok_today": {
        "am": "📱 የዛሬውን ቃል በቲክቶክ እይ",
        "en": "📱 Watch Today's Word on TikTok",
        "ti": "📱 ናይ ሎሚ ቃል ኣብ ቲክቶክ ርኣዩ",
        "om": "📱 Jecha Har'aa TikTok irratti Ilaalaa"
    },
    "btn_gift_tiktok_tomorrow": {
        "am": "📱 የነገውን ቃል በቲክቶክ እይ",
        "en": "📱 Watch Tomorrow's Word on TikTok",
        "ti": "📱 ናይ ጽባሕ ቃል ኣብ ቲክቶክ ርኣዩ",
        "om": "📱 Jecha Borii TikTok irratti Ilaalaa"
    },
    "btn_read_won_book": {
        "am": "📚 ያሸነፉትን መጽሐፍ አንብብ",
        "en": "📚 Read Your Won Book",
        "ti": "📚 ዝተዓወትኩምዎ መጽሓፍ ኣንብቡ",
        "om": "📚 Kitaaba Mo'attan Dubbisaa"
    },
    "btn_read_book_now": {
        "am": "📚 መጽሐፉን አሁኑኑ አንብብ",
        "en": "📚 Read Book Now",
        "ti": "📚 ነቲ መጽሓፍ ሕጂ ኣንብቡ",
        "om": "📚 Kitaaba Amma Dubbisaa"
    },
    "btn_claim_free_msgs": {
        "am": "💬 25 ነፃ መልዕክቶች ውሰድ",
        "en": "💬 Claim 25 Free Messages",
        "ti": "💬 25 ናጻ መልእኽትታት ውሰዱ",
        "om": "💬 Ergaawwan Bilisaa 25 Fudhadhaa"
    },
    "btn_claim_book_fmt": {
        "am": "🎁 «{title}» ውሰድ",
        "en": "🎁 Claim «{title}»",
        "ti": "🎁 «{title}» ውሰዱ",
        "om": "🎁 «{title}» Fudhadhaa"
    },
    "btn_already_owned_fmt": {
        "am": "✅ {title} (ቀድመው የወሰዱት)",
        "en": "✅ {title} (Already Unlocked)",
        "ti": "✅ {title} (ኣቐዲምኩም ዝወሰድኩምዎ)",
        "om": "✅ {title} (Kanaan dura kan fudhattan)"
    },

    "library_title": {
        "am": "📚 <b>የእርስዎ መጻሕፍት</b>",
        "en": "📚 <b>Your Library</b>",
        "ti": "📚 <b>ናይ መጻሕፍቲ ቤትኩም</b>",
        "om": "📚 <b>Mana Dubbisa Keessanii</b>"
    },
    "library_empty": {
        "am": "📚 ገና የገዙት ወይም የተከራዩት መጽሐፍ የለም። ከታች ያለውን ቁልፍ ተጭነው መጻሕፍት ቤቱን ይጎብኙ!",
        "en": "📚 You have not purchased or rented any books yet. Tap below to visit the library!",
        "ti": "📚 ዛጊት ዝገዛእኩምዎ ወይ ዝተኻረይኩምዎ መጽሓፍ የለን። ኣብ ታሕቲ ዘሎ ቁልፊ ብምጥዋቕ ናይ መጻሕፍቲ ቤት ጎብኙ!",
        "om": "📚 Hanga ammaatti kitaaba bitattan ykn kireeffattan hin qabdan. Qabduu armaan gadii tuquun mana dubbisaa daawwadhaa!"
    },
    "btn_open_library": {
        "am": "📚 መጻሕፍት ቤት ክፈት",
        "en": "📚 Open Library",
        "ti": "📚 መጻሕፍቲ ቤት ክፈቱ",
        "om": "📚 Mana Dubbisaa Banaa"
    },
    "rental_badge": {
        "am": "ኪራይ — ቀሪ {days} ቀናት",
        "en": "Rental — {days} days left",
        "ti": "ኪራይ — ዝተረፈ {days} መዓልታት",
        "om": "Kiraa — Guyyoota {days} hafe"
    },
    "full_book_badge": {
        "am": "ሙሉ መጽሐፍ",
        "en": "Full Book",
        "ti": "ምሉእ መጽሓፍ",
        "om": "Kitaaba Guutuu"
    },
    "expired_badge": {
        "am": "የኪራይ ጊዜው ያለፈ",
        "en": "Rental Expired",
        "ti": "ናይ ኪራይ ግዜ ዝሓለፎ",
        "om": "Yeroon Kiraa Darbe"
    },
    "book_unlocked_rental": {
        "am": "🎉 <b>እንኳን ደስ አለዎት!</b>\n\n📖 <b>«{title}»</b> ሙሉ መጽሐፍ <b>ለ {days} ቀናት (ኪራይ)</b> ተከፍቶልዎታል!\n\nከታች ያለውን ቁልፍ ተጭነው በ<b>'📚 የኔ መጻሕፍት'</b> ስር ማንበብ ይችላሉ 👇",
        "en": "🎉 <b>Congratulations!</b>\n\n📖 The full book <b>«{title}»</b> has been unlocked for you for <b>{days} days (Rental)</b>!\n\nTap the button below to read it under <b>'📚 My Books'</b> 👇",
        "ti": "🎉 <b>እንኳዕ ደስ በለኩም!</b>\n\n📖 እቲ ምሉእ መጽሓፍ <b>«{title}»</b> ን <b>{days} መዓልታት (ኪራይ)</b> ተኸፊቱልኩም ኣሎ!\n\nኣብ ታሕቲ ዘሎ ቁልፊ ብምጥዋቕ ኣብ <b>'📚 ናተይ መጻሕፍቲ'</b> ከተንብቡ ትኽእሉ ኢኹም 👇",
        "om": "🎉 <b>Baga gammaddan!</b>\n\n📖 Kitaabni guutuun <b>«{title}»</b> guyyoota <b>{days}f (Kiraadhaan)</b> isiniif banameera!\n\nQabduu armaan gadii tuquun <b>'📚 Kitaabota Koo'</b> keessatti dubbisuu dandeessu 👇"
    },
    "book_unlocked_perm": {
        "am": "🎉 <b>እንኳን ደስ አለዎት!</b>\n\n📖 <b>«{title}»</b> ሙሉ መጽሐፍ <b>ለዘላለም በነፃ</b> ተከፍቶልዎታል!\n\nከታች ያለውን ቁልፍ ተጭነው በ<b>'📚 የኔ መጻሕፍት'</b> ስር ማንበብ ይችላሉ 👇",
        "en": "🎉 <b>Congratulations!</b>\n\n📖 The full book <b>«{title}»</b> has been unlocked for you <b>permanently</b>!\n\nTap the button below to read it under <b>'📚 My Books'</b> 👇",
        "ti": "🎉 <b>እንኳዕ ደስ በለኩም!</b>\n\n📖 እቲ ምሉእ መጽሓፍ <b>«{title}»</b> <b>ንዘለኣለም ብናጻ</b> ተኸፊቱልኩም ኣሎ!\n\nኣብ ታሕቲ ዘሎ ቁልፊ ብምጥዋቕ ኣብ <b>'📚 ናተይ መጻሕፍቲ'</b> ከተንብቡ ትኽእሉ ኢኹም 👇",
        "om": "🎉 <b>Baga gammaddan!</b>\n\n📖 Kitaabni guutuun <b>«{title}»</b> <b>bara baraan bilisaan</b> isiniif banameera!\n\nQabduu armaan gadii tuquun <b>'📚 Kitaabota Koo'</b> keessatti dubbisuu dandeessu 👇"
    },

    "tip_title": {
        "am": "💛 <b>እውነታውን ይደግፉ</b>",
        "en": "💛 <b>Back the Truth</b>",
        "ti": "💛 <b>ንሓቂ ደገፍኩም ሃቡ</b>",
        "om": "💛 <b>Dhugaa Deggeraa</b>"
    },
    "tip_body": {
        "am": "ይህንን AI የገነባነው ሰዎች እንዲያድጉ እና ከራሳቸው ጋር እንዲታረቁ የሚያስፈልጋቸው ያልተበረዘ እውነት እንጂ የውሸት ማባበያ አይደለም ብለን ስለምናምን ነው። በየቀኑ በሺዎች የሚቆጠሩ ሰዎችን የሚሞግት እና ጥልቅ የስነ-ልቦና ትንታኔ የሚሰጥ ሲስተም ማስተዳደር ቀላል አይደለም።\n\nበዚህ ውይይት ውስጥ ህይወትዎን የሚቀይር አዲስ እይታ ካገኙ፣ እና ይህ አገልግሎት ለሌሎችም እንዳይቋረጥ ከፈለጉ፣ ከጀርባ ያለውን ቡድን ያበረታቱ።\n\nከታች ካሉት አማራጮች አንዱን ይምረጡ፦",
        "en": "We built this AI because we believe people need the unfiltered truth to grow—not just comforting lies. Running an uncompromised system that challenges thousands of people daily takes serious resources.\n\nIf these conversations have shifted something inside you, and you want to ensure this system stays sharp and available for those who need to hear the hard truth, back the team that made it possible.\n\nChoose an amount below:",
        "ti": "እዚ AI ዝሃነጽናዮ፡ ሰባት ንክዓብዩ ዘድልዮም ዘይተበረዘ ሓቂ እምበር ናይ ሓሶት መደዓዓሲ ኣይኮነን ኢልና ስለንኣምን እዩ። ኣብ ነፍሲ ወከፍ መዓልቲ ንኣሽሓት ሰባት ዝሞግትን ዕሙቕ ዝበለ ናይ ስነ-ኣእምሮ ትንታነ ዝህብን ስርዓት ምምሕዳር ቀሊል ኣይኮነን።\n\nኣብዚ ዕላል ህይወትኩም ዝቕይር ሓድሽ ኣረኣእያ እንተረኺብኩም፡ ከምኡ'ውን እዚ ኣገልግሎት ንኻልኦት ከይቋረጽ እንተደሊኹም፡ ነቶም ኣብ ድሕሪ እዚ ዘለዉ ጉጅለ ኣበራትዑዎም።\n\nካብዞም ኣብ ታሕቲ ዘለዉ ኣማራጺታት ሓደ ምረጹ፦",
        "om": "AI kana kan ijaarre namoonni akka guddattaniif dhugaa qullaa malee soba nama jajjabeessu akka hin barbaadne waan amannuuf. Sirna guyyoota hundumaa namoota kumaatamaan lakkaa'aman qoratu fi qaaccessa xiin-sammuu gadi fago kennu bulchuun salphaa miti.\n\nMarii kana keessatti ilaalcha haaraa jireenya keessan jijjiiru yoo argattan, fi tajaajilli kun warra kaaniif akka hin cinne yoo barbaaddan, garee kana duuba jiru jajjabeessaa.\n\nFilannoowwan armaan gadii keessaa tokko filadhaa:"
    },
    "tip_pay_btn": {
        "am": "💳 {amount} ብር ይሸልሙ",
        "en": "💳 Tip {amount} Birr",
        "ti": "💳 {amount} ብር ሽለሙ",
        "om": "💳 Birrii {amount} badhaasaa"
    },
    "tip_payment_text": {
        "am": "☕ <b>{amount} ብር ስጦታ</b>\nእባክዎ ከታች ያለውን ቁልፍ ተጭነው ስጦታዎን ይላኩ። ከልብ እናመሰግናለን!",
        "en": "☕ <b>Gift of {amount} Birr</b>\nPlease click the button below to send your gift. Thank you so much!",
        "ti": "☕ <b>{amount} ብር ውህብቶ</b>\nበጃኹም ኣብ ታሕቲ ዘሎ መርገጺ ብምጥዋቕ ውህብቶኹም ስደዱ። ካብ ልቢ ነመስግን!",
        "om": "☕ <b>Kennaa Birrii {amount}</b>\nMaaloo cuqqaallii armaan gadii tuquun kennaa keessan ergaa. Guddaa galatoomaa!"
    },

    "banned": {
        "am": "🚫 ይህ አካውንት ታግዷል።",
        "en": "🚫 This account has been banned.",
        "ti": "🚫 እዚ ኣካውንት ተኣጊዱ ኣሎ።",
        "om": "🚫 Herregni kun uggurameera."
    },
    "text_only": {
        "am": "እባክዎ ፅሁፍ ብቻ ይላኩ።",
        "en": "Please send text only.",
        "ti": "በጃኹም ጽሑፍ ጥራይ ስደዱ።",
        "om": "Maaloo barreeffama qofa ergaa."
    },
    "ai_error": {
        "am": "⚠️ ይቅርታ፣ ምላሽ ማግኘት አልተቻለም። እባክዎ እንደገና ይሞክሩ።",
        "en": "⚠️ Sorry, unable to get a response. Please try again.",
        "ti": "⚠️ ይቕሬታ፣ ግብረ መልሲ ምርካብ ኣይተኻእለን። በጃኹም እንደገና ፈትኑ።",
        "om": "⚠️ Dhiifama, deebii argachuun hin danda'amne. Maaloo irra deebi'aa yaalaa."
    },
    "tech_error": {
        "am": "⚠️ የቴክኒክ ችግር: {err}",
        "en": "⚠️ Technical Error: {err}",
        "ti": "⚠️ ቴክኒካዊ ጸገም: {err}",
        "om": "⚠️ Rakkoo Teeknikaa: {err}"
    },
    "no_history_prompt": {
        "am": "💡 <b>እኔ ከጎንዎ ነኝ፤ እባክዎ የሚያስጨንቅዎትን ነገር ወይም ያለዎትን ስሜት በነፃነት ያካፍሉኝ...</b>",
        "en": "💡 <b>I am here for you; please feel free to share what's bothering you or how you're feeling...</b>",
        "ti": "💡 <b>ኣነ ኣብ ጎድንኹም እየ፤ በጃኹም ዘጨንቐኩም ነገር ወይ ዘለኩም ስምዒት ብነጻነት ኣካፍሉኒ...</b>",
        "om": "💡 <b>Ani cinaa keessan jira; maaloo wanta isin yaaddessu ykn miira isinitti dhaga'amu bilisaan natti himaa...</b>"
    },
    "legacy_redirect": {
        "am": "ይህ አገልግሎት ተዘግቷል። ወደ አዲሱ ገፅ እንመልስዎታለን...",
        "en": "This service has been closed. Redirecting you to the new page...",
        "ti": "እዚ ኣገልግሎት ተዓጽዩ ኣሎ። ናብቲ ሓድሽ ገጽ ክንምልሰኩም ኢና...",
        "om": "Tajaajilli kun cufameera. Gara fuula haaraatti isin deebisaa jirra..."
    },
    "lang_changed": {
        "am": "✅ ቋንቋው ተቀይሯል!",
        "en": "✅ Language changed!",
        "ti": "✅ ቋንቋ ተቐይሩ እዩ!",
        "om": "✅ Afaan jijjiirameera!"
    },
    "gift_notification": {
        "am": "🎁 <b>እንኳን ደስ አለዎት!</b>\n\nከአስተዳዳሪ ተጨማሪ {amount} የአማካሪ መልዕክቶች በስጦታ ተሰጥቶዎታል።",
        "en": "🎁 <b>Congratulations!</b>\n\nYou have been gifted an additional {amount} counselor messages from the admin.",
        "ti": "🎁 <b>እንኳዕ ደስ በለኩም!</b>\n\nካብ ኣማሓዳሪ ተወሳኺ ናይ {amount} ኣማኻሪ መልእኽትታት ብውህብቶ ተዋሂቡኩም ኣሎ።",
        "om": "🎁 <b>Baga gammaddan!</b>\n\nBulchaa irraa dabalataan ergaawwan gorsaa {amount} kennaan isiniif kennamaniiru."
    },
    "unlimited_display": {
        "am": "♾️ ያልተገደበ (እስከ {date})",
        "en": "♾️ Unlimited (until {date})",
        "ti": "♾️ ዘይተደረተ (ክሳብ {date})",
        "om": "♾️ Daangaa Malee (hanga {date})"
    },

    "last_free_hook_m": {
        "am": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>ይሄ የመጨረሻ ነፃ መልዕክትህ ነበር።</b>\n\nአሁን ነው ትክክለኛው ለውጥ የሚጀምረው — የጀመርነውን ጥልቅ ውይይት ማቋረጥ አያስፈልግም። ስላንተ ብዙ ነገር አስተውያለሁ... ግን ገና ያልነገርኩህ ወሳኝ ነገሮች አሉ። ውይይታችንን ለመቀጠል /topup ተጫን።",
        "en": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>That was your last free message.</b>\n\nThis is exactly where the real breakthrough begins — don't walk away from what we've started. I've already spotted patterns in what you've shared... but there are critical things I haven't told you yet. Press /topup to continue our conversation.",
        "ti": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>እዚ ናይ መወዳእታ ነጻ መልእኽትኻ ነይሩ።</b>\n\nሕጂ እዩ ናይ ብሓቂ ለውጢ ዝጅምር — ዝጀመርናዮ ዕሙቕ ዘተ ምቁራጽ ኣየድልን። ብዛዕባኻ ብዙሕ ነገራት ኣስተብሂለ ኣለኹ... ግን ዛጊት ዘይነገርኩኻ ወሰንቲ ነገራት ኣለዉ። ዕላልና ንምቕጻል /topup ጠውቕ።",
        "om": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>Kun ergaa bilisaa kee isa dhumaa ture.</b>\n\nKan amma jijjiiramni dhugaa itti jalqabu dha — wanta jalqabne addaan hin kutinaa. Waa'ee kee wantoota baay'ee hubadheera... garuu wantoota murteessoo ta'an kan amma iyyuu siif hin himne jiru. Marii keenya itti fufuuf /topup tuqi."
    },
    "last_free_hook_f": {
        "am": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>ይሄ የመጨረሻ ነፃ መልዕክትሽ ነበር።</b>\n\nአሁን ነው ትክክለኛው ለውጥ የሚጀምረው — የጀመርነውን ጥልቅ ውይይት ማቋረጥ አያስፈልግም። ስላንቺ ብዙ ነገር አስተውያለሁ... ግን ገና ያልነገርኩሽ ወሳኝ ነገሮች አሉ። ውይይታችንን ለመቀጠል /topup ተጫኝ።",
        "en": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>That was your last free message.</b>\n\nThis is exactly where the real breakthrough begins — don't walk away from what we've started. I've already spotted patterns in what you've shared... but there are critical things I haven't told you yet. Press /topup to continue our conversation.",
        "ti": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>እዚ ናይ መወዳእታ ነጻ መልእኽትኺ ነይሩ።</b>\n\nሕጂ እዩ ናይ ብሓቂ ለውጢ ዝጅምር — ዝጀመርናዮ ዕሙቕ ዘተ ምቁራጽ ኣየድልን። ብዛዕባኺ ብዙሕ ነገራት ኣስተብሂለ ኣለኹ... ግን ዛጊት ዘይነገርኩኺ ወሰንቲ ነገራት ኣለዉ። ዕላልና ንምቕጻል /topup ጠውቒ።",
        "om": "\n\n━━━━━━━━━━━━━━━━━━━━\n⚡ <b>Kun ergaa bilisaa kee isa dhumaa ture.</b>\n\nKan amma jijjiiramni dhugaa itti jalqabu dha — wanta jalqabne addaan hin kutinaa. Waa'ee kee wantoota baay'ee hubadheera... garuu wantoota murteessoo ta'an kan amma iyyuu siif hin himne jiru. Marii keenya itti fufuuf /topup tuqi."
    }
}

def S(lang, key, **kwargs):
    """Get a localized string. Falls back to Amharic if key missing for language."""
    entry = STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(lang, entry.get("am", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
