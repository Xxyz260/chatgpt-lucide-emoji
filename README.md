# ChatGPT Lucide Emoji

A userscript and modified Lucide icon font that render selected Unicode emoji as Lucide-style icons on `chatgpt.com`.

The project keeps ordinary text fonts intact and only substitutes explicitly mapped emoji/code points. Mappings are curated for visual and semantic fit rather than attempting to replace every emoji.

## Current version

`v2.11`

Highlights:

- 522 curated Unicode-to-Lucide mappings.
- Conventional emoji colors through OpenType COLR/CPAL layers where color adds meaning.
- `📊`, `📈`, and `📉` use custom multicolor layers while their axes retain the surrounding text color.
- Common gray hardware/object icons inherit the page text color instead of receiving arbitrary gray fills.
- ASCII digits `0`–`9` are removed from every cmap subtable so they always render as normal text.
- Mapped glyphs are vertically aligned for surrounding text and horizontally recentered/tightened to avoid lopsided blank space.
- The userscript embeds the WOFF2 font and has no runtime network dependency.

## Installation

Open [`userscript/chatgpt_lucide_emoji_font_v2.11.user.js`](userscript/chatgpt_lucide_emoji_font_v2.11.user.js) as raw text and install it with a userscript manager such as Violentmonkey or Tampermonkey. Disable older versions first so multiple font overrides do not compete.

## Repository layout

- `userscript/` — installable userscript.
- `dist/` — generated userscript/font snapshots; binary fonts are tracked as `.b64`.
- `src/` — font builder.
- `data/` — source/current mappings, removed-mapping audit, and horizontal-metrics audit.
- `vendor/` — exact upstream Lucide font snapshots as `.b64`.
- `scripts/` — binary materialization helper.
- `tests/` — structural/regression validation.
- `docs/` — mapping and rendering design notes.
- `third_party/` — upstream license notices.

## Build

Requires Python 3.10+.

```sh
python -m pip install -r requirements.txt
python scripts/materialize_binary_assets.py --vendor-only
python src/build_lucide_emoji_v2.11.py
python tests/validate_font.py
```

The builder reads `vendor/lucide.ttf` and `data/lucide_emoji_mappings_v2.8.csv`, then regenerates the v2.11 fonts, userscript, current mapping table, and horizontal-metrics audit.

To reconstruct the exact checked-in binary snapshots without rebuilding:

```sh
python scripts/materialize_binary_assets.py
```

## Design principles

A browser/system emoji fallback is preferable to a misleading Lucide substitution. Color is used when it is strongly encoded by the emoji specification or by consistent cross-platform convention. Neutral gray is avoided unless gray/black/white distinguishes a member of an explicit color set.

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for details and regression history.

## Licensing

Project code and project-authored data are under the ISC License. The redistributed/modified Lucide font remains subject to Lucide's ISC notice and the MIT notice for Feather-derived icons. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`third_party/LUCIDE_LICENSE.txt`](third_party/LUCIDE_LICENSE.txt).

## Disclaimer

This is an independent project and is not affiliated with, endorsed by, or maintained by OpenAI or the Lucide project.