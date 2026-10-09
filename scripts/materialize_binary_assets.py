import argparse
import base64
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def extract_embedded_woff2():
	script = (ROOT / "userscript/chatgpt_lucide_emoji_font_v2.11.user.js").read_text(encoding="utf-8")
	match = re.search(r"data:font/woff2;base64,([^']+)", script)
	if not match:
		raise RuntimeError("Embedded WOFF2 not found in userscript")
	target = ROOT / "dist/lucide_emoji_colorized_v2.11.woff2"
	target.parent.mkdir(exist_ok=True)
	target.write_bytes(base64.b64decode(match.group(1)))
	print(target.relative_to(ROOT))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--extract-output", action="store_true", help="Extract the embedded v2.11 WOFF2 from the userscript")
	args = parser.parse_args()
	if args.extract_output:
		extract_embedded_woff2()
	else:
		parser.error("Use --extract-output. The upstream lucide.ttf build input is intentionally not synthesized.")

if __name__ == "__main__":
	main()
