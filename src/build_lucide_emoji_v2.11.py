import base64, csv
from copy import deepcopy
from pathlib import Path
from array import array
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.colorLib.builder import buildCOLR, buildCPAL

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'vendor' / 'lucide.ttf'
MAPPING_CSV = ROOT / 'data' / 'lucide_emoji_mappings_v2.8.csv'
DIST = ROOT / 'dist'
USERSCRIPT_DIR = ROOT / 'userscript'
DATA_DIR = ROOT / 'data'
DIST.mkdir(exist_ok=True)
USERSCRIPT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
VERSION='v2.11'
SHIFT_Y = -72

VS16_BASES = {
    0xA9, 0x203C, 0x2049, 0x2139, 0x2194, 0x2195, 0x2196, 0x2197, 0x2198, 0x2199,
    0x21A9, 0x21AA, 0x2328, 0x23CF, 0x23ED, 0x23EE, 0x23F1, 0x23F2, 0x23F8, 0x23F9,
    0x23FA, 0x25AA, 0x25AB, 0x25B6, 0x25C0, 0x25FB, 0x25FC, 0x2600, 0x2601, 0x2602,
    0x260E, 0x2611, 0x2618, 0x2620, 0x2622, 0x2623, 0x2626, 0x2639, 0x263A, 0x2640,
    0x2642, 0x265F, 0x2660, 0x2663, 0x2665, 0x2666, 0x267B, 0x267E, 0x2692, 0x2694,
    0x2696, 0x2697, 0x2699, 0x269B, 0x26A0, 0x26A7, 0x26C8, 0x26CF, 0x26D1, 0x26D3,
    0x26F0, 0x26F1, 0x26F4, 0x2702, 0x2708, 0x2709, 0x270D, 0x270F, 0x2712, 0x2714,
    0x2716, 0x271D, 0x2733, 0x2734, 0x2744, 0x2747, 0x2763, 0x2764, 0x27A1, 0x2B05,
    0x2B06, 0x2B07, 0x1F17F, 0x1F321, 0x1F324, 0x1F325, 0x1F326, 0x1F327, 0x1F328,
    0x1F329, 0x1F32A, 0x1F32B, 0x1F32C, 0x1F37D, 0x1F396, 0x1F397, 0x1F399, 0x1F39E,
    0x1F39F, 0x1F3CB, 0x1F3CE, 0x1F3D4, 0x1F3D8, 0x1F3D9, 0x1F3DB, 0x1F3DF, 0x1F3F3,
    0x1F3F5, 0x1F3F7, 0x1F43F, 0x1F441, 0x1F54A, 0x1F576, 0x1F579, 0x1F587, 0x1F58A,
    0x1F58B, 0x1F58C, 0x1F58D, 0x1F590, 0x1F5A5, 0x1F5A8, 0x1F5B1, 0x1F5BC, 0x1F5C2,
    0x1F5C3, 0x1F5C4, 0x1F5D1, 0x1F5D2, 0x1F5D3, 0x1F5DD, 0x1F5DE, 0x1F5E1, 0x1F5E3,
    0x1F5E8, 0x1F5EF, 0x1F5FA, 0x1F6CB, 0x1F6CD, 0x1F6CF, 0x1F6E0, 0x1F6E1, 0x1F6E9,
    0x1F6F0, 0x1F6F3,
}

# prune mappings that were too broad or conceptually off
EXCLUDED_CODEPOINTS = {
    # generic person glyph was too broad
    0x1F466, 0x1F467, 0x1F468, 0x1F469, 0x1F471, 0x1F474, 0x1F475, 0x1F9D1, 0x1F9D2, 0x1F9D3, 0x1F9D4,
    # generic users glyph was too broad
    0x1F46A, 0x1F46B, 0x1F46C, 0x1F46D, 0x1FAC2,
    # open-hand glyph was too broad
    0x1F44F, 0x1F450, 0x1F64C, 0x1F91A, 0x1F932, 0x1FAF1, 0x1FAF2, 0x1FAF3, 0x1FAF7, 0x1FAF8,
}


def rgba(hexcolor):
    hexcolor = hexcolor.lstrip('#')
    return (int(hexcolor[0:2],16)/255, int(hexcolor[2:4],16)/255, int(hexcolor[4:6],16)/255, 1.0)

