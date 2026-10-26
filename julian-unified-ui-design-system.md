# Julian Unified UI — Desktop Design System

Dark, cyan and magenta futuristic aesthetic with a light mode. Every desktop app follows and is updated to follow this system.

## 1. Principles and usage rules

One look for every desktop tool: a dark control-room interface lit by cyan and magenta, with a light mode that keeps the same structure. Build every window from the tokens and components here; never invent a colour, radius or font.

### Content fundamentals

- Write like a terse instrument panel. Short, literal, present tense: "Export complete", "3 warnings", "Sync paused".
- Buttons are verbs, one or two words: "Run", "Export CSV", "Clear queue". No "Click here", no exclamation marks, no emoji.
- Use sentence case for body text, headings and messages. Use uppercase only for `display-xl`, `display-lg` and `label`, which are set uppercase in CSS, so write the source text normally.
- Address the user as "you" only in help text. Status and log lines have no subject: "Connection restored".
- Numbers, paths, versions and timestamps are data: set them in `mono` or `mono-sm`, 24-hour time, units after the number ("12.4 MB/s").
- Errors say what failed and what to do next: "Could not open file. Check the path and try again."

### Visual foundations

**Themes.** Dark is the default and the identity. Light is the same layout with inverted surfaces and darker accent ink. Put `data-theme="dark"` or `data-theme="light"` on the root element; follow the OS setting on first launch (`prefers-color-scheme`), then remember the user's choice. Never hard-code a hex value in an app: read tokens so both themes work.

**Colour roles.**
- Page and surfaces stack in four steps: `bg`, `surface`, `surface-raised`, `surface-overlay`. Each step goes on top of the previous one; do not skip more than one step.
- `ink` is primary text, `ink-muted` is secondary, `ink-faint` is placeholder and disabled only.
- Cyan means "you can act on this": primary buttons, focus, links, selected nav, hover. Use `cyan` as a fill with `on-accent` text, and `cyan-ink` as text, icon or border. Never put `cyan` text on a surface in light mode; it fails contrast.
- Magenta means "live or special": running jobs, AI activity, selection highlights, notifications. Use `magenta` as a fill with `on-accent` text, and `magenta-ink` as text, icon or border. One magenta element per region is plenty; if everything is magenta, nothing is.
- Status uses `success`, `warning`, `danger`. Every status also carries a word or glyph (check, !, x); never colour alone. `danger` is not magenta; do not mix them.
- The signal gradient (cyan to magenta, left to right, class `.signal`) is reserved for: the active tab underline, progress fills, the window brand mark and one hero hairline. Never behind text, never on large areas, never on buttons.

**Type.** Three families. `display` (Chakra Petch) for titles and labels, `sans` (IBM Plex Sans) for reading text, `mono` (JetBrains Mono) for data. Base UI size is `body` 14px. Set `label` for button text, tab text, table headers, panel titles. Do not use any other typeface, and do not use weight below 400 or above 700.

**Spacing and layout.** 4px base, seven steps `space-1` to `space-7`. Panel padding `space-4`, gap between panels `space-5`, window margin `space-6`. Controls are 32px tall (`control-md`); 24px for dense toolbars, 40px for a single hero action. A window is: title bar (`titlebar`), sidebar (`sidebar`, 208px, collapses to 48px), content, status bar (`statusbar`). Align everything to the grid; the content area may show the dot grid (`.grid-bg`, `line` dots on a `space-5` pitch) as texture behind panels, never behind text blocks.

**Shape and borders.** Corners are tight and technical: `radius-sm` 2px, `radius-md` 6px, `radius-lg` 10px, `radius-pill` only for toggles, progress and dots. Panels have a 1px `line` border; interactive controls have a 1px `line-strong` border. Do not use border-left accents on cards. The one signature flourish is the corner bracket on a hero panel (`.panel--bracket`): cyan top-left, magenta bottom-right. Use it at most once per window.

**Glow and depth.** Dark mode glows; light mode does not need to. `glow-cyan` and `glow-magenta` appear only on hover or focus of controls and on the live dot. Floating layers (menus, dialogs) use `elevation` and a `scrim` behind. Do not add glow to text, panels at rest or static icons.

**Motion.** Hover, press and focus use `dur-fast` (120ms); tab and toggle changes `dur-base` (200ms); progress and window changes `dur-slow` (360ms); always `ease-out`. Nothing loops except the live dot pulse (optional, 2s) and indeterminate progress. Honour `prefers-reduced-motion` by removing all transitions.

**States.** Hover: border and text move to `cyan-ink`, add `cyan-tint`. Pressed: drop the glow, keep the border. Focus: 2px `focus-ring` outline with 2px offset, always visible with the keyboard. Disabled: `ink-faint` text, `line` border, no glow, no hover. Selected: `surface-overlay` background plus a 1px `cyan-ink` outline.

