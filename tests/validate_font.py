from pathlib import Path
import csv
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
TTF = ROOT / "dist/lucide_emoji_colorized_v2.11.ttf"
USERSCRIPT = ROOT / "userscript/chatgpt_lucide_emoji_font_v2.11.user.js"
MAPPING = ROOT / "data/lucide_emoji_mappings_v2.11.csv"
METRICS = ROOT / "data/lucide_emoji_horizontal_metrics_v2.11.csv"

font = TTFont(TTF)
rows = list(csv.DictReader(MAPPING.open(encoding="utf-8")))
assert len(rows) == 522, len(rows)

for table in font["cmap"].tables:
	if hasattr(table, "cmap"):
		for cp in range(0x30, 0x3A):
			assert cp not in table.cmap, (table.platformID, table.platEncID, cp)

assert "COLR" in font and "CPAL" in font
color_layers = font["COLR"].ColorLayers

def mapped(cp):
	for table in font["cmap"].tables:
		if table.isUnicode() and hasattr(table, "cmap") and cp in table.cmap:
			return table.cmap[cp]
	raise AssertionError(f"U+{cp:04X} not mapped")

assert len(color_layers[mapped(0x1F4CA)]) == 4
assert len(color_layers[mapped(0x1F4C8)]) == 2
assert len(color_layers[mapped(0x1F4C9)]) == 2
for cp in (0x1F4BB, 0x1F5A5, 0x1F5A8, 0x2328, 0x1F5B1):
	assert mapped(cp) not in color_layers, hex(cp)
for cp in (0x26AA, 0x26AB, 0x1F5A4, 0x1F90D):
	assert mapped(cp) in color_layers, hex(cp)

metric_rows = list(csv.DictReader(METRICS.open(encoding="utf-8")))
assert metric_rows
for row in metric_rows:
	assert int(row["new_lsb"]) >= 0
	assert int(row["new_rsb"]) >= 0
	assert abs(int(row["new_lsb"]) - int(row["new_rsb"])) <= 1

fire = next(row for row in metric_rows if row["codepoint"] == "U+1F525")
assert (int(fire["new_advance"]), int(fire["new_lsb"]), int(fire["new_rsb"])) == (800, 60, 60)

script = USERSCRIPT.read_text(encoding="utf-8")
assert "// @version      2.11" in script
assert "font-variant-emoji" not in script
assert "U+30" not in script and "U+31" not in script and "U+39" not in script
print("v2.11 validation passed")
