# Contributing

Changes to mappings should favor accuracy over coverage. A browser/system emoji fallback is better than a Lucide icon that only vaguely resembles the original emoji.

Before submitting a change:

1. Update the mapping/build source.
2. Materialize `vendor/lucide.ttf` if needed.
3. Rebuild the generated artifacts.
4. Run `python tests/validate_font.py`.
5. Check representative rendering in both light and dark themes.
6. Pay particular attention to editable text fields, ASCII digits, black/white symbols, side bearings, and the layered chart glyphs.

For color changes, avoid neutral gray unless it is semantically part of a color series. For new special multicolor glyphs, keep uncolored structural strokes on the `currentColor` palette index where possible.