**Accessibility.** Text is at least 4.5:1 and meaningful borders and icons at least 3:1 on the surfaces their token notes name, in both themes. Cyan and magenta fills carry `on-accent` text (6:1 or better). Keep every control keyboard reachable and show its shortcut with `.kbd` where one exists.

### Iconography

Use a single outline icon set, Lucide, at 16px (toolbars, nav) or 20px (empty states), 1.5px stroke, colour `currentColor`. Icons inherit text colour; active nav icons take `cyan-ink`. No filled icons, no emoji, no multi-colour icons. Status glyphs inside alerts are plain characters (check, !, x, i) in a bordered square, as the Alert component shows.

### Components

AppShell, Button, Field, Toggle, Panel, Badge, Tabs, Table, Progress, Alert. Their classes live in `components/bundle.css`; each component's guideline lists the classes and rules. For toolkits that are not web-based, see the rollout section for how to carry the tokens across.

## 2. Tokens

### Colour

| Token | Dark | Light | Usage |
|---|---|---|---|
| `bg` | `#05060d` | `#f3f5ff` | App window background, behind everything. Ink and muted ink read on it in both themes. |
| `surface` | `#0b0e1a` | `#ffffff` | Default panel, sidebar and input background. Body copy (`ink`, `ink-muted`) reads on it. |
| `surface-raised` | `#121629` | `#eaeefc` | Cards inside panels, table row hover, menus. `ink` and `ink-muted` read on it. |
| `surface-overlay` | `#1a2040` | `#dde3f9` | Selected rows, active nav item, progress track, popovers. `ink` and `ink-muted` read on it. |
| `scrim` | `rgba(2, 3, 8, 0.72)` | `rgba(11, 16, 48, 0.38)` | Dimmed backdrop behind dialogs and command palettes. |
| `line` | `#262d52` | `#cdd4f0` | Decorative hairlines: panel borders, dividers, table rules. Never the only cue that a control exists. |
| `line-strong` | `#6370b6` | `#6c76a8` | Borders of interactive controls (inputs, secondary buttons, toggle tracks). 3:1 or better on every surface in both themes. |
| `ink` | `#e8ecff` | `#0b1030` | Primary text and icons on `bg`, `surface`, `surface-raised` and `surface-overlay`. |
| `ink-muted` | `#9ca5d4` | `#414a78` | Secondary text, labels, captions on `surface` and `surface-raised`. |
| `ink-faint` | `#8089bd` | `#5a6391` | Placeholders and disabled text on `surface` and `surface-raised`. Still 4.5:1 there. |
| `cyan` | `#00e5ff` | `#00c8e8` | Fill colour for primary buttons, toggle-on tracks, progress start and the signal gradient. Put `on-accent` text on it; do not use as text. |
| `magenta` | `#ff2bd6` | `#f01fc8` | Fill colour for the secondary accent: live or AI activity, selection highlights, progress end of the signal gradient. Put `on-accent` text on it. |
| `cyan-ink` | `#19e6ff` | `#00657d` | Cyan as text, icon, link, focus ring and border on `bg`, `surface`, `surface-raised`, `surface-overlay`. 4.5:1 or better in both themes. |
| `magenta-ink` | `#ff6be2` | `#a8008a` | Magenta as text, icon and border on `bg`, `surface`, `surface-raised`, `surface-overlay`. 4.5:1 or better in both themes. |
| `cyan-tint` | `rgba(0, 229, 255, 0.10)` | `rgba(0, 101, 125, 0.08)` | Background wash behind cyan badges, info alerts and hovered ghost buttons. Text on it is `cyan-ink` or `ink`. |
| `magenta-tint` | `rgba(255, 43, 214, 0.12)` | `rgba(168, 0, 138, 0.08)` | Background wash behind magenta badges and live-state alerts. Text on it is `magenta-ink` or `ink`. |
| `on-accent` | `#02101a` | `#02101a` | Text and icons on `cyan` and `magenta` fills. 6:1 or better on both fills in both themes. |
| `focus-ring` | = `cyan-ink` | = `cyan-ink` | 2px keyboard focus outline, offset 2px, on every interactive element. 3:1 or better on all surfaces. |
| `success` | `#2de2a6` | `#00704f` | Success text, icon and border on surfaces. Always pair with the word or a check glyph, never colour alone. |
| `warning` | `#ffc233` | `#7f5400` | Warning text, icon and border on surfaces. Always pair with a word or a ! glyph. |
| `danger` | `#ff6482` | `#c4003a` | Error and destructive text, icon and border on surfaces. Always pair with a word or an x glyph. Lighter than `success` in dark, darker in light, so the pair also differs in lightness. |

