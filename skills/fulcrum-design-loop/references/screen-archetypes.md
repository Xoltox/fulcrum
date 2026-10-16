# Screen archetypes

Derived from outsystems-design-to-app v1.4.1 (MIT, Copyright (c) 2026 OutSystems), condensed and modified; see THIRD-PARTY-NOTICE.md. All content is [UNVERIFIED] (source: official design-to-app skill): a checklist of what such screens usually contain, not a spec. Block names follow block-map.md and must be confirmed against the tenant (tenant-profile.md). Each line: regions, blocks, common miss.

- list-table: header with title + primary add; filter bar (search, 1-2 dropdowns; ColumnsSmallLeft); TableRecords with status Tag and row actions; Pagination; empty state with clear-filters. Miss: no empty state, status as plain text. Variant: Gallery cards for image-heavy data.
- dashboard: header + period selector; KPI tiles in ColumnsN; 1-2 charts in Columns2; compact summary list. Miss: tiles not wrapped in a Columns block so they stack; charts without height or data.
- detail-view: header with title, status Tag, Edit/Delete/Back; info card (CardSectioned) of label-value pairs grouped by heading; one table per related entity; Tabs at 3+ related groups. Miss: delete without a confirm modal.
- edit-form: conditional title (New/Edit); Form card, label above input, grouped sections; right-aligned Cancel + Save; per-field validation. Two-column (Columns2) at 6+ fields; Tabs at 10+. Miss: placeholder-only labels, full-width stretched form.
- gallery-grid: header + count + view toggle; filter/sort bar; Gallery of cards (image at fixed ratio, title, meta, action); Pagination; empty state. Variants: catalog, file manager, directory, bento. Miss: Columns used instead of Gallery.
- kanban: board header + filters; horizontal strip of fixed-width columns (header + count Badge + card stack); cards with title, avatar, due date, Tag. No Adaptive block fits a horizontal-scroll board, so expect one named theme class (reject-rule exception 2). Miss: phone layout.
- calendar: header with month label, prev/next, view toggle; 7-column month grid with event previews, week/day variants; optional mini-calendar sidebar. Phone falls back to an agenda list. Miss: today highlight, "show more" overflow.
- timeline: feed header + filters; entries (avatar or icon, actor, action, time) with date separators and a connector line; load-more; empty state. Variants: audit, notifications, social, chat. Miss: date grouping.
- wizard: step indicator (Wizard or ProgressBar); one step's fields; Back / Next (becomes Submit on the last); summary step with edit links; success state. Miss: all fields shown at once, default steps left in.
- settings: category nav (left list or Tabs) beside a form (ColumnsSmallLeft); grouped rows with Switch/Dropdown/Input; per-section save or autosave; danger zone with confirm. Phone: category list, then full-screen form.
- master-detail: left list (~1/3) with search and highlighted selection beside a detail panel (~2/3) with a "select an item" empty state. Phone shows the list only; tap navigates. Miss: no selected-state style.
- inbox-notifications: header with unread Badge and Mark-all-read; list with unread styling, sender, preview, relative time, hover actions; optional detail panel; "inbox zero" empty state. Variants: dropdown, task inbox with approve/reject.
- map-view: header with search/filters; Map with markers and popup card; location list (~35%) synced to the map. Provider and clustering are tenant facts. Miss: list/map selection sync.

## States every screen needs [UNVERIFIED] (source: official design-to-app skill)

- Empty: icon + message + next action, for every list, table, grid and chart; never a blank area.
- Loading: skeleton for 1-3 s, progress bar beyond; submit buttons show a loading state immediately (no dead click).
- Error: inline per field with text and icon (not colour alone), a form-level summary, a retry path for server errors.
