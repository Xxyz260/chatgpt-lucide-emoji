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
- The userscript embeds the exact v2.11 WOFF2 font and has no runtime network dependency.

## Installation

Open [`userscript/chatgpt_lucide_emoji_font_v2.11.user.js`](userscript/chatgpt_lucide_emoji_font_v2.11.user.js) as raw text and install it with a userscript manager such as Violentmonkey or Tampermonkey.

Disable older versions first so multiple font overrides do not compete.

## Repository layout

- `userscript/` — installable self-contained userscript, including the generated WOFF2.
- `dist/` — text distribution copy of the userscript.
- `src/` — font builder.
- `data/` — source/current mappings, removed-mapping audit, and horizontal-metrics audit.
- `reference/` — emoji reference datasets used during mapping work.
- `scripts/` — extraction/materialization helper.
- `tests/` — structural/regression validation.
- `docs/` — mapping and rendering design notes.
- `third_party/` — upstream license notices.

## Build

Requires Python 3.10+ and the Lucide source font used as build input at `vendor/lucide.ttf`.

```sh
python -m pip install -r requirements.txt
python src/build_lucide_emoji_v2.11.py
python tests/validate_font.py
```

The development source-font snapshot used for v2.11 has SHA-256:

`e2d97a4a3c773062a32131638933f8e7a0c414c4b8a701fb778b641ad7c8ea88`

The corresponding source WOFF2 SHA-256 is:

`4bbcab663ca7c85032ceb1d5ee093f42db5d91b9bf5f39806e90f5cee47beec8`

The exact generated v2.11 WOFF2 is embedded in the userscript. Extract it with:

```sh
python scripts/materialize_binary_assets.py --extract-output
```

Generated-font snapshot hashes:

- TTF: `e47ddd0f482d261e624a2394f23f95a34cbdbc571ea2527c6f413a451992e4f8`
- WOFF2: `7c658aa2fd525b90123497da505c2d68e4ad032d9c7bf318b458666c183694fc`

## Design principles

A browser/system emoji fallback is preferable to a misleading Lucide substitution. Color is used when it is strongly encoded by the emoji specification or by consistent cross-platform convention. Neutral gray is avoided unless gray/black/white distinguishes a member of an explicit color set.

See [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) for detailed rules and regression history.

## Licensing

Project code and project-authored data are under the ISC License. The redistributed/modified Lucide font remains subject to Lucide's ISC notice and the MIT notice for Feather-derived icons. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and [`third_party/LUCIDE_LICENSE.txt`](third_party/LUCIDE_LICENSE.txt).

## Disclaimer

This is an independent project and is not affiliated with, endorsed by, or maintained by OpenAI or the Lucide project.