### Typography

Families:

- `display`: "Chakra Petch", "Rajdhani", system-ui, sans-serif
- `sans`: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif
- `mono`: "JetBrains Mono", ui-monospace, "Cascadia Code", Consolas, monospace

**Display** (family `display`)

| Style | Size / line | Weight | Tracking | Usage |
|---|---|---|---|---|
| `display-xl` | 40px / 44px | 700 | 0.04em | Splash, empty-state and onboarding headlines. Set uppercase. |
| `display-lg` | 28px / 32px | 700 | 0.04em | Window and page titles. Set uppercase. |
| `heading` | 20px / 26px | 600 | 0.02em | Section headings inside a window. Sentence case. |
| `label` | 11px / 14px | 600 | 0.14em | Panel titles, table headers, button text, tab text, badges. Set uppercase. |

**Text** (family `sans`)

| Style | Size / line | Weight | Tracking | Usage |
|---|---|---|---|---|
| `title` | 16px / 22px | 600 | 0 | Card titles, dialog titles, list item primary line. |
| `body` | 14px / 20px | 400 | 0 | Default UI and paragraph text. The desktop base size. |
| `body-sm` | 12.5px / 18px | 400 | 0 | Helper text, captions, status bar text. |

**Data** (family `mono`)

| Style | Size / line | Weight | Tracking | Usage |
|---|---|---|---|---|
| `mono` | 13px / 18px | 400 | 0 | Code, paths, logs, numeric fields and table figures. |
| `mono-sm` | 11.5px / 16px | 500 | 0.02em | Timestamps, version tags, shortcut hints, dense table cells. |

### Spacing

| Token | Value | Usage |
|---|---|---|
| `space-1` | `4px` | Icon-to-text gap, tight inline spacing. |
| `space-2` | `8px` | Gap between related controls, list item padding. |
| `space-3` | `12px` | Input horizontal padding, compact panel padding. |
| `space-4` | `16px` | Default panel padding, gap between form fields. |
| `space-5` | `24px` | Gap between panels, section spacing. |
| `space-6` | `32px` | Window content margin, large section gaps. |
| `space-7` | `48px` | Empty-state and splash vertical rhythm. |

### Radius

| Token | Value | Usage |
|---|---|---|
| `radius-sm` | `2px` | Badges, checkboxes, table selection outline. |
| `radius-md` | `6px` | Buttons, inputs, toggles, menus. |
| `radius-lg` | `10px` | Panels, dialogs, alerts. |
| `radius-pill` | `999px` | Toggle thumbs, progress bars, status dots. |

### Sizes

| Token | Value | Usage |
|---|---|---|
| `control-sm` | `24px` | Compact button and badge height. |
| `control-md` | `32px` | Default button, input, select and tab height. |
| `control-lg` | `40px` | Primary call-to-action and search field height. |
| `titlebar` | `36px` | Custom window title bar height. |
| `statusbar` | `24px` | Bottom status bar height. |
| `sidebar` | `208px` | Default sidebar width; collapses to 48px. |

### Motion

| Token | Value | Usage |
|---|---|---|
| `dur-fast` | `120ms` | Hover, press and focus transitions. |
| `dur-base` | `200ms` | Tab switches, panel expand, toggle thumb. |
| `dur-slow` | `360ms` | Window-level transitions and progress fill. |
| `ease-out` | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Default easing for every transition. Disable under prefers-reduced-motion. |

### Glow and elevation

| Token | Dark | Light | Usage |
|---|---|---|---|
| `glow-cyan` | `0 0 0 1px rgba(0, 229, 255, 0.55), 0 0 18px rgba(0, 229, 255, 0.30)` | `0 0 0 1px rgba(0, 101, 125, 0.60), 0 4px 14px rgba(0, 200, 232, 0.28)` | Hover and focus-within on cyan controls, active nav item. The only glow; never on body text. |
| `glow-magenta` | `0 0 0 1px rgba(255, 43, 214, 0.55), 0 0 18px rgba(255, 43, 214, 0.30)` | `0 0 0 1px rgba(168, 0, 138, 0.60), 0 4px 14px rgba(240, 31, 200, 0.25)` | Hover on magenta controls and the live-activity indicator. |
| `elevation` | `0 12px 32px rgba(0, 0, 0, 0.55)` | `0 12px 28px rgba(11, 16, 48, 0.16)` | Menus, popovers and dialogs floating above the window. |

## 3. Components

### AppShell

The window frame every desktop app uses: title bar, sidebar, content area and status bar, in that arrangement.