# Explicit per-codepoint colors, including many conventionally-colored emoji.
CP_COLORS = {
    # circles / geometric shapes
    0x1F534:'#ef4444', 0x1F7E0:'#f97316', 0x1F7E1:'#facc15', 0x1F7E2:'#22c55e', 0x1F535:'#2563eb', 0x1F7E3:'#8b5cf6',
    0x26AA:'#d1d5db', 0x26AB:'#374151',
    0x2B55:'#ef4444', 0x1F536:'#f97316', 0x1F537:'#2563eb', 0x1F538:'#facc15', 0x1F539:'#2563eb',
    0x25FB:'#d1d5db', 0x25FC:'#374151', 0x25FD:'#d1d5db', 0x25FE:'#374151', 0x2B1B:'#374151', 0x2B1C:'#d1d5db',

    # hearts
    0x2764:'#ef4444', 0x1F9E1:'#f97316', 0x1F49B:'#facc15', 0x1F49A:'#22c55e', 0x1F499:'#2563eb', 0x1F49C:'#8b5cf6',
    0x1F5A4:'#374151', 0x1F90D:'#d1d5db', 0x1F90E:'#8b5a2b', 0x1F494:'#ef4444', 0x1F493:'#fb7185',
    0x1F496:'#ec4899', 0x1F497:'#f43f5e', 0x1F495:'#f472b6', 0x1F49D:'#f59e0b', 0x1F49F:'#a855f7', 0x2763:'#ef4444',
    0x1FA77:'#f9a8d4',

    # books/notebooks
    0x1F4D5:'#ef4444', 0x1F4D7:'#22c55e', 0x1F4D8:'#2563eb', 0x1F4D9:'#f97316', 0x1F4D3:'#6366f1', 0x1F4D4:'#facc15',
    0x1F4D2:'#10b981', 0x1F4D6:'#60a5fa',

    # pins and office objects conventionally colored
    0x1F4CD:'#ef4444', 0x1F4CC:'#ef4444', 0x1F4CB:'#9ca3af',

    # status / symbols
    0x2705:'#22c55e', 0x274C:'#ef4444', 0x274E:'#ef4444', 0x26A0:'#f59e0b', 0x2753:'#2563eb', 0x2754:'#2563eb',
    0x2755:'#ef4444', 0x2757:'#ef4444', 0x26D4:'#ef4444', 0x1F6AB:'#ef4444',

    # weather/nature
    0x2600:'#facc15', 0x26A1:'#facc15', 0x1F525:'#f97316', 0x2744:'#60a5fa', 0x1F4A7:'#38bdf8', 0x1F4A6:'#38bdf8',
    0x1F308:'#7c3aed', 0x1F31E:'#facc15', 0x1F31F:'#facc15',

    # food/drink explicitly conventional
    0x1F34E:'#ef4444', 0x1F34F:'#65a30d', 0x1F34C:'#facc15', 0x1F352:'#ef4444', 0x1F347:'#8b5cf6', 0x1F955:'#f97316',
    0x1F966:'#16a34a', 0x1F355:'#f59e0b', 0x1F36A:'#b45309', 0x1F36C:'#ec4899', 0x1F36D:'#ef4444', 0x1F37F:'#facc15',
    0x1F382:'#f472b6', 0x1F370:'#f59e0b', 0x1F95A:'#fde68a', 0x1F375:'#16a34a', 0x2615:'#92400e', 0x1F377:'#dc2626',
    0x1F37A:'#f59e0b', 0x1F37B:'#f59e0b', 0x1F378:'#fb7185', 0x1F379:'#f97316', 0x1F37E:'#e5e7eb',

    # transport / misc conventional
    0x1F381:'#ec4899', 0x1F389:'#8b5cf6', 0x1F38A:'#8b5cf6', 0x1F388:'#ef4444', 0x1F3C6:'#f59e0b', 0x1F947:'#f59e0b',
    0x1F948:'#9ca3af', 0x1F949:'#b45309', 0x1F680:'#ef4444', 0x26FD:'#22c55e', 0x1F692:'#ef4444', 0x1F691:'#ef4444',
    0x1F69A:'#f97316', 0x1F68C:'#f59e0b', 0x1F695:'#facc15', 0x1F451:'#f59e0b', 0x1F4A1:'#facc15', 0x1F514:'#f59e0b',
    0x1F4B0:'#22c55e',
}

# Defaults for conceptually colored glyph families.
GLYPH_DEFAULT_COLORS = {
    # faces / people / hands
    'face-grinning':'#facc15', 'face-slightly-smiling':'#facc15', 'face-neutral':'#facc15', 'face-slightly-frowning':'#facc15',
    'annoyed':'#facc15', 'angry':'#f97316', 'user':'#facc15', 'users':'#facc15', 'person-standing':'#facc15', 'baby':'#facc15',
    'hand':'#facc15', 'hand-fist':'#facc15', 'hand-metal':'#facc15', 'hand-heart':'#facc15', 'thumbs-up':'#facc15', 'thumbs-down':'#facc15',
    'biceps-flexed':'#facc15', 'ear':'#facc15', 'nose':'#facc15',
    # explicit object defaults retained from v2.6
    'apple':'#ef4444','banana':'#facc15','cherry':'#ef4444','grape':'#8b5cf6','carrot':'#f97316','broccoli':'#16a34a','bean':'#65a30d','beef':'#a16207',
    'pizza':'#f59e0b','cookie':'#b45309','candy':'#ec4899','candy-cane':'#ef4444','popcorn':'#facc15','cake':'#f472b6','cake-slice':'#f59e0b','ice-cream-cone':'#f3e8ff',
    'ice-cream-2':'#f9a8d4','coffee':'#92400e','wine':'#dc2626','beer':'#f59e0b','martini':'#fb7185','bottle-wine':'#dc2626',
    'sun':'#facc15','sunrise':'#fb923c','sunset':'#f97316','moon':'#fbbf24','moon-star':'#60a5fa','cloud':'#94a3b8','cloud-sun':'#facc15','cloud-rain':'#60a5fa',
    'cloud-lightning':'#facc15','cloud-snow':'#93c5fd','cloud-fog':'#94a3b8','snowflake':'#60a5fa','wind':'#93c5fd','droplets':'#38bdf8','droplet':'#38bdf8','waves':'#38bdf8',
    'flower':'#ec4899','flower-2':'#facc15','leaf':'#22c55e','sprout':'#22c55e','plant-pot':'#22c55e','tree-pine':'#16a34a','tree-deciduous':'#16a34a','palm-tree':'#16a34a','cactus':'#16a34a','mushroom':'#ef4444',
    'flame':'#f97316','sparkles':'#facc15','star':'#facc15','gift':'#ec4899','party-popper':'#8b5cf6','balloon':'#ef4444','trophy':'#f59e0b','award':'#f59e0b','medal':'#f59e0b',
    'traffic-light':'#f59e0b','traffic-cone':'#f97316','fuel':'#22c55e','rocket':'#ef4444','ambulance':'#ef4444','truck':'#f97316','bus':'#f59e0b','bus-front':'#f59e0b','car-taxi-front':'#facc15',
    'crown':'#f59e0b','bell':'#f59e0b','lightbulb':'#facc15','banknote':'#22c55e','parking-meter':'#2563eb','shopping-bag':'#ec4899','handbag':'#7c2d12','ribbon':'#ec4899',
    'gem':'#38bdf8','rainbow':'#7c3aed','earth':'#22c55e','globe':'#3b82f6','volcano':'#dc2626','mountain-snow':'#94a3b8','mountain':'#64748b',
    'book':'#60a5fa', 'notebook':'#6366f1', 'pin':'#ef4444',
}

