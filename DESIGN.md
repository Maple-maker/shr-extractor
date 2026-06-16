# SHR Command Dashboard Design System

## Design Direction

The dashboard should feel like a command post accountability surface: focused, legible, serious, and fast to scan under pressure. It should not look like a generic upload utility or a decorative SaaS admin template.

The visual tone should balance two needs:

- operational density for repeated daily use
- calm clarity so exception states stand out without visual chaos

## Experience Priorities

1. Exceptions should be visible before everything else.
2. High-value actions should require minimal pointer travel and few clicks.
3. Users should be able to scan by assignee, location, and discrepancy status without reading long prose.
4. The interface should remain effective on laptop and tablet screens used in offices, motor pools, and arms rooms.

## Layout Model

- Primary layout: full-width application shell, not a centered marketing card
- Header: compact command bar with dashboard identity, import/export actions, and current dataset context
- Top band: exception summary tiles and review counters
- Main area: dense inventory table plus secondary grouped views
- Detail surface: side panel or drawer for item-level editing
- Section styling: unframed bands and panels; avoid stacking decorative cards inside cards

## Visual System

### Color Tokens

Use a grounded, operational palette with warm alert colors and neutral field tones. Avoid purple-heavy UI and avoid a flat monochrome navy treatment.

- `--bg-canvas`: `#f3f1ea`
- `--bg-panel`: `#fbf8f1`
- `--bg-panel-strong`: `#e5dfd0`
- `--ink-strong`: `#1f2a2e`
- `--ink-body`: `#344248`
- `--ink-muted`: `#66757c`
- `--line-subtle`: `#c7c0b1`
- `--line-strong`: `#8f866f`
- `--accent-command`: `#2f5d50`
- `--accent-command-strong`: `#1f4339`
- `--accent-attention`: `#b15b2d`
- `--accent-danger`: `#8f2d23`
- `--accent-warning`: `#c48a18`
- `--accent-info`: `#315f7d`
- `--status-ok`: `#567a35`
- `--status-new`: `#315f7d`
- `--status-missing`: `#8f2d23`
- `--status-review`: `#b15b2d`

### Usage Rules

- Canvas and panels should stay light to support long reading sessions and printing if needed.
- Use dark ink colors for text; avoid low-contrast gray-on-tan combinations.
- Reserve saturated colors for true status, actions, and exception emphasis.
- Row states and badges must include iconography or text labels in addition to color.

## Typography

Use a sturdy serif-plus-sans pairing that feels official and readable, with local fallbacks only.

- Display/headings: `Georgia`, `Times New Roman`, serif
- UI/body/table text: `Trebuchet MS`, `Segoe UI`, sans-serif
- Data requiring alignment: `Consolas`, `Courier New`, monospace

Typography rules:

- Letter spacing stays at `0`
- Hero-scale type is not appropriate for this product
- Headings should be compact and disciplined
- Table text should be optimized for scanning, not branding
- Serial numbers, LINs, NSNs, and counts may use monospace selectively

## Component Vocabulary

- Exception tile: small summary block with count, label, and one-sentence operational meaning
- Filter bar: segmented controls, toggles, search, and quick filters
- Inventory table: sticky headers, sortable columns, row status markers, and durable widths
- Status badge: text plus icon, never color alone
- Detail drawer: serial-level editing form and review history context
- Grouped list: assignee or location rollups with counts and unresolved-item indicators
- Save/export controls: always visible, simple, and explicit

## Interaction Rules

- Editing should happen inline where safe, and in the detail panel when more context is needed.
- Searches and filters should update quickly and preserve the current editing context where possible.
- High-risk destructive actions should require confirmation.
- Empty states should be operationally useful, for example: `No items are missing an assignee.`
- Import and merge states must explain what changed:
  - new items
  - missing-from-latest items
  - preserved annotations
  - low-confidence matches

## Motion Rules

- Motion should support orientation, not decoration.
- Use subtle transitions for:
  - opening the detail drawer
  - updating counters after filters/imports
  - revealing status changes after save or merge
- Keep durations short, around `120ms` to `180ms`.
- Respect `prefers-reduced-motion` by removing non-essential animation and using instant state changes.

## Accessibility Rules

- WCAG AA contrast is required for text, controls, focus states, and status surfaces.
- Every interactive control must be keyboard reachable.
- Focus indicators must remain clearly visible against light and strong backgrounds.
- Tables need readable hover and focus behavior without relying on tiny hit targets.
- Icons require text labels or tooltips where meaning is not obvious.

## Content And Labeling

Use plain operational language:

- `Signed Down To`
- `Sub-holder`
- `Current Location`
- `Discrepancy`
- `Last Reviewed`
- `Missing From Latest SHR`
- `Needs Assignee`
- `Needs Location`

Avoid vague software labels such as:

- `metadata`
- `records`
- `entity`
- `object state`

## Dashboard Behavior Guidance

- Default landing view after generation should be the exception-first dashboard, not a raw table.
- Inventory table must still be available immediately for supply workflows.
- The item detail surface should be the single source of truth for extended notes and structured location fields.
- Save state should be obvious so users know whether they need to export a refreshed HTML file.

## Offline Implementation Constraints

- No CDN fonts, icon packs, or JavaScript frameworks in the exported dashboard.
- Any icons should be inline SVG or code-native shapes.
- CSS and JavaScript needed for daily use should be embedded directly in the saved HTML.
- Exported artifacts must remain functional with network access disabled.