Classes: `.shell`, `.shell__title`, `.shell__brand`, `.shell__mark`, `.shell__win`, `.shell__side`, `.nav-item`, `.nav-group`, `.shell__main`, `.shell__status`, `.live-dot`.

- The consumer provides the app name, nav items, content and status text.
- Mark the current nav item with `aria-current="page"`; it takes the cyan outline, not a side bar.
- Show the magenta `.live-dot` in the status bar only while a job is running.
- Keep the native title bar where the platform requires it and apply the rest of the frame.
- Collapse the sidebar to 48px icons below 900px window width.

### Button

Buttons trigger actions. Classes: `.btn` plus one of `.btn--primary`, `.btn--accent`, `.btn--ghost`, `.btn--danger`, and a size `.btn--sm` or `.btn--lg`.

- One primary (cyan) button per view. Use secondary (plain `.btn`) for the rest.
- Use `.btn--accent` (magenta) only to start live or AI activity, once per region.
- Use `.btn--danger` for destructive actions and confirm them in a dialog.
- Label with a verb, one or two words; text is set uppercase by the class.
- The consumer provides the label and the click handler; add `.kbd` inside to show a shortcut.
- Disabled buttons use the `disabled` attribute, not a lookalike class.

### Field

Text inputs with a label, optional help and an error line. Classes: `.field`, `.input`, `.input--mono`, `.field__help`, `.field__error`.

- Always provide a visible `label`-style caption above the input; placeholders are examples, not labels.
- Use `.input--mono` for paths, ports, codes and any numeric value.
- Flag errors with `aria-invalid="true"` and an error line that starts with the glyph x and says what to do.
- Focus shows the cyan border and glow; do not remove it.
- Keep helper text short, one line, in `body-sm`.

### Toggle

A switch for settings that apply immediately. Classes: `.toggle` wrapping an `<input type="checkbox" role="switch">`.

- Use for on/off settings that take effect at once; use a checkbox plus a Save button for deferred changes.
- The label names the setting, never the state: "Auto-sync", not "Enable auto-sync on or off".
- On is a cyan track with a dark thumb; off is an outlined track. State is never colour alone, since the thumb also moves.
- The consumer provides the label and the change handler.

### Panel

The container for grouped content. Classes: `.panel`, `.panel--raised`, `.panel--bracket`, `.panel__title`, `.stat`, `.stat__unit`.

- Give every panel a `.panel__title` in label style; the right side of the title row can hold a badge.
- Use `.panel--raised` for a panel nested inside another panel.
- Use `.panel--bracket` for the one hero panel in a window; never more than one.
- Do not nest more than two panel levels, and do not add side-border accents.
- The consumer provides the title and the content; padding is `space-4`.

### Badge

A compact status tag. Classes: `.badge` plus `.badge--cyan`, `.badge--magenta`, `.badge--success`, `.badge--warning`, `.badge--danger`.

- A badge always contains a word ("Passed", "3 warnings"); the dot is decoration, never the message.
- Cyan means ready or info, magenta means live, success, warning and danger map to their meanings.
- Keep to one or two words; use mono casing set uppercase by the class.
- The consumer provides the text only.

### Tabs

Switches between views of the same content. Classes: `.tabs` containing `.tab` buttons.

- Mark the active tab with `aria-selected="true"`; it takes cyan text and the signal underline.
- Use three to six tabs with one-word labels; use the sidebar for anything larger.
- Support arrow keys to move between tabs and Enter or Space to select.
- The consumer provides the labels, the selected state and the panel content.

### Table

A dense data table. Classes: `.table`, with `.num` on right-aligned numeric cells.

- Headers use label style; cells use `mono-sm`. Put the table in a `.panel` with `padding: 0`.
- Right-align numbers and put units in the header or after the value.
- Mark the selected row with `aria-selected="true"`; hover is automatic.
- Show status as a Badge with a word, not a coloured dot.
- The consumer provides columns, rows and the selection handler. Sort by clicking the header and show the direction with an arrow glyph.

### Progress

A thin progress bar with a mono caption. Classes: `.progress`, `.progress__meta`, `.progress__track`, `.progress__fill`, plus `.progress--success` or `.progress--danger`.

- The default fill is the signal gradient; success and danger switch to a solid status colour.
- Always show the label and the figure in `.progress__meta`; state the result in words ("100% done", "Upload failed at").
- Set the fill width inline; for unknown duration, animate an indeterminate fill and honour reduced motion.

### Alert

An inline message about state. Classes: `.alert` plus `.alert--info`, `.alert--live`, `.alert--success`, `.alert--warning`, `.alert--danger`, with `.alert__icon`, `.alert__title`, `.alert__body`.