SPECIAL_NOTES = {
    0x1F4CA: 'axes currentColor; bars left green, middle red, right blue',
    0x1F4C8: 'axes currentColor; rising line green',
    0x1F4C9: 'axes currentColor; falling line red (mirrored)',
}



# Additional visual-accuracy audit: a generic shape should not erase salient emoji details.
# For example, the moon-crescent should not replace a full moon, and a waving hand
# should not replace two clapping hands.
UNSUITABLE_EMOJI = """
♿ 🏃 🏋 🛋 🛀 🛌 🚴 🚵
🐓 🐔 🐣 🐤 🐥 🕊 🦃 🦅 🦆 🦢 🪿
🐛 🏬 🏟 🚎 🐩 🐶 🐺 🦊 🦮 😻 😼 😽
💹 🍵 🍻 🪒 🎱 📹 🎥 🎦 🎴
👿 😤 😾 🤬 😬 🙄 😁 😅 😆 😂 🤣 😸 😺
😑 😒 😶 🫥 😔 😕 😞 😟 😢 😿 😊 😌
🌑 🌒 🌓 🌔 🌕 🌖 🌗 🌘 🌚 🌛 🌜 🌝 🌞 🌃
☔ 🌦 🍁 🍀 ☘ 🍂 🌷 🌹 💐 💮 🏵 🪻
📑 📚 🥮 🪙 💰 ☦
🧼 🗼 🏮 🚧 🚒 🪑 💁 💸 🗂 🗞
💭 🗯 🌂 🎍 🧫 ⚗ 🖍 🤳 🤒 🚉
✍ 🔪 💝 💖
🐭 🐰 🐿 🐠 🐡 🫛 🍳 🍹 🍼 📲 🛫 🛬 📶
🎌 🏁 ⛳ 🏎 🚘 📩 💌 📃
🤛 🤜 🤟 🙏 🔏 🔐 🫕 🍲 🎟 🚍
✒ 🖊 🖋 👀
""".split()
UNSUITABLE_CODEPOINTS = {ord(emoji[0]) for emoji in UNSUITABLE_EMOJI}

# Half-hour clock emojis were previously assigned to their corresponding whole-hour hand.
UNSUITABLE_CODEPOINTS.update(range(0x1F55C, 0x1F568))

# Where the supplied font has a substantially closer icon, use it instead.
BETTER_GLYPHS = {
    0x1F9EA: 'test-tube',         # 🧪, not a conical flask
    0x1F4DD: 'notebook-pen',      # 📝, not a lone pencil
    0x1F3BC: 'music-3',          # 🎼 musical score (closer but not exact; excluded below)
    0x1F3B6: 'music-2',          # 🎶 two notes
}
UNSUITABLE_CODEPOINTS.add(0x1F3BC)  # sheet music cannot be depicted faithfully by two notes

