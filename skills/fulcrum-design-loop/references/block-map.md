# Block map: design element -> OutSystems UI block

Derived from outsystems-design-to-app v1.4.1 (MIT, Copyright (c) 2026 OutSystems), condensed and modified; see THIRD-PARTY-NOTICE.md. Every row below is [UNVERIFIED] (source: official design-to-app skill) until observed on the tenant. Probe before relying: block names, placeholders, and which blocks exist are tenant facts (OutSystemsUI version); check `tenant-profile.md` section 2 (UI blocks), where a block is probed by attempting to reference it, before the gate accepts a row; whether a published-state search can list the blocks a tenant offers is `[UNVERIFIED]` (tool facts: `../../fulcrum-mentor-turns/references/mcp-surface.md`). No per-block inputs are listed on purpose; read them from the tenant.

## Region -> block [UNVERIFIED] (source: official design-to-app skill)

| Design element | Block / widget |
|---|---|
| Page chrome, left nav (with top bar) | LayoutSideMenu (top bar built in; nav goes in a Menu block) |
| Page chrome, top nav only | LayoutTopMenu |
| Modal content, login, embed (no chrome) | LayoutBlank (never the default for full screens) |
| Screen title | Title placeholder of the layout, h1 via AdvancedHtml |
| N equal columns, 2 to 6 | Columns2..Columns6 |
| Unequal split (~1/3 + 2/3, ~1/4 + 3/4) | ColumnsSmallLeft / ColumnsSmallRight / ColumnsMediumLeft / ColumnsMediumRight |
| Repeating card or item grid | Gallery |
| Card surface | Card, CardItem, CardSectioned |
| Tab header + switching content | Tabs |
| Stepper / multi-step flow | Wizard |
| Collapsible sections | Accordion |
| Swipeable cards, slideshow | Carousel (a frame named Carousel/Slider is Carousel, never Columns3) |
| Side drawer, slide-in panel | Sidebar |
| Modal, popover, toast, alert | Modal, Popover, Notification/Alert blocks, wired to show/hide |
| Status chip, numeric pill | Tag, Badge |
| Linear progress | ProgressBar |
| Radial progress | ProgressCircle |
| KPI number tile | Card + text (counter pattern if the tenant has it) |
| Bar / line / area / donut chart | BarChart, LineChart, AreaChart, DonutChart (+ legend/series styling blocks) |
| Segmented strip / sparkline | stacked-100 BarChart / line chart with axes hidden |
| Avatar / initials | UserAvatar |
| Tables | TableRecords bound to a populated aggregate |
| Lists with rows | List + ListItem |
| Breadcrumb, pagination | Breadcrumbs, Pagination |
| Inputs, dropdown, switch, radio, textarea | Input, Dropdown, DropdownSearch, Switch, RadioGroup, TextArea |
| Buttons, clickable actions | Button, Link (never Container + click) |
| Icon | Icon widget; glyph name and font are tenant facts (tenant-profile.md), mapped at the gate, never hardcoded from the design source |
| Map | Map block (provider varies by tenant) |
| Hero gradient, decorative banner, ornament | Container + one named theme class (the valid CSS case) |

Fallback order when no block fits: AdvancedHtml with a semantic tag, then a platform widget, then Container as a pure positioning wrapper.

## Reject rules [UNVERIFIED] (source: official design-to-app skill)

- Two or more children side by side, or a grid, at screen or section level: use an Adaptive block row above. Reject a node whose layout is `display-flex`, `display-grid`, `flex-1`, `grid-template-columns`, `repeat(N,1fr)`.
- Reject Container + CSS standing in for a button, chart, carousel, progress bar, tag, avatar, input, icon, or repeating rows.
- Reject a class name that implies structure (`.card`, `.tabs`, `.carousel`, `.button`, `.sidebar`) on a Container.
- Exactly one Layout block per screen; never nest two. The default layout a new screen ships with must be removed before adding the chosen one.
- Exception 1: inline alignment inside a single block placeholder (icon + text in a card slot, title left / action right in one card).
- Exception 2: an exact-ratio split no Adaptive block hits (e.g. 62/38), only as one named class defined once in the theme, never inline.
- Interactive or data widgets (Upload, Input, Form, Button, Table, Chart) must not sit inside a Link; a clickable card is fine only when its content is static.
- One primary action per screen = one button wired once; no second Button or Link for the same label/target.
- Fulcrum agrees: Gallery for repeating grids; flex/wrap only if Gallery is unavailable on the tenant.

## Always-block primitives [UNVERIFIED] (source: official design-to-app skill)