- The icon square holds a plain glyph: i, ~, a check, !, or x. The title is always present; the body says what to do next.
- Use `.alert--live` for running agents and jobs, `.alert--danger` for errors that need action.
- The consumer provides the title and body; place alerts at the top of the area they refer to, not floating.

## 4. Component stylesheet

Save as `ui.css` and load after the tokens CSS. Requires the custom properties above (e.g. `--cyan`, `--surface`) defined per theme.

```css
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 14px/20px var(--font-sans); -webkit-font-smoothing: antialiased; }
.stage { padding: 20px; background: var(--bg); min-height: 100%; color: var(--ink); }
.row { display: flex; flex-wrap: wrap; gap: var(--space-3); align-items: center; }
.col { display: flex; flex-direction: column; gap: var(--space-3); }
:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 2px; }
.display-xl, .display-lg, .label { text-transform: uppercase; }
.label { color: var(--ink-muted); }
.signal { background: linear-gradient(90deg, var(--cyan), var(--magenta)); }
.grid-bg { background-image: radial-gradient(var(--line) 1px, transparent 1px); background-size: var(--space-5) var(--space-5); }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }

/* Button */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); height: var(--control-md); padding: 0 var(--space-4); border: 1px solid var(--line-strong); border-radius: var(--radius-md); background: transparent; color: var(--ink); font: 600 11px/14px var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; cursor: pointer; transition: box-shadow var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out), background var(--dur-fast) var(--ease-out); }
.btn:hover { border-color: var(--cyan-ink); color: var(--cyan-ink); background: var(--cyan-tint); }
.btn--primary { background: var(--cyan); border-color: var(--cyan-ink); color: var(--on-accent); }
.btn--primary:hover { background: var(--cyan); color: var(--on-accent); box-shadow: var(--glow-cyan); }
.btn--accent { background: var(--magenta); border-color: var(--magenta-ink); color: var(--on-accent); }
.btn--accent:hover { background: var(--magenta); color: var(--on-accent); border-color: var(--magenta-ink); box-shadow: var(--glow-magenta); }
.btn--ghost { border-color: transparent; color: var(--ink-muted); }
.btn--danger { border-color: var(--danger); color: var(--danger); }
.btn--danger:hover { border-color: var(--danger); color: var(--danger); background: transparent; box-shadow: 0 0 0 1px var(--danger); }
.btn--sm { height: var(--control-sm); padding: 0 var(--space-3); }
.btn--lg { height: var(--control-lg); padding: 0 var(--space-5); }
.btn:disabled { color: var(--ink-faint); border-color: var(--line); background: transparent; box-shadow: none; cursor: not-allowed; }
.kbd { font: 500 11.5px/16px var(--font-mono); color: var(--ink-muted); border: 1px solid var(--line-strong); border-radius: var(--radius-sm); padding: 0 var(--space-1); }

/* Field */
.field { display: flex; flex-direction: column; gap: var(--space-1); min-width: 220px; }
.field__help { font: 400 12.5px/18px var(--font-sans); color: var(--ink-muted); }
.field__error { font: 400 12.5px/18px var(--font-sans); color: var(--danger); }
.input { height: var(--control-md); padding: 0 var(--space-3); background: var(--surface); color: var(--ink); border: 1px solid var(--line-strong); border-radius: var(--radius-md); font: 400 14px/20px var(--font-sans); transition: box-shadow var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out); }
.input--mono { font: 400 13px/18px var(--font-mono); }
.input::placeholder { color: var(--ink-faint); }
.input:hover { border-color: var(--cyan-ink); }
.input:focus { outline: none; border-color: var(--cyan-ink); box-shadow: var(--glow-cyan); }
.input[aria-invalid="true"] { border-color: var(--danger); }
.input:disabled { color: var(--ink-faint); border-color: var(--line); background: var(--bg); cursor: not-allowed; }

/* Toggle and check */
.toggle { display: inline-flex; align-items: center; gap: var(--space-2); cursor: pointer; font: 400 14px/20px var(--font-sans); color: var(--ink); }
.toggle input { appearance: none; -webkit-appearance: none; margin: 0; position: relative; width: 36px; height: 20px; border: 1px solid var(--line-strong); border-radius: var(--radius-pill); background: var(--surface); cursor: pointer; transition: background var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out); }
.toggle input::after { content: ""; position: absolute; top: 3px; left: 3px; width: 12px; height: 12px; border-radius: var(--radius-pill); background: var(--ink-muted); transition: transform var(--dur-base) var(--ease-out), background var(--dur-base) var(--ease-out); }
.toggle input:checked { background: var(--cyan); border-color: var(--cyan-ink); }
.toggle input:checked::after { transform: translateX(16px); background: var(--on-accent); }
.toggle input:hover { box-shadow: var(--glow-cyan); }
.toggle input:disabled { border-color: var(--line); cursor: not-allowed; box-shadow: none; }
.toggle input:disabled::after { background: var(--ink-faint); }

/* Panel */
.panel { position: relative; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: var(--space-4); }
.panel--raised { background: var(--surface-raised); }
.panel__title { display: flex; justify-content: space-between; align-items: center; margin: 0 0 var(--space-3); font: 600 11px/14px var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-muted); }
.panel--bracket::before, .panel--bracket::after { content: ""; position: absolute; width: 14px; height: 14px; border: 2px solid var(--cyan-ink); pointer-events: none; }
.panel--bracket::before { top: -1px; left: -1px; border-right: 0; border-bottom: 0; border-top-left-radius: var(--radius-lg); }
.panel--bracket::after { bottom: -1px; right: -1px; border-left: 0; border-top: 0; border-bottom-right-radius: var(--radius-lg); border-color: var(--magenta-ink); }
.stat { font: 700 28px/32px var(--font-display); letter-spacing: 0.04em; color: var(--ink); }
.stat__unit { font: 500 11.5px/16px var(--font-mono); color: var(--ink-muted); margin-left: var(--space-1); }

/* Badge */
.badge { display: inline-flex; align-items: center; gap: 6px; height: 20px; padding: 0 var(--space-2); border: 1px solid currentColor; border-radius: var(--radius-sm); font: 500 11.5px/16px var(--font-mono); letter-spacing: 0.02em; text-transform: uppercase; color: var(--ink-muted); }
.badge::before { content: ""; width: 6px; height: 6px; border-radius: var(--radius-pill); background: currentColor; }
.badge--cyan { color: var(--cyan-ink); background: var(--cyan-tint); }
.badge--magenta { color: var(--magenta-ink); background: var(--magenta-tint); }
.badge--success { color: var(--success); }
.badge--warning { color: var(--warning); }
.badge--danger { color: var(--danger); }

/* Tabs */
.tabs { display: flex; gap: var(--space-1); border-bottom: 1px solid var(--line); }
.tab { position: relative; height: var(--control-md); padding: 0 var(--space-4); background: transparent; border: 0; color: var(--ink-muted); font: 600 11px/14px var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; cursor: pointer; transition: color var(--dur-fast) var(--ease-out); }
.tab:hover { color: var(--ink); }
.tab[aria-selected="true"] { color: var(--cyan-ink); }
.tab[aria-selected="true"]::after { content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px; background: linear-gradient(90deg, var(--cyan), var(--magenta)); }

/* Table */
.table { width: 100%; border-collapse: collapse; font: 500 11.5px/16px var(--font-mono); letter-spacing: 0.02em; color: var(--ink); }
.table th { text-align: left; padding: var(--space-2) var(--space-3); border-bottom: 1px solid var(--line-strong); font: 600 11px/14px var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-muted); }
.table td { padding: var(--space-2) var(--space-3); border-bottom: 1px solid var(--line); }
.table tbody tr:hover { background: var(--surface-raised); }
.table tbody tr[aria-selected="true"] { background: var(--surface-overlay); box-shadow: inset 0 0 0 1px var(--cyan-ink); }
.table .num { text-align: right; }

/* Progress */
.progress { display: flex; flex-direction: column; gap: var(--space-1); }
.progress__meta { display: flex; justify-content: space-between; font: 500 11.5px/16px var(--font-mono); color: var(--ink-muted); }
.progress__track { height: 6px; background: var(--surface-overlay); border-radius: var(--radius-pill); overflow: hidden; }
.progress__fill { height: 100%; background: linear-gradient(90deg, var(--cyan), var(--magenta)); border-radius: var(--radius-pill); transition: width var(--dur-slow) var(--ease-out); }
.progress--success .progress__fill { background: var(--success); }
.progress--danger .progress__fill { background: var(--danger); }

/* Alert */
.alert { display: flex; gap: var(--space-3); align-items: flex-start; padding: var(--space-3) var(--space-4); background: var(--surface-raised); border: 1px solid var(--line-strong); border-radius: var(--radius-lg); color: var(--ink); }
.alert__icon { flex: none; width: 20px; height: 20px; display: grid; place-items: center; border: 1px solid currentColor; border-radius: var(--radius-sm); font: 700 12px/1 var(--font-mono); }
.alert__title { font: 600 14px/20px var(--font-sans); }
.alert__body { font: 400 12.5px/18px var(--font-sans); color: var(--ink-muted); }
.alert--info .alert__icon { color: var(--cyan-ink); }
.alert--info { background: var(--cyan-tint); border-color: var(--cyan-ink); }
.alert--live .alert__icon { color: var(--magenta-ink); }
.alert--live { background: var(--magenta-tint); border-color: var(--magenta-ink); }
.alert--success .alert__icon { color: var(--success); }
.alert--success { border-color: var(--success); }
.alert--warning .alert__icon { color: var(--warning); }
.alert--warning { border-color: var(--warning); }
.alert--danger .alert__icon { color: var(--danger); }
.alert--danger { border-color: var(--danger); }

/* App shell */
.shell { display: grid; grid-template-columns: var(--sidebar) 1fr; grid-template-rows: var(--titlebar) 1fr var(--statusbar); height: 380px; background: var(--bg); border: 1px solid var(--line-strong); border-radius: var(--radius-lg); overflow: hidden; }
.shell__title { grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between; padding: 0 var(--space-3); background: var(--surface); border-bottom: 1px solid var(--line); font: 600 11px/14px var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-muted); }
.shell__brand { display: flex; align-items: center; gap: var(--space-2); color: var(--ink); }
.shell__mark { width: 14px; height: 14px; border-radius: var(--radius-sm); background: linear-gradient(135deg, var(--cyan), var(--magenta)); }
.shell__win { display: flex; gap: var(--space-2); }
.shell__win i { width: 10px; height: 10px; border: 1px solid var(--line-strong); border-radius: var(--radius-sm); }
.shell__side { background: var(--surface); border-right: 1px solid var(--line); padding: var(--space-3) var(--space-2); display: flex; flex-direction: column; gap: var(--space-1); }
.nav-item { display: flex; align-items: center; gap: var(--space-2); height: var(--control-md); padding: 0 var(--space-3); border: 1px solid transparent; border-radius: var(--radius-md); background: transparent; color: var(--ink-muted); font: 400 14px/20px var(--font-sans); cursor: pointer; text-align: left; transition: color var(--dur-fast) var(--ease-out), background var(--dur-fast) var(--ease-out); }
.nav-item:hover { color: var(--ink); background: var(--surface-raised); }
.nav-item[aria-current="page"] { color: var(--cyan-ink); background: var(--surface-overlay); border-color: var(--cyan-ink); }
.nav-item .kbd { margin-left: auto; }
.nav-group { margin: var(--space-3) var(--space-3) var(--space-1); font: 600 11px/14px var(--font-display); letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-faint); }
.shell__main { padding: var(--space-4); display: flex; flex-direction: column; gap: var(--space-4); overflow: hidden; background-image: radial-gradient(var(--line) 1px, transparent 1px); background-size: var(--space-5) var(--space-5); }
.shell__status { grid-column: 1 / -1; display: flex; align-items: center; gap: var(--space-4); padding: 0 var(--space-3); background: var(--surface); border-top: 1px solid var(--line); font: 500 11.5px/16px var(--font-mono); color: var(--ink-muted); }
.live-dot { display: inline-block; width: 8px; height: 8px; margin-right: var(--space-1); border-radius: var(--radius-pill); background: var(--magenta); box-shadow: var(--glow-magenta); }
```