# Distinct conventional emoji colors; dark/light neutral shades avoid background blending.
EXTRA_CP_COLORS = {
    # Colored shapes and single-purpose status UI
    0x1F7E4: '#9a6135',  # brown circle
    0x1F7EB: '#9a6135', # brown square
    0x1F7E5: '#ef4444', 0x1F7E6: '#2563eb', 0x1F7E7: '#f97316',
    0x1F7E8: '#facc15', 0x1F7E9: '#22c55e', 0x1F7EA: '#8b5cf6',
    0x1F7F0: '#f9fafb',
    0x1F532: '#64748b', 0x1F533: '#94a3b8',
    0x1F518: '#6b7280', 0x23FA: '#ef4444', 0x23F9: '#64748b', 0x23F8: '#3b82f6',
    0x2753: '#dc2626', 0x2754: '#9ca3af', 0x2755: '#ef4444', 0x2757: '#ef4444',
    0x203C: '#ef4444', 0x2049: '#ef4444',
    0x1F6D1: '#ef4444', 0x1F6AD: '#dc2626', 0x1F6AC: '#f59e0b',
    0x1F3F3: '#cbd5e1', 0x1F3F4: '#475569', 0x1F6A9: '#ef4444',
    0x1F3C1: '#94a3b8', 0x1F38C: '#dc2626', 0x26F3: '#ef4444',
    0x1F4D1: '#3b82f6', 0x1F4D2: '#7c3aed', 0x1F4D3: '#4b5563',
    0x1F4D4: '#f4c542', 0x1F4D5: '#ef4444', 0x1F4D6: '#93c5fd',
    0x1F4D7: '#22c55e', 0x1F4D8: '#2563eb', 0x1F4D9: '#f97316',
    0x1FA75: '#7dd3fc', 0x1FA76: '#94a3b8', 0x1FA77: '#f9a8d4',
    0x1F49E: '#ec4899', 0x2665: '#ef4444', 0x1F495: '#f472b6',
    0x1F49F: '#ec4899',
    # Commonly yellow human-expression emoji; red angry variants
    0x1F620: '#f59e0b', 0x1F621: '#ef4444', 0x1F476: '#facc15',
    0x1F9CD: '#facc15', 0x1F463: '#a16207',
    # Distinctive red / green / amber objects
    0x1F4CC: '#ef4444', 0x1F4CD: '#ef4444', 0x1F6AB: '#ef4444',
    0x1F9E0: '#f9a8d4', 0x1F9B4: '#f3e8db', 0x1F48A: '#ef4444',
    0x1F489: '#64748b', 0x1FA79: '#e7bde6',
    0x1F6A8: '#eab308', 0x1F6A6: '#ef4444', 0x1F6A5: '#eab308',
    0x1F6A7: '#f97316', 0x1F3C6: '#eab308',
    0x1F947: '#eab308', 0x1F948: '#a1a1aa', 0x1F949: '#b45309',
    0x1F4BF: '#94a3b8', 0x1F4BE: '#94a3b8',
    0x1F4E6: '#b88a5c', 0x1F9F3: '#964b33', 0x1F4BC: '#92400e',
    0x1F4C1: '#eab308', 0x1F4C2: '#eab308',
    0x1F4F0: '#94a3b8', 0x1F5DE: '#94a3b8',
    0x1F4E7: '#60a5fa', 0x1F4E8: '#93c5fd', 0x1F4E9: '#93c5fd',
    0x1F4EA: '#9ca3af', 0x1F4EB: '#ef4444', 0x1F4EC: '#ef4444',
    0x1F4ED: '#9ca3af', 0x1F4EE: '#2563eb',
    0x1F6E1: '#94a3b8', 0x1F52A: '#94a3b8', 0x1F528: '#94a3b8',
    0x1F529: '#64748b', 0x1F9F0: '#ef4444',
    0x1F9EA: '#22c55e', 0x1F9EC: '#8b5cf6',
    0x1F9F9: '#a16207', 0x1F9FC: '#93c5fd',
    0x1F388: '#ef4444', 0x1F389: '#f97316', 0x1F38A: '#8b5cf6',
    0x1F3AF: '#ef4444', 0x1F579: '#94a3b8',
    0x1F4CA: None, 0x1F4C8: None, 0x1F4C9: None, # per-contour color layers are preserved
    # Natural objects with distinctive dominant colors
    0x1F34F: '#84cc16', 0x1F34E: '#ef4444', 0x1F347: '#8b5cf6',
    0x1F352: '#ef4444', 0x1F337: '#ec4899', 0x1F338: '#f9a8d4',
    0x1F33A: '#f97316', 0x1F33C: '#facc15', 0x1F33B: '#eab308',
    0x1F340: '#22c55e', 0x1F33F: '#16a34a', 0x1F343: '#22c55e',
    0x1F331: '#22c55e', 0x1F332: '#16a34a', 0x1F333: '#16a34a',
    0x1F384: '#16a34a', 0x1F334: '#16a34a', 0x1F335: '#16a34a',
    0x1F95A: '#fef3c7', 0x1F966: '#22c55e', 0x1F9C1: '#f9a8d4',
    0x1F355: '#f59e0b', 0x1F36A: '#c18443', 0x1F37F: '#facc15',
    0x1F373: '#fef3c7', 0x1F95B: '#e5e7eb',
    0x1F37D: '#94a3b8', 0x1F374: '#9ca3af',
    0x1F41F: '#60a5fa', 0x1F420: '#fb923c', 0x1F421: '#facc15',
    0x1F40D: '#22c55e', 0x1F40C: '#a16207',
    0x1F426: '#facc15', 0x1F408: '#f59e0b', 0x1F415: '#b45309',
    0x1F422: '#16a34a', 0x1F430: '#d1d5db', 0x1F407: '#d1d5db',
    0x1F43E: '#b45309', 0x1F43F: '#b45309',
    0x1F4A3: '#64748b', 0x1F916: '#94a3b8',
    0x1F300: '#7c3aed', 0x1F32A: '#93c5fd',
    0x1F31F: '#eab308', 0x1F320: '#eab308', 0x2B50: '#facc15',
    0x1F4A8: '#93c5fd', 0x1F4A6: '#38bdf8', 0x1F4A7: '#38bdf8',
    0x1F9EF: '#a855f7', 0x1F3B9: '#9ca3af',
    0x1F3B8: '#a16207', 0x1F3C0: '#f97316',
    0x1F3B2: '#e5e7eb',
    0x1F6B2: '#2563eb', 0x1F697: '#ef4444', 0x1F698: '#ef4444',
    0x1F699: '#64748b', 0x1F69A: '#f97316', 0x1F68C: '#eab308',
    0x1F691: '#ef4444', 0x1F695: '#facc15', 0x1F6A2: '#2563eb',
    0x1F6F6: '#ef4444', 0x1F3E0: '#b45309', 0x1F3E1: '#b45309',
    0x1F3EB: '#b45309', 0x1F3E5: '#ef4444', 0x1F3ED: '#64748b',
    0x1F3E6: '#64748b', 0x1F3F0: '#9ca3af',
    0x1F3A4: '#64748b', 0x1F3A8: '#f97316',
}

