# OutSystems UI v3.0.0 - theme vocabulary

Condensed extract of OutSystems UI, tag `v3.0.0`, taken 2026-10-30. BSD-3-Clause, Copyright (c) 2023, OutSystems; see THIRD-PARTY-NOTICE.md. Not endorsed by OutSystems. Generated once by a maintainer; nothing runs at install.
Library facts are `[SCHEMA]`: the vendor describing one library version, not a tenant. Before relying on a row, compare the tag with the tenant's version: `block-map.md`, heading "OutSystems UI library reference".

Sources at the tag: `docs-ai/llms-tokens.txt`, `docs-ai/llms-utilities.txt`, `docs-ai/osui.icons.json`, `src/scss/01-foundations/_root.scss`, `stories/_helpers/token-data/*.ts`.

## Override rule

Read chain: property -> `--osui-<component>-<prop>` -> `--<role>` -> `--token-*`. Override variables, never component rules: roles or `--token-*` at `:root` for the app, an `--osui-*` knob in one class for an instance. Dark mode is class `os-dark-theme` on `<html>`. Responsive rules are class-driven: the runtime sets `phone`, `tablet` or `desktop` on `<body>`, so write `.phone .x { }`; there are no responsive utility prefixes.

## Theme roles

Set the role that matches the design's meaning. Defaults are copied as the tag publishes them, so a design value can be matched to the nearest role; `-` means the tag's token tables give no value.

| Role | Default token | Default value |
|---|---|---|
| `--color-background-body` | `--token-bg-body` | - |
| `--color-background-surface` | `--token-bg-surface-default` | - |
| `--color-background-raised` | `--token-bg-surface-elevation-2` | - |
| `--color-background-panel` | `--token-bg-surface-elevation-3` | - |
| `--color-background-header` | `--token-bg-surface-default` | - |
| `--color-background-sidemenu` | `--token-bg-surface-default` | - |
| `--color-background-footer` | `--token-bg-surface-default` | - |
| `--color-background-login` | `--token-bg-surface-default` | - |
| `--color-background-input` | `--token-bg-input-default` | - |
| `--color-background-input-disabled` | `--token-bg-input-disabled` | - |
| `--color-text` | `--token-text-default` | #242528 |
| `--color-text-subtle` | `--token-text-subtle` | #383e45 |
| `--color-text-subtlest` | `--token-text-subtlest` | #6c727a |
| `--color-text-disabled` | `--token-text-disabled` | #9fa5ad |
| `--color-text-inverse` | `--token-text-inverse` | #ffffff |
| `--color-text-light` | `--token-text-light` | #ffffff |
| `--color-text-dark` | `--token-text-dark` | #131518 |
| `--color-border` | `--token-border-default` | #d0d7df |
| `--color-border-subtle` | `--token-border-subtle` | #e6eaee |
| `--color-border-subtlest` | `--token-border-subtlest` | #ffffff |
| `--color-border-input` | `--token-border-input-default` | #d0d7df |
| `--color-border-input-hover` | `--token-border-input-hover` | #9fa5ad |
| `--color-border-input-press` | `--token-border-input-press` | #7e858e |
| `--color-border-primary` | `--token-border-primary` | #105cef |
| `--color-focus-outer` | `--token-semantics-primary-base` | #105cef |
| `--color-focus-inner` | `--token-border-boldest` | #242528 |
| `--color-primary` | `--token-semantics-primary-base` | #105cef |
| `--color-primary-hover` | `--token-semantics-primary-800` | #0f54da |
| `--color-primary-selected` | `--token-semantics-primary-900` | #0d4bc3 |
| `--color-primary-active` | `--token-semantics-primary-900` | #0d4bc3 |
| `--color-secondary` | `--token-bg-neutral-bold-default` | - |
| `--color-error` | `--token-semantics-danger-base` | #e0243a |
| `--color-warning` | `--token-semantics-warning-base` | #ffd600 |
| `--color-success` | `--token-semantics-success-base` | #4aae83 |
| `--color-info` | `--token-semantics-info-base` | #105cef |
| `--border-radius-2xs` | `--token-shape-soft-2xs` | 4px |
| `--border-radius-xs` | `--token-shape-soft-xs` | 8px |
| `--border-radius-sm` | `--token-shape-soft-sm` | 12px |
| `--border-radius-md` | `--token-shape-soft-md` | 16px |
| `--border-radius-lg` | `--token-shape-soft-lg` | 8px |
| `--border-radius-xl` | `--token-shape-soft-xl` | 12px |
| `--border-radius-2xl` | `--token-shape-soft-2xl` | 16px |

Layout sizes: `--header-size`, `--header-size-content`, `--side-menu-size`, `--bottom-bar-size`, `--footer-height`.