## 5. Token CSS (starter)

```css
:root, [data-theme="dark"] {
  --bg: #05060d;
  --surface: #0b0e1a;
  --surface-raised: #121629;
  --surface-overlay: #1a2040;
  --scrim: rgba(2, 3, 8, 0.72);
  --line: #262d52;
  --line-strong: #6370b6;
  --ink: #e8ecff;
  --ink-muted: #9ca5d4;
  --ink-faint: #8089bd;
  --cyan: #00e5ff;
  --magenta: #ff2bd6;
  --cyan-ink: #19e6ff;
  --magenta-ink: #ff6be2;
  --cyan-tint: rgba(0, 229, 255, 0.10);
  --magenta-tint: rgba(255, 43, 214, 0.12);
  --on-accent: #02101a;
  --focus-ring: var(--cyan-ink);
  --success: #2de2a6;
  --warning: #ffc233;
  --danger: #ff6482;
  --glow-cyan: 0 0 0 1px rgba(0, 229, 255, 0.55), 0 0 18px rgba(0, 229, 255, 0.30);
  --glow-magenta: 0 0 0 1px rgba(255, 43, 214, 0.55), 0 0 18px rgba(255, 43, 214, 0.30);
  --elevation: 0 12px 32px rgba(0, 0, 0, 0.55);
}
[data-theme="light"] {
  --bg: #f3f5ff;
  --surface: #ffffff;
  --surface-raised: #eaeefc;
  --surface-overlay: #dde3f9;
  --scrim: rgba(11, 16, 48, 0.38);
  --line: #cdd4f0;
  --line-strong: #6c76a8;
  --ink: #0b1030;
  --ink-muted: #414a78;
  --ink-faint: #5a6391;
  --cyan: #00c8e8;
  --magenta: #f01fc8;
  --cyan-ink: #00657d;
  --magenta-ink: #a8008a;
  --cyan-tint: rgba(0, 101, 125, 0.08);
  --magenta-tint: rgba(168, 0, 138, 0.08);
  --on-accent: #02101a;
  --focus-ring: var(--cyan-ink);
  --success: #00704f;
  --warning: #7f5400;
  --danger: #c4003a;
  --glow-cyan: 0 0 0 1px rgba(0, 101, 125, 0.60), 0 4px 14px rgba(0, 200, 232, 0.28);
  --glow-magenta: 0 0 0 1px rgba(168, 0, 138, 0.60), 0 4px 14px rgba(240, 31, 200, 0.25);
  --elevation: 0 12px 28px rgba(11, 16, 48, 0.16);
}
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --radius-sm: 2px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --radius-pill: 999px;
  --control-sm: 24px;
  --control-md: 32px;
  --control-lg: 40px;
  --titlebar: 36px;
  --statusbar: 24px;
  --sidebar: 208px;
  --dur-fast: 120ms;
  --dur-base: 200ms;
  --dur-slow: 360ms;
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
  --font-display: "Chakra Petch", "Rajdhani", system-ui, sans-serif;
  --font-sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "Cascadia Code", Consolas, monospace;
}
```

