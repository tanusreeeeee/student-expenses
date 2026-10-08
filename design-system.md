You are building a money-ledger app (Hisaab Guru) with a soft, calm, minimal visual identity. Nothing sharp: every corner is rounded.

## Color Palette
- Primary: #6B5CE7 (soft indigo): main actions, active tab
- Secondary: #F2B8A2 (peach): small accents
- Background: #FAF7F4 (warm cream)
- Surface: #FFFFFF: cards, inputs
- Text Primary: #2B2A33
- Text Secondary: #7A7785
- Border: #ECE7E1
- Success: #4F9D7A / Warning: #E0A458 / Error: #D9667A

## Typography
- Font: DM Sans (system sans-serif fallback when offline)
- Headings: bold, tracking tight. Body: regular.
- Sizes: 12 / 14 / 16 / 20 / 24 / 32 / 40 / 48px

## Spacing: 4px base: 4, 8, 12, 16, 24, 32, 48, 64

## Border Radius
- Small (inputs, chips): 12px
- Medium (alerts, buttons are pills): 16px
- Large (cards, containers): 28px
- Full (buttons, tabs, pills): 9999px

## Shadows (purple-tinted, very soft)
- Subtle: 0 1px 3px rgba(107,92,231,0.06)
- Medium: 0 6px 20px rgba(107,92,231,0.10)

## Components
- Buttons: pill, 48px high, 24px side padding, scale 1.02 on hover
- Inputs: 48px high, 16px padding, 2px primary border on focus
- Cards: 24px padding, large radius, subtle shadow, 1px border

## Rules
1. No colors outside this palette
2. Spacing from the scale only
3. Same radius per element type
4. When in doubt, add whitespace

All of this lives in theme.py (CSS) and .streamlit/config.toml. Change a color once at the top of theme.py.
