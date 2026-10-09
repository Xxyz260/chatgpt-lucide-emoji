# Changelog

## v2.11

- Recentered mapped glyphs horizontally.
- Trimmed excessive side padding while preserving a conservative minimum advance.
- Added a horizontal-metrics audit; `🔥` now has balanced `60/60` side bearings.
- Public-repository packaging corrects the userscript metadata version from `2.10` to `2.11`; rendering behavior is unchanged by that metadata correction.

## v2.10

- Removed ASCII digits from every cmap subtable, including the legacy Macintosh cmap.
- Removed global `font-variant-emoji: emoji`.

## v2.9

- Removed non-semantic grayscale colorization from ordinary objects.
- Preserved black/white/gray where it distinguishes an explicit color set.

## v2.8

- Tightened mapping quality substantially; weak substitutions now fall back to the system emoji font.
- Expanded conventional color coverage.
- Added special multicolor chart rendering.

## v2.7

- Added explicit colors for hearts, circles, books, pins, hands/smileys and other conventionally colored symbols.
- Pruned broad person and hand mappings.

## v2.6

- Introduced COLR/CPAL colorization and improved vertical alignment.

## v2.5

- First broad full-font Unicode-to-Lucide mapping pass.