Legacy aliases, still present but marked "prefer --osui-* knobs or --token-*": `--color-neutral`, `--color-neutral-0..10`, `--border-radius-none|soft|rounded`, `--color-<family>`, `--space-<type>`. A note naming these, or a hex neutral ramp, may be pre-3.0 vocabulary. An invented variable is a silent no-op, so a value set on one proves nothing: confirm by computed style on the first render.

## Instance knobs

The components a design restyles most. Other components: `docs-ai/llms-tokens.txt`, section "Component CSS API knobs".

- btn: btn-min-height btn-background btn-color btn-border-color btn-hover-background btn-active-background btn-border-width btn-border-radius btn-disabled-overlay btn-primary-background btn-primary-border-color btn-primary-color btn-success-background btn-success-border-color (+4 more)
- card: card-background card-border-color card-border-width card-border-radius card-color card-padding card-shadow
- tag: tag-color tag-on-light-color tag-soft-border-radius tag-medium-soft-border-radius
- badge: badge-color badge-on-light-color
- table: table-border-color table-border-radius table-header-background table-header-color table-cell-background table-row-hover-background table-row-stripe-background table-sorted-color table-row-selected-background
- inputs-and-textareas: input-background input-border-color input-hover-border-color input-color input-border-radius textarea-border-radius input-focus-border-color input-focus-ring-color input-error-border-color
- dropdown: dropdown-background dropdown-border-color dropdown-border-width dropdown-color dropdown-border-radius dropdown-popup-border-radius dropdown-hover-border-color dropdown-prompt-color dropdown-list-background dropdown-list-border-color dropdown-list-max-height dropdown-list-shadow dropdown-focus-border-color dropdown-focus-ring-color (+5 more)
- pagination: pagination-button-background pagination-button-border-color pagination-button-border-width pagination-button-font-weight pagination-button-hover-background pagination-button-padding pagination-button-size pagination-button-text-color pagination-active-background pagination-active-border-color pagination-active-color pagination-counter-color pagination-button-border-radius
- section: section-title-color section-title-border-color section-content-color section-title-line-height section-content-line-height section-group-gap
- master-detail: master-detail-background master-detail-border-color master-detail-border-radius
- layout: layout-aside-lines

Names drop the `--osui-` prefix.

## Utility classes

538 classes in 24 families, long form: `<property>[-<side>][-<value>]`. Tailwind short names (`p-4`, `mt-2`) do not exist, so one in a spec is a silent no-op.

- Sides: `top bottom left right`, `x` (inline), `y` (block).
- Steps: `none xs s base m l xl xxl` = 0, 4, 8, 16, 24, 32, 40, 48 px.
- Spacing: `margin-{side}-{step}`, `padding-{side}-{step}`, `gap-{step}`, `row-gap-{step}`, `column-gap-{step}`.
- Layout: `display-flex`, `flex-direction-*`, `flex-wrap-*`, `justify-content-*`, `align-items-*`, `full-width`, `full-height`. Structure still goes through blocks (`block-map.md`, "Reject rules").
- Colour: `background-<hue>[-<shade>]`, `text-<hue>[-<shade>]`. Hues: blue cyan grape green indigo lime orange pink red teal violet yellow primary secondary error info success warning. Shades: lightest lighter light dark darker darkest; none means base. Neutrals: `background-neutral-<0..10>`, `text-neutral-<0..10>`.
- Radius: `border-radius-{none|soft|rounded|circle}`; `shape-soft`, `shape-round`, `shape-rectangular` remap every radius tier.
- Shadow, text, type: `docs-ai/llms-utilities.txt` at the tag.

## Icons

The library ships Phosphor (1530 names; markup `icon ph ph-<name>`) and Font Awesome 4 (786 names; markup `fa fa-<name>`). Which one an app uses is `[TENANT]`: `tenant-profile.md` section 3 wins over this list. A wrong name renders blank or a fallback with no error, and design sources often use another family (a chevron here is `caret`), so map by meaning. Names below exist in the tag's list; anything else: `docs-ai/osui.icons.json`.

| Meaning | `ph-` name | Meaning | `ph-` name |
|---|---|---|---|
| add | plus | error | warning-circle |
| arrow-left | arrow-left | filter | funnel |
| arrow-right | arrow-right | folder | folder |
| attachment | paperclip | home | house |
| bell | bell | info | info |
| calendar | calendar-blank | link | link |
| check | check | list | list |
| chevron-down | caret-down | lock | lock |
| chevron-left | caret-left | logout | sign-out |
| chevron-right | caret-right | menu | list |
| chevron-up | caret-up | more | dots-three |
| clock | clock | phone | phone |
| close | x | search | magnifying-glass |
| copy | copy | settings | gear |
| dashboard | squares-four | star | star |
| delete | trash | upload | upload-simple |
| document | file-text | user | user |
| download | download-simple | users | users |
| edit | pencil-simple | warning | warning |
| email | envelope |  |  |
