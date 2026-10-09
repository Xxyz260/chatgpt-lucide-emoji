# Development notes

## Mapping policy

Prefer a system emoji fallback to a weak Lucide match. Mappings should be visually recognizable and semantically close. Broad category substitutions such as mapping distinct people to a generic bust, or two-hand gestures to a single open hand, were intentionally removed.

## Color policy

Use color when it is encoded by the emoji name/specification or is a strong cross-platform convention. Avoid arbitrary neutral gray on ordinary hardware and objects. Gray/black/white remains useful when it distinguishes an explicit color set, for example `⚪ ⚫`, black/white squares, `🖤 🤍`, and silver medal `🥈`.

COLR/CPAL color is attached to glyphs. Code points that share a Lucide source glyph therefore receive duplicated emoji glyphs when they need different colors.

`📊`, `📈`, and `📉` are special layered glyphs: structural axes use `currentColor`; bars/zigzags use semantic colors. The `📉` zigzag is horizontally mirrored.

## Alignment

Mapped glyphs are shifted vertically by `-72` font units. Font metrics are normalized to `850/-150` ascender/descender values for better alignment with surrounding UI text.

Lucide outlines are often centered in a 1000-unit design box while the source icon font uses `lsb = 0`, leaving excess whitespace on the right. v2.11 recenters mapped glyphs and caps total side padding at 120 units, with a 650-unit minimum advance. The horizontal audit is in `data/lucide_emoji_horizontal_metrics_v2.11.csv`.

## ASCII digit regression

The upstream font contains ASCII `0`–`9` mappings in multiple cmap subtables, including a legacy Macintosh Roman cmap. Removing digits only from Unicode cmaps was insufficient: browsers could still expose the legacy mappings under some font-selection paths. The builder removes `0x30`–`0x39` from every cmap table that has a `cmap` dictionary.

Do not reintroduce a global `font-variant-emoji: emoji`; it is unnecessary for the curated mappings and can influence presentation of ordinary text-capable characters.

## Binary/font inputs

The exact generated WOFF2 is embedded in the checked-in userscript and can be extracted with:

```sh
python scripts/materialize_binary_assets.py --extract-output
```

A source Lucide `lucide.ttf` is required to rebuild from scratch. Place it at `vendor/lucide.ttf`. The development snapshot used for v2.11 had SHA-256:

`e2d97a4a3c773062a32131638933f8e7a0c414c4b8a701fb778b641ad7c8ea88`

The corresponding source WOFF2 SHA-256 was:

`4bbcab663ca7c85032ceb1d5ee093f42db5d91b9bf5f39806e90f5cee47beec8`

## Validation checklist

Run:

```sh
python src/build_lucide_emoji_v2.11.py
python tests/validate_font.py
```

Then test representative strings in both light and dark themes, including editable text fields, colored symbol sets, charts, `🔥`, and ordinary ASCII digits.
