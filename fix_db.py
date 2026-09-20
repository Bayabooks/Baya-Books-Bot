import re

with open('database.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('previews_left INTEGER DEFAULT 3', 'previews_left INTEGER DEFAULT 5')
text = text.replace('IFNULL(previews_left, 3)', 'IFNULL(previews_left, 5)')
text = text.replace('return 3, None', 'return 5, None')
text = text.replace('previews_left = 3', 'previews_left = 5')

if 'free_protocol_used' not in text:
    target = '    try:\n        c.execute("ALTER TABLE users ADD COLUMN preview_timer_start TEXT")\n    except:\n        pass'
    replacement = target + '\n    try:\n        c.execute("ALTER TABLE users ADD COLUMN free_protocol_used INTEGER DEFAULT 0")\n    except:\n        pass'
    text = text.replace(target, replacement)

with open('database.py', 'w', encoding='utf-8') as f:
    f.write(text)