EXTRA_GLYPH_DEFAULT_COLORS = {
    # Semantic symbols: generally blue or red in popular emoji sets.
    'alert-circle': '#ef4444', 'alert-triangle': '#f59e0b',
    'ban': '#ef4444', 'octagon': '#ef4444', 'x': '#ef4444',
    'check':'#22c55e', 'check-circle':'#22c55e', 'check-square':'#22c55e',
    'circle-help':'#ef4444', 'info':'#3b82f6', 'circle-parking':'#2563eb',
    'plus':'#22c55e', 'minus':'#ef4444', 'divide':'#2563eb', 'equal':'#2563eb',
    'arrow-down':'#3b82f6','arrow-left':'#3b82f6','arrow-right':'#3b82f6','arrow-up':'#3b82f6',
    'arrow-up-left':'#3b82f6','arrow-up-right':'#3b82f6','arrow-down-left':'#3b82f6','arrow-down-right':'#3b82f6',
    'arrow-up-down':'#3b82f6','arrow-left-right':'#3b82f6','corner-up-left':'#3b82f6','corner-up-right':'#3b82f6',
    'play':'#3b82f6','pause':'#3b82f6','step-back':'#3b82f6','skip-back':'#3b82f6','skip-forward':'#3b82f6',
    'fast-forward':'#3b82f6','rewind':'#3b82f6','repeat':'#3b82f6','repeat-1':'#3b82f6','shuffle':'#3b82f6',
    'refresh-cw':'#3b82f6','eject':'#3b82f6','volume-x':'#94a3b8','volume-1':'#64748b','volume-2':'#64748b',
    'wifi':'#3b82f6','vibrate':'#3b82f6','circle-dot':'#64748b',
    'square':'#64748b', 'diamond':'#f97316','triangle':'#ef4444',
    'recycle':'#16a34a', 'radiation':'#eab308','biohazard':'#eab308',
    # Metallic / wood / common colors on conventional objects.
    'alarm-clock':'#ef4444','anchor':'#94a3b8','amphora':'#b45309','archive':'#94a3b8',
    'axe':'#a16207','backpack':'#2563eb','baggage-claim':'#2563eb',
    'bandage':'#fde68a','battery':'#16a34a','battery-low':'#ef4444',
    'bath':'#93c5fd','bed':'#93c5fd','bell-off':'#eab308',
    'bike':'#ef4444','bird':'#facc15','bomb':'#64748b','bone':'#e2e8f0',
    'bookmark':'#ef4444','bot':'#94a3b8','brain':'#f9a8d4',
    'brick-wall':'#b45309','briefcase-business':'#92400e','broom':'#b45309',
    'bubbles':'#7dd3fc','bug':'#84cc16','building':'#94a3b8',
    'building-2':'#94a3b8','cable-car':'#94a3b8','calendar':'#ef4444',
    'camera':'#64748b','car':'#ef4444','car-front':'#2563eb',
    'castle':'#94a3b8','cat':'#f59e0b','clapperboard':'#64748b',
    'clipboard':'#b45309','clock-1':'#64748b','clock-2':'#64748b','clock-3':'#64748b',
    'clock-4':'#64748b','clock-5':'#64748b','clock-6':'#64748b','clock-7':'#64748b',
    'clock-8':'#64748b','clock-9':'#64748b','clock-10':'#64748b','clock-11':'#64748b',
    'clock-12':'#64748b', 'coins':'#eab308','compass':'#94a3b8',
    'cooking-pot':'#94a3b8','credit-card':'#2563eb','croissant':'#b45309',
    'dice-5':'#e2e8f0','disc':'#94a3b8','dna':'#8b5cf6',
    'dog':'#a16207','door-open':'#92400e','drama':'#8b5cf6',
    'drum':'#a16207','egg':'#fde68a','eye':'#60a5fa',
    'factory':'#64748b','feather':'#94a3b8','ferris-wheel':'#ec4899',
    'file-text':'#93c5fd','film':'#64748b','fire-extinguisher':'#ef4444',
    'fish':'#3b82f6','flag':'#ef4444','flashlight':'#64748b',
    'flask-conical':'#22c55e','test-tube':'#22c55e','folder':'#eab308',
    'folder-open':'#eab308','footprints':'#a16207','fork-knife':'#9ca3af',
    'gamepad-2':'#64748b','ghost':'#e2e8f0','glasses':'#64748b',
    'graduation-cap':'#64748b','guitar':'#a16207','hamburger':'#d97706',
    'hammer':'#64748b','handshake':'#facc15','hard-hat':'#eab308',
    'headphones':'#64748b','helicopter':'#64748b','home':'#b45309',
    'hospital':'#ef4444','hotel':'#94a3b8','hourglass':'#fbbf24',
    'houses':'#b45309','image':'#3b82f6','joystick':'#64748b',
    'key-round':'#eab308','keyboard':'#64748b','landmark':'#94a3b8',
    'laptop':'#94a3b8','leafy-green':'#22c55e','life-buoy':'#ef4444',
    'link':'#94a3b8','lock':'#eab308','lock-open':'#eab308',
    'luggage':'#8b5a2b','magnet':'#ef4444','mail':'#94a3b8',
    'mail-open':'#94a3b8','mailbox':'#ef4444','map':'#22c55e',
    'megaphone':'#f59e0b','message-circle':'#93c5fd',
    'mic':'#64748b','microscope':'#64748b','milk':'#e2e8f0',
    'monitor':'#64748b','mosque':'#94a3b8','mouse':'#64748b',
    'mouth':'#ef4444','music':'#3b82f6','music-2':'#3b82f6',
    'newspaper':'#94a3b8','notebook-pen':'#3b82f6','nut':'#64748b',
    'package':'#b45309','paintbrush':'#8b5cf6','palette':'#f97316',
    'panda':'#64748b','paperclip':'#94a3b8','pause':'#3b82f6',
    'paw-print':'#a16207','pen-tool':'#64748b','pencil':'#eab308',
    'phone':'#64748b','piano':'#64748b','pickaxe':'#94a3b8',
    'pill':'#ef4444','plane':'#94a3b8','plug':'#64748b',
    'pocket-knife':'#64748b','printer':'#64748b','puzzle':'#a855f7',
    'rabbit':'#e2e8f0','radio':'#94a3b8','rat':'#64748b',
    'receipt':'#e2e8f0','rocking-chair':'#b45309','roller-coaster':'#ef4444',
    'ruler':'#eab308','sailboat':'#3b82f6','salad':'#16a34a',
    'sandwich':'#eab308','satellite':'#94a3b8','save':'#94a3b8',
    'scale':'#94a3b8','school':'#b45309','scissors':'#94a3b8',
    'scroll':'#d6b788','search':'#64748b','settings':'#94a3b8',
    'shell':'#f3c7ad','shield':'#94a3b8','ship':'#2563eb',
    'shirt':'#2563eb','shopping-cart':'#64748b','shovel':'#64748b',
    'shower-head':'#64748b','shrimp':'#fb923c','skull':'#cbd5e1',
    'smartphone':'#64748b','snail':'#b45309',
    'soup':'#eab308','speech':'#facc15','squirrel':'#b45309',
    'stethoscope':'#64748b','sword':'#94a3b8','syringe':'#64748b',
    'tag':'#eab308','target':'#ef4444','telescope':'#94a3b8',
    'tent':'#eab308','thermometer':'#ef4444','ticket':'#eab308',
    'timer':'#64748b','toilet':'#e2e8f0','toolbox':'#ef4444',
    'toothbrush':'#3b82f6','tornado':'#94a3b8',
    'tractor':'#16a34a','train':'#64748b','train-front':'#64748b',
    'trash-2':'#64748b','turtle':'#16a34a','tv':'#64748b',
    'umbrella':'#a855f7','volleyball':'#e2e8f0',
    'wand':'#8b5cf6','watch':'#64748b','wind':'#93c5fd','hand-platter':'#facc15',
    'wine':'#dc2626','worm':'#a16207','wrench':'#94a3b8',
}