## 6. Rolling out to desktop apps

How to bring an existing desktop app onto this system without redesigning it from scratch. Do the steps in order and stop at the first one that is enough for the app.

### 1. One shared theme file per app

Create one theme source in the app, generated from `tokens.json` (or `tokens.css` for web-based shells). Everything else reads from it. Do not copy hex values into individual screens.

- **Electron, Tauri, web-view or any HTML shell:** load `tokens.css` and `components/bundle.css`, set `data-theme` on `<html>`, and remap existing class names onto the component classes (`.btn`, `.input`, `.panel`, and so on).
- **Python (PyQt, PySide, CustomTkinter, Tkinter):** generate a small `theme.py` with two dictionaries, `DARK` and `LIGHT`, whose keys are the token names (`bg`, `surface`, `ink`, `cyan`, and so on) and whose values are the hex strings. Build one stylesheet or style function from the active dictionary; switching theme re-applies it.
- **Windows-native (WPF, WinUI, AutoHotkey GUIs):** put the same keys in a resource dictionary or a config file, and load the active theme at start-up. Tint every control from those keys.
- **Android or other:** map tokens to the platform's theme attributes; keep the names identical.

Rule: token names are the contract. If a platform cannot express a token exactly (glow, gradient), approximate with a border in `cyan-ink` or `magenta-ink` and keep the rest.