Gate check 5. These elements always go through the block or widget, never a Container plus CSS, even when the source gives exact pixel values:

| Element | Block / widget |
|---|---|
| Buttons, clickable actions | Button, Link |
| Charts (bar, line, area, donut) | BarChart, LineChart, AreaChart, DonutChart |
| Carousels, horizontally scrolling card stacks | Carousel |
| Icons | Icon widget (glyph name and font from tenant-profile.md section 3) |
| Inputs (text, date, number, dropdown, textarea, checkbox, switch, radio) | Input, Dropdown, TextArea, Checkbox, Switch, RadioGroup |
| Avatars (image, initials, silhouette) | UserAvatar |
| Linear and radial progress | ProgressBar, ProgressCircle |
| Status pills, numeric badges | Tag, Badge |
| Repeating data rows | List + ListItem |
| N equal columns, 2 to 6 | Columns2..Columns6 |
| Repeating card or item grid | Gallery (flex/wrap only if Gallery is unavailable) |
| Tab header + switching content | Tabs |
| Card-shaped surface | Card, CardItem, CardSectioned |

Container plus one named theme class stays valid for decorative banners, ornaments and pure positioning wrappers: use the block whenever one exists for the role.

## Default children [UNVERIFIED] (source: official design-to-app skill)

Some blocks ship placeholder children that survive next to new content: Carousel (one List in its items slot), Tabs (3 header + 3 content items), Wizard (a few steps), Accordion (a few items), Button/Link (default text). Official advice: delete all of them before adding content.
Fulcrum conflict: apply the REPEAT-or-POSITION test instead of stripping everything. Keep a default child that is the repeater or positioned slot you need (the Carousel's List when the content repeats); delete the rest. Observe the real defaults on the tenant first.

## Reserved names and class rules [UNVERIFIED] (source: official design-to-app skill)

- Do not use `main-content`, `sidebar`, `header`, `content`, `footer` as custom class names; the theme styles them and both rules apply. Prefix with the app name.
- Avoid `<aside>`, nested `<nav>` in brand areas, and raw `<table>` without display overrides.
- Link colour rules need `!important` or the theme's `a` rule wins and links vanish.
- ExtendedClass is additive to the block's default class. Official advice puts project classes on every block; Fulcrum conflict: no project ExtendedClass on overlay blocks (Modal, Popover, Sidebar, Notification).
- Every custom class a region references must be defined in the theme; an undefined class is a silent no-op.
- Official advice never generalises extracted hex values; Fulcrum conflict: the fidelity bar decides whether colour drift earns a fix turn.

## Sizing and polish [UNVERIFIED] (source: official design-to-app skill)

- Charts need a real height (about 28px minimum; sparkline ~40px; segmented strip 14-20px) and a populated bound source; an empty list draws nothing.
- Numbers and labels: `white-space:nowrap` plus min-width; grids get explicit column sizes.
- Page background must be applied to the screen root, not merely defined.
- Headline KPI values come from stored or seeded-to-match data, not a live count over seed rows.
- Show the value in cells and labels, never a literal binding path.
- Typography hierarchy: h1 screen title, h2 sections, h3 card titles.

## Gotchas [UNVERIFIED] (source: official design-to-app skill; originates from the claude-oml-tool corpus)

Kept here as observed-or-discard; not promoted to engine-traps.
- Icons render black on dark surfaces: set an explicit light text colour on the container; font-icon markup (`<i class="...">`) may not render in the runtime; a baked inline SVG ignores `currentColor`, so bake the fill. The official fix names a hardcoded Phosphor font; Fulcrum conflict: icon font and glyph names are tenant facts (tenant-profile.md), mapped at the gate.
- Icon coverage: list every icon location (nav, KPI corners, chips, buttons, search) up front; skipped spots look empty.
- Icon family mismatch: design sources often use a different family than the tenant font; map semantically, not by name.
- Source-page visibility toggles (`display:none` + `.active`) must not be carried over when each section becomes its own screen; keep hidden-by-default only for overlays, realised as real overlay blocks.
- Fidelity details not inferable from the runtime (per-screen header title, table header style, upload zone styling, light icons on coloured tiles) must be stated explicitly.
- A table over an unseeded source renders zero rows. Fulcrum conflict: official seeds one Create call per row with literal dates; Fulcrum seeds in its own step via fulcrum-seed-data loaders with day offsets plus time.
- Publish validators can reject constructs that save fine; a save round-trip is not a quality bar (official file is OmlTool-specific; read only if installed).
- Iterating on one asset keeps a stable URL and revision counter; a new asset per run is the failure.