# Discriminating the color for each shape is important: a red and blue diamond
# must not use the same orange glyph simply because they share the same outline.
EXTRA_CP_COLORS.update({
    0x1F536: '#f97316', 0x1F537: '#2563eb', 0x1F538: '#f97316',
    0x1F539: '#2563eb', 0x2666: '#ef4444',
    0x1F534: '#ef4444', 0x1F535: '#2563eb', 0x1F7E0: '#f97316',
    0x1F7E1: '#facc15', 0x1F7E2: '#22c55e', 0x1F7E3: '#8b5cf6',
    0x26AA: '#cbd5e1', 0x26AB: '#475569',
    0x25FB: '#cbd5e1',0x25FC: '#475569',0x25FD: '#cbd5e1',0x25FE: '#475569',
    0x2B1B: '#475569', 0x2B1C: '#cbd5e1',
    0x1F5A4: '#475569',0x1F90D: '#e2e8f0',0x1F90E: '#8b5a2b',
    0x1F494: '#ef4444', 0x1F9E1: '#f97316',0x1F49B: '#facc15',
    0x1F49A: '#22c55e',0x1F499: '#2563eb',0x1F49C: '#8b5cf6',
    0x1F4D5: '#ef4444',0x1F4D7: '#22c55e',0x1F4D8: '#2563eb',0x1F4D9: '#f97316',
    0x2640: '#ec4899', 0x2642: '#3b82f6', 0x265F: '#64748b',
    0x2660: '#64748b', 0x2663: '#64748b', 0x267E: '#3b82f6',
    0x269B: '#8b5cf6', 0x26A7: '#a855f7', 0x2733: '#22c55e',
    0x1F4B2: '#22c55e', 0x26EA: '#9ca3af',
})

CP_COLORS.update({k:v for k,v in EXTRA_CP_COLORS.items() if v is not None})
GLYPH_DEFAULT_COLORS.update(EXTRA_GLYPH_DEFAULT_COLORS)

GRAY_COLOR_EXCEPTIONS = {
    # Grayscale is semantically part of these explicit color series.
    0x26AA, 0x26AB,                         # white / black circles
    0x25FB, 0x25FC, 0x25FD, 0x25FE,         # white / black squares
    0x2B1B, 0x2B1C,                         # black / white large squares
    0x1F532, 0x1F533,                       # black / white square buttons
    0x1F5A4, 0x1F90D, 0x1FA76,             # black / white / gray hearts
    0x1F948,                                # silver medal in gold/silver/bronze series
}

def is_grayish(hexcolor):
    if not hexcolor or not hexcolor.startswith('#') or len(hexcolor) != 7:
        return False
    r, g, b = (int(hexcolor[i:i+2], 16) for i in (1, 3, 5))
    return max(r, g, b) - min(r, g, b) <= 40

def color_for(cp, glyph):
    color = CP_COLORS.get(cp) or GLYPH_DEFAULT_COLORS.get(glyph)
    if color and is_grayish(color) and cp not in GRAY_COLOR_EXCEPTIONS:
        return None
    return color


def shift_simple_glyph(glyph, dy):
    if glyph.isComposite():
        for comp in glyph.components:
            comp.y += dy
    elif hasattr(glyph, 'coordinates') and glyph.numberOfContours > 0:
        glyph.coordinates.translate((0, dy))
    return glyph


def split_simple_glyph(font, base_name, contour_indices, new_name, dy=0, mirror_x=None):
    base = font['glyf'][base_name]
    coords, endPts, flags = base.getCoordinates(font['glyf'])
    starts = [0] + [e+1 for e in endPts[:-1]]
    sel_coords = []
    sel_flags = []
    sel_end = []
    pos = 0
    for idx in contour_indices:
        s, e = starts[idx], endPts[idx]
        pts = list(coords[s:e+1])
        if mirror_x is not None:
            pts = [(2*mirror_x - x, y) for x, y in pts]
        if dy:
            pts = [(x, y + dy) for x, y in pts]
        sel_coords.extend(pts)
        sel_flags.extend(flags[s:e+1])
        pos += len(pts)
        sel_end.append(pos-1)
    g = Glyph()
    g.numberOfContours = len(sel_end)
    g.coordinates = GlyphCoordinates(sel_coords)
    g.flags = array('B', sel_flags)
    g.endPtsOfContours = sel_end
    g.program = base.program
    font['glyf'][new_name] = g
    base_advance, base_lsb = font['hmtx'][base_name]
    # Separate COLR layers share an advance but must retain their *original*
    # horizontal positions. Bearings otherwise normalize every piece to x=0.
    font['hmtx'][new_name] = (base_advance, base_lsb + min(x for x, y in sel_coords) - base.xMin)
    return new_name

font = TTFont(SOURCE)

# Digits are ordinary text, not emoji/icon substitutions. Remove Lucide's original
# Strip ASCII digits from every cmap, including the legacy Macintosh cmap.
# The source Lucide font maps Mac Roman 0-9 to arrow icons, which can leak through
# in browser font selection even when the Unicode cmap entries are absent.
for table in font['cmap'].tables:
    if hasattr(table, 'cmap'):
        for cp in range(0x30, 0x3A):
            table.cmap.pop(cp, None)