### 2. Window frame

Every app window follows the AppShell: title bar, sidebar, content, status bar. Where the platform forbids a custom title bar, keep the native one and apply the rest. Put the app name in the title bar in `label` style with the signal mark to its left. Show connection or job state in the status bar, with the magenta live dot only while something is running.

### 3. Component pass

Replace controls in this order: buttons, inputs and selects, toggles, tabs, tables, panels, alerts, progress. One primary button per view. Check each screen in both themes before moving on.

### 4. Fonts

Bundle Chakra Petch (500, 600, 700), IBM Plex Sans (400, 500, 600) and JetBrains Mono (400, 500) with the app so it works offline. If a font cannot load, the fallback stacks in the type tokens apply.

### 5. Acceptance checklist

- Theme switch works live, and the OS preference is the first-run default.
- No hex values outside the theme file.
- Every interactive element has hover, focus, pressed and disabled states from this system.
- Focus ring visible by keyboard everywhere.
- Status is never colour alone.
- Magenta appears at most once per region; the signal gradient appears only where the guideline allows.

### Token cheat sheet

| Token | Dark | Light |
| --- | --- | --- |
| bg | #05060d | #f3f5ff |
| surface | #0b0e1a | #ffffff |
| surface-raised | #121629 | #eaeefc |
| surface-overlay | #1a2040 | #dde3f9 |
| line | #262d52 | #cdd4f0 |
| line-strong | #6370b6 | #6c76a8 |
| ink | #e8ecff | #0b1030 |
| ink-muted | #9ca5d4 | #414a78 |
| ink-faint | #8089bd | #5a6391 |
| cyan | #00e5ff | #00c8e8 |
| magenta | #ff2bd6 | #f01fc8 |
| cyan-ink | #19e6ff | #00657d |
| magenta-ink | #ff6be2 | #a8008a |
| on-accent | #02101a | #02101a |
| success | #2de2a6 | #00704f |
| warning | #ffc233 | #7f5400 |
| danger | #ff6482 | #c4003a |