# Better font metrics for text alignment.
os2 = font['OS/2']
os2.sTypoAscender = 850
os2.sTypoDescender = -150
os2.sTypoLineGap = 0
os2.usWinAscent = 969
os2.usWinDescent = 150
if hasattr(os2,'sxHeight'): os2.sxHeight = 520
if hasattr(os2,'sCapHeight'): os2.sCapHeight = 720
hhea = font['hhea']
hhea.ascent = 850
hhea.descent = -150
hhea.lineGap = 0

rows = []
with MAPPING_CSV.open(encoding='utf-8', newline='') as f:
    for row in csv.DictReader(f):
        cp = int(row['codepoint'].removeprefix('U+'), 16)
        if cp in EXCLUDED_CODEPOINTS or cp in UNSUITABLE_CODEPOINTS:
            continue
        mapped_glyph = BETTER_GLYPHS.get(cp, row['lucide_glyph'])
        if mapped_glyph not in font['glyf'].glyphs:
            raise ValueError(f'Missing Lucide glyph for U+{cp:04X}: {mapped_glyph}')
        rows.append({'cp': cp, 'emoji': row['emoji'], 'glyph': mapped_glyph, 'unicode_name': row.get('unicode_name','')})

# Duplicate glyphs for each remaining emoji codepoint, shifted for better optical centering.
new_cmap = {}
colorGlyphs = {}
palette = []
palette_index = {}

def palette_slot(hexcolor):
    if hexcolor not in palette_index:
        palette_index[hexcolor] = len(palette)
        palette.append(rgba(hexcolor))
    return palette_index[hexcolor]

for row in rows:
    cp, base_glyph = row['cp'], row['glyph']
    new_name = f'emoji_u{cp:04X}'
    if new_name not in font['glyf'].glyphs:
        glyph = deepcopy(font['glyf'][base_glyph])
        shift_simple_glyph(glyph, SHIFT_Y)
        if cp == 0x1F53B and not glyph.isComposite() and hasattr(glyph, 'coordinates'):
            glyph.coordinates = GlyphCoordinates([(x, 1000 - 2*72 - y) for x, y in glyph.coordinates])
        font['glyf'][new_name] = glyph
        font['hmtx'][new_name] = font['hmtx'][base_glyph]
    new_cmap[cp] = new_name

# Special layered glyphs for charts.
GREEN = '#22c55e'; RED = '#ef4444'; BLUE = '#2563eb'
# 📊 bar chart uses bar-chart-3: contour0 frame, contour3 left bar, contour1 middle bar, contour2 right bar
if 0x1F4CA in new_cmap:
    base_name = new_cmap[0x1F4CA]
    split_simple_glyph(font, 'bar-chart-3', [0], base_name + '_frame', dy=SHIFT_Y)
    split_simple_glyph(font, 'bar-chart-3', [3], base_name + '_bar_left', dy=SHIFT_Y)
    split_simple_glyph(font, 'bar-chart-3', [1], base_name + '_bar_mid', dy=SHIFT_Y)
    split_simple_glyph(font, 'bar-chart-3', [2], base_name + '_bar_right', dy=SHIFT_Y)
    colorGlyphs[base_name] = [
        (base_name + '_frame', 0xFFFF),
        (base_name + '_bar_left', palette_slot(GREEN)),
        (base_name + '_bar_mid', palette_slot(RED)),
        (base_name + '_bar_right', palette_slot(BLUE)),
    ]
# 📈 chart increasing uses chart-line: contour0 frame, contour1 line
if 0x1F4C8 in new_cmap:
    base_name = new_cmap[0x1F4C8]
    split_simple_glyph(font, 'chart-line', [0], base_name + '_frame', dy=SHIFT_Y)
    split_simple_glyph(font, 'chart-line', [1], base_name + '_line', dy=SHIFT_Y)
    colorGlyphs[base_name] = [
        (base_name + '_frame', 0xFFFF),
        (base_name + '_line', palette_slot(GREEN)),
    ]
# 📉 chart decreasing: same frame, but mirror line horizontally
if 0x1F4C9 in new_cmap:
    base_name = new_cmap[0x1F4C9]
    split_simple_glyph(font, 'chart-line', [0], base_name + '_frame', dy=SHIFT_Y)
    split_simple_glyph(font, 'chart-line', [1], base_name + '_line', dy=SHIFT_Y, mirror_x=541)
    colorGlyphs[base_name] = [
        (base_name + '_frame', 0xFFFF),
        (base_name + '_line', palette_slot(RED)),
    ]

# Add simple color layers for all other conventionally-colored glyphs.
for row in rows:
    cp, base_glyph = row['cp'], row['glyph']
    name = new_cmap[cp]
    if name in colorGlyphs:
        continue
    color = color_for(cp, base_glyph)
    if color:
        colorGlyphs[name] = [(name, palette_slot(color))]

# finalize glyph order and cmap
font.setGlyphOrder(font.getGlyphOrder())
font['glyf'].glyphOrder = font.getGlyphOrder()
for table in font['cmap'].tables:
    if table.isUnicode() and table.format in (4, 12):
        table.cmap.update({cp: glyph for cp, glyph in new_cmap.items() if table.format == 12 or cp <= 0xFFFF})
variation = next((t for t in font['cmap'].tables if getattr(t, 'format', None) == 14), None)
if variation is None:
    variation = CmapSubtable.newSubtable(14)
    variation.platformID = 0
    variation.platEncID = 5
    variation.language = 0
    variation.cmap = {}
    variation.uvsDict = {}
    font['cmap'].tables.append(variation)
variation.uvsDict[0xFE0F] = [(cp, new_cmap[cp]) for cp in sorted(new_cmap) if cp in VS16_BASES]

# build color tables
if palette:
    font['CPAL'] = buildCPAL([palette])
    font['COLR'] = buildCOLR(colorGlyphs, glyphMap=font.getReverseGlyphMap())

# Normalize horizontal metrics for mapped emoji glyphs.
# Lucide's icon font stores many outlines centered in a 1000-unit design box while
# hmtx uses lsb=0, which turns intended symmetric side padding into right-side whitespace.
# Recenter every mapped glyph and trim only clearly excessive padding. A 650-unit
# minimum advance keeps very narrow vertical icons from becoming unnaturally cramped.
MAX_TOTAL_SIDE_PADDING = 120
MIN_EMOJI_ADVANCE = 650
horizontal_metric_changes = []
for row in rows:
    cp = row['cp']
    name = new_cmap[cp]
    glyph = font['glyf'][name]
    glyph.recalcBounds(font['glyf'])
    if glyph.numberOfContours == 0 and not glyph.isComposite():
        continue
    ink_width = glyph.xMax - glyph.xMin
    old_advance, old_lsb = font['hmtx'][name]
    old_total_padding = max(0, old_advance - ink_width)
    new_advance = max(MIN_EMOJI_ADVANCE, ink_width + min(old_total_padding, MAX_TOTAL_SIDE_PADDING))
    new_total_padding = max(0, new_advance - ink_width)
    new_lsb = new_total_padding // 2
    font['hmtx'][name] = (new_advance, new_lsb)
    if new_advance != old_advance or new_lsb != old_lsb:
        horizontal_metric_changes.append((cp, name, old_advance, old_lsb, ink_width, new_advance, new_lsb))

# names
name_values = {1:'Lucide Emoji Color',3:'Lucide Emoji Color v2.11',4:'Lucide Emoji Color v2.11',6:'LucideEmojiColorv211',16:'Lucide Emoji Color',17:'Regular'}
for entry in font['name'].names:
    if entry.nameID in name_values:
        val = name_values[entry.nameID]
        entry.string = val.encode('utf-16-be') if entry.isUnicode() else val.encode('latin-1', 'ignore')

# save
font.recalcBBoxes = True
font.recalcTimestamp = False
font['head'].modified += 1
out_ttf = DIST / 'lucide_emoji_colorized_v2.11.ttf'
out_woff2 = DIST / 'lucide_emoji_colorized_v2.11.woff2'
font.flavor = None
font.save(out_ttf)
font.flavor = 'woff2'
font.save(out_woff2)

# userscript
cps = [row['cp'] for row in rows]
unicode_range = ','.join(f'U+{cp:X}' for cp in cps)
b64 = base64.b64encode(out_woff2.read_bytes()).decode('ascii')
userscript = f'''// ==UserScript==
// @name         ChatGPT Lucide Emoji Font
// @namespace    local.lucide-emoji
// @version      2.11
// @description  Render supported Unicode emoji as Lucide icons on chatgpt.com, with colorized conventionally-colored emoji and improved alignment.
// @match        https://chatgpt.com/*
// @match        https://www.chatgpt.com/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(() => {{
  'use strict';
  const css = `
@font-face {{
  font-family: 'Lucide Emoji Colorized';
  src: url('data:font/woff2;base64,{b64}') format('woff2');
  font-style: normal;
  font-weight: 100 900;
  font-display: swap;
  ascent-override: 85%;
  descent-override: 15%;
  line-gap-override: 0%;
  unicode-range: {unicode_range};
}}
:where(html, body, body *):not(:is(pre, pre *, code, code *, kbd, kbd *, samp, samp *, svg, svg *, [class*='font-mono'], [class*='font-mono'] *)) {{
  font-family: 'Lucide Emoji Colorized', var(--font-sans, ui-sans-serif), ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}
[data-radix-popper-content-wrapper], [role='img'], svg, svg * {{
  font-family: inherit !important;
}}
`;
  const style = document.createElement('style');
  style.id = 'lucide-emoji-font-v2.11';
  style.textContent = css;
  const inject = () => (document.head || document.documentElement).append(style);
  if (document.documentElement) inject(); else document.addEventListener('DOMContentLoaded', inject, {{ once: true }});
}})();
'''
(USERSCRIPT_DIR / 'chatgpt_lucide_emoji_font_v2.11.user.js').write_text(userscript, encoding='utf-8')
(DIST / 'chatgpt_lucide_emoji_font_v2.11.txt').write_text(userscript, encoding='utf-8')

# mapping CSV
out_csv = DATA_DIR / 'lucide_emoji_mappings_v2.11.csv'
with out_csv.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['codepoint', 'emoji', 'lucide_glyph', 'unicode_name', 'assigned_color_or_note'])
    for row in rows:
        cp = row['cp']
        note = SPECIAL_NOTES.get(cp) or color_for(cp, row['glyph']) or ''
        w.writerow([f'U+{cp:04X}', row['emoji'], row['glyph'], row['unicode_name'], note])

metrics_csv = DATA_DIR / 'lucide_emoji_horizontal_metrics_v2.11.csv'
with metrics_csv.open('w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['codepoint','emoji','lucide_glyph','old_advance','old_lsb','ink_width','new_advance','new_lsb','new_rsb'])
    row_by_cp = {row['cp']: row for row in rows}
    for cp, name, old_advance, old_lsb, ink_width, new_advance, new_lsb in horizontal_metric_changes:
        row = row_by_cp[cp]
        w.writerow([f'U+{cp:04X}', row['emoji'], row['glyph'], old_advance, old_lsb, ink_width, new_advance, new_lsb, new_advance - new_lsb - ink_width])

print('Created', out_ttf, out_woff2, USERSCRIPT_DIR / 'chatgpt_lucide_emoji_font_v2.11.user.js', DIST / 'chatgpt_lucide_emoji_font_v2.11.txt', out_csv, metrics_csv)
print('Mappings kept:', len(rows), 'Color layers:', len(colorGlyphs), 'Palette entries:', len(palette), 'Horizontal metrics adjusted:', len(horizontal_metric_changes))