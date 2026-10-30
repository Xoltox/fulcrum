#!/usr/bin/env python3
"""Regenerate the vendored OutSystems UI extracts. MAINTAINER ONLY.

Never run at install: install.sh neither copies nor calls this file, and no
skill or role runs it. It takes a tag as argument and reads a local clone of
OutSystems/outsystems-ui as data; it executes nothing from the clone and makes
no network call.

    git clone --depth 1 --branch <tag> \
        https://github.com/OutSystems/outsystems-ui <clone dir>
    python -I scripts/gen-osui-ref.py <tag> <clone dir> [--out <dir>] [--date YYYY-MM-DD]

Needs Python 3.10 or later: write_text takes newline= from 3.10. The tag must look
like v3.0.0, because it becomes part of the output file names.

Keep the clone outside this repository. It writes osui-<tag>-blocks.md and
osui-<tag>-theme.md to --out, by default skills/fulcrum-design-loop/references.

The script cannot tell what the clone has checked out: the output is labelled
with the tag you pass, so check out that tag. The output is rewritten ASCII.

Two things stay by hand after a refresh. Prose in theme_doc (spacing steps, hue
names, the semantic icon table, the knob list) was curated at v3.0.0: review it
against the new tag, since only the assertions below will catch a change. And a
new tag means new file names: update every citation of the old names
(block-map.md, design-spec-format.md, THIRD-PARTY-NOTICE.md) and delete the old
files.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

DEFAULT_OUT = (
    pathlib.Path(__file__).resolve().parent.parent
    / "skills" / "fulcrum-design-loop" / "references"
)

BLOCKS_JSON = "docs-ai/osui.blocks.json"
TOKENS_TXT = "docs-ai/llms-tokens.txt"
UTILITIES_TXT = "docs-ai/llms-utilities.txt"
ICONS_JSON = "docs-ai/osui.icons.json"
ROOT_SCSS = "src/scss/01-foundations/_root.scss"
TOKEN_TABLES = "stories/_helpers/token-data"
TOKEN_TABLE_FILES = ["colors.ts", "shape.ts", "spacing.ts", "elevation.ts", "typography.ts"]

KNOB_COMPONENTS = [
    "btn", "card", "tag", "badge", "table", "inputs-and-textareas", "dropdown",
    "pagination", "section", "master-detail", "layout",
]
KNOBS_SHOWN = 14

ROLE_GROUPS = [
    r"--color-background",
    r"--color-text",
    r"--color-(border|focus)",
    r"--color-(primary|secondary|error|warning|success|info)",
    r"--border-radius",
]
LEGACY_ROLE = re.compile(r"--color-neutral|--border-radius-(none|soft|rounded)$")

SEMANTIC_ICONS = {
    "add": "plus", "arrow-left": "arrow-left", "arrow-right": "arrow-right",
    "attachment": "paperclip", "bell": "bell", "calendar": "calendar-blank",
    "check": "check", "chevron-down": "caret-down", "chevron-left": "caret-left",
    "chevron-right": "caret-right", "chevron-up": "caret-up", "clock": "clock",
    "close": "x", "copy": "copy", "dashboard": "squares-four", "delete": "trash",
    "document": "file-text", "download": "download-simple", "edit": "pencil-simple",
    "email": "envelope", "error": "warning-circle", "filter": "funnel",
    "folder": "folder", "home": "house", "info": "info", "link": "link",
    "list": "list", "lock": "lock", "logout": "sign-out", "menu": "list",
    "more": "dots-three", "phone": "phone", "search": "magnifying-glass",
    "settings": "gear", "star": "star", "upload": "upload-simple", "user": "user",
    "users": "users", "warning": "warning",
}


def read_text(clone, relative):
    return (clone / relative).read_text(encoding="utf8")


def read_json(clone, relative):
    return json.loads(read_text(clone, relative))


def write_ascii(path, lines):
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="ascii", newline="\n")


def to_ascii(text):
    """Map the upstream punctuation to ASCII, drop the rest, collapse whitespace."""
    for source, target in (
        (chr(0x2014), "-"), (chr(0x2013), "-"), (chr(0xb7), "|"), (chr(0x2192), "->"), (chr(0x2026), "..."),
    ):
        text = text.replace(source, target)
    text = text.encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text).strip()


def header(tag, date):
    return (
        f"Condensed extract of OutSystems UI, tag `{tag}`, taken {date}. BSD-3-Clause, "
        "Copyright (c) 2023, OutSystems; see THIRD-PARTY-NOTICE.md. Not endorsed by "
        "OutSystems. Generated once by a maintainer; nothing runs at install.\n"
        "Library facts are `[SCHEMA]`: the vendor describing one library version, not a "
        "tenant. Before relying on a row, compare the tag with the tenant's version: "
        "`block-map.md`, heading \"OutSystems UI library reference\".\n"
    )


def param_default(param):
    default = param.get("default")
    if default in (None, "", '""'):
        return ""
    return to_ascii(re.sub(r"^Entities\.\w+\.", "", str(default)))


def block_line(key, block, enums_used):
    """One index line for a public block; records the enums its parameters use."""
    parts = []
    for param in block.get("params", []):
        if param["name"] == "ExtendedClass":
            continue
        if param.get("typeKind") == "staticEntity" and param.get("typeRef"):
            enums_used.setdefault(param["typeRef"], param.get("values") or [])
        star = "*" if param.get("mandatory") else ""
        default = param_default(param)
        type_name = to_ascii(str(param.get("typeRef") or param.get("type") or ""))
        parts.append(f"{param['name']}{star}:{type_name}" + (f"={default}" if default else ""))
    slots = [to_ascii(s["name"]) for s in block.get("placeholders", [])]
    line = f"- `{key}`"
    if parts:
        line += ": " + ", ".join(parts)
    if slots:
        line += " | slots: " + ", ".join(slots)
    return line


def blocks_doc(clone, tag, date):
    doc = read_json(clone, BLOCKS_JSON)
    module_version = doc["snapshots"][0]["moduleVersion"]
    enums_used = {}
    flows = {}
    no_extended_class = []
    for key, block in doc["blocks"].items():
        if block["flow"] == "Private":
            continue
        if "ExtendedClass" not in [p["name"] for p in block.get("params", [])]:
            no_extended_class.append(key)
        flows.setdefault(block["flow"], []).append(block_line(key, block, enums_used))

    exceptions = ""
    if no_extended_class:
        exceptions = ", except " + ", ".join(f"`{k}`" for k in sorted(no_extended_class))
    lines = [f"# OutSystems UI {tag} - block index", "", header(tag, date)]
    lines += [
        f"Source: `{BLOCKS_JSON}` at the tag, ODC module version "
        f"`{module_version}`. {sum(len(v) for v in flows.values())} public blocks; the "
        "`Private` flow is left out. A key is `<flow>/<name>`, a lookup into this library. "
        "How Mentor names a block is `[UNVERIFIED]`: say the plain name in a prompt.",
        "",
        "Read a line as `key: Param:Type=default` (`*` mandatory; no default means the "
        "type's own; enum defaults drop the `Entities.<Enum>.` prefix) `| slots`. Every "
        "block also takes `ExtendedClass:Text`" + exceptions
        + ". Not listed here at all: layouts, Modal, Popover, Button, Link, Input, Switch, "
        "RadioGroup, TextArea, Checkbox, TableRecords, List, charts, Map, the Icon widget "
        "(`block-map.md`).",
        "",
    ]
    for flow in sorted(flows):
        lines += [f"## {flow}", ""] + flows[flow] + [""]
    lines += ["## Enum values", "", "Identifier parameters take `Entities.<Enum>.<Value>`.", ""]
    for name in sorted(enums_used):
        if enums_used[name]:
            lines.append(f"- {name}: {', '.join(to_ascii(str(v)) for v in enums_used[name])}")
    return lines


def theme_roles(clone):
    """Rows of (role, default token, default value), grouped, legacy aliases dropped."""
    values = {}
    for name in TOKEN_TABLE_FILES:
        text = read_text(clone, f"{TOKEN_TABLES}/{name}")
        for match in re.finditer(
            r'"css_variable":\s*"(--token-[\w-]+)"[^{}]*?"value":\s*"([^"]*)"', text
        ):
            values.setdefault(match.group(1), match.group(2))
    roles = []
    for match in re.finditer(
        r"^\s*(--(?:color|border-radius)-[\w-]+):\s*(.+?);", read_text(clone, ROOT_SCSS), re.M
    ):
        tokens = re.findall(r"variables\.\$token-([\w-]+)", match.group(2))
        token = "--token-" + tokens[0] if tokens else ""
        roles.append((match.group(1), token, values.get(token, "")))
    rows = []
    seen = set()
    for pattern in ROLE_GROUPS:
        for name, token, value in roles:
            if re.match(pattern, name) and name not in seen and not LEGACY_ROLE.search(name):
                seen.add(name)
                rows.append((name, token, value))
    return rows


def knob_lines(clone):
    tokens = read_text(clone, TOKENS_TXT)
    knobs = dict(re.findall(r"^- ([\w-]+): (--osui-.+)$", tokens, re.M))
    lines = []
    for component in KNOB_COMPONENTS:
        if component in knobs:
            names = knobs[component].split()
            shown = [n[len("--osui-"):] for n in names[:KNOBS_SHOWN]]
            more = len(names) - len(shown)
            lines.append(f"- {component}: " + " ".join(shown) + (f" (+{more} more)" if more > 0 else ""))
    return lines


def utility_count(clone):
    match = re.search(r"(\d+) classes in (\d+) families", read_text(clone, UTILITIES_TXT))
    assert match, f"no class count in {UTILITIES_TXT}: read its header and update this script"
    return match.group(1), match.group(2)


def icon_lines(clone):
    icons = read_json(clone, ICONS_JSON)
    phosphor = set(icons["phosphor"]["classes"])
    missing = [name for name in SEMANTIC_ICONS.values() if "ph-" + name not in phosphor]
    assert not missing, f"icons absent at this tag, update SEMANTIC_ICONS: {missing}"
    lines = [
        "## Icons",
        "",
        f"The library ships Phosphor ({len(phosphor)} names; markup `icon ph ph-<name>`) and "
        f"Font Awesome 4 ({len(icons['fontawesome4']['classes'])} names; markup `fa fa-<name>`). "
        "Which one an app uses "
        "is `[TENANT]`: `tenant-profile.md` section 3 wins over this list. A wrong name "
        "renders blank or a fallback with no error, and design sources often use another "
        "family (a chevron here is `caret`), so map by meaning. Names below exist in the "
        f"tag's list; anything else: `{ICONS_JSON}`.",
        "",
        "| Meaning | `ph-` name | Meaning | `ph-` name |",
        "|---|---|---|---|",
    ]
    items = sorted(SEMANTIC_ICONS.items())
    half = (len(items) + 1) // 2
    for index in range(half):
        left = items[index]
        right = items[index + half] if index + half < len(items) else ("", "")
        lines.append(f"| {left[0]} | {left[1]} | {right[0]} | {right[1]} |")
    return lines


def theme_doc(clone, tag, date):
    classes, families = utility_count(clone)
    lines = [f"# OutSystems UI {tag} - theme vocabulary", "", header(tag, date)]
    lines += [
        f"Sources at the tag: `{TOKENS_TXT}`, `{UTILITIES_TXT}`, "
        f"`{ICONS_JSON}`, `{ROOT_SCSS}`, "
        f"`{TOKEN_TABLES}/*.ts`.",
        "",
        "## Override rule",
        "",
        "Read chain: property -> `--osui-<component>-<prop>` -> `--<role>` -> `--token-*`. "
        "Override variables, never component rules: roles or `--token-*` at `:root` for the "
        "app, an `--osui-*` knob in one class for an instance. Dark mode is class "
        "`os-dark-theme` on `<html>`. Responsive rules are class-driven: the runtime sets "
        "`phone`, `tablet` or `desktop` on `<body>`, so write `.phone .x { }`; there are no "
        "responsive utility prefixes.",
        "",
        "## Theme roles",
        "",
        "Set the role that matches the design's meaning. Defaults are copied as the tag "
        "publishes them, so a design value can be matched to the nearest role; `-` means "
        "the tag's token tables give no value.",
        "",
        "| Role | Default token | Default value |",
        "|---|---|---|",
    ]
    for name, token, value in theme_roles(clone):
        lines.append(f"| `{name}` | {'`' + token + '`' if token else '-'} | {to_ascii(value) or '-'} |")
    lines += [
        "",
        "Layout sizes: `--header-size`, `--header-size-content`, `--side-menu-size`, "
        "`--bottom-bar-size`, `--footer-height`.",
        "",
        "Legacy aliases, still present but marked \"prefer --osui-* knobs or --token-*\": "
        "`--color-neutral`, `--color-neutral-0..10`, `--border-radius-none|soft|rounded`, "
        "`--color-<family>`, `--space-<type>`. A note naming these, or a hex neutral ramp, "
        "may be pre-3.0 vocabulary. An invented variable is a silent no-op, so a value set "
        "on one proves nothing: confirm by computed style on the first render.",
        "",
        "## Instance knobs",
        "",
        "The components a design restyles most. Other components: "
        f"`{TOKENS_TXT}`, section \"Component CSS API knobs\".",
        "",
    ]
    lines += knob_lines(clone)
    lines += [
        "",
        "Names drop the `--osui-` prefix.",
        "",
        "## Utility classes",
        "",
        f"{classes} classes in {families} families, long form: `<property>[-<side>][-<value>]`. "
        "Tailwind short names (`p-4`, `mt-2`) do not exist, so one in a spec is a silent "
        "no-op.",
        "",
        "- Sides: `top bottom left right`, `x` (inline), `y` (block).",
        "- Steps: `none xs s base m l xl xxl` = 0, 4, 8, 16, 24, 32, 40, 48 px.",
        "- Spacing: `margin-{side}-{step}`, `padding-{side}-{step}`, `gap-{step}`, "
        "`row-gap-{step}`, `column-gap-{step}`.",
        "- Layout: `display-flex`, `flex-direction-*`, `flex-wrap-*`, `justify-content-*`, "
        "`align-items-*`, `full-width`, `full-height`. Structure still goes through "
        "blocks (`block-map.md`, \"Reject rules\").",
        "- Colour: `background-<hue>[-<shade>]`, `text-<hue>[-<shade>]`. Hues: blue cyan "
        "grape green indigo lime orange pink red teal violet yellow primary secondary "
        "error info success warning. Shades: lightest lighter light dark darker darkest; "
        "none means base. Neutrals: `background-neutral-<0..10>`, `text-neutral-<0..10>`.",
        "- Radius: `border-radius-{none|soft|rounded|circle}`; `shape-soft`, `shape-round`, "
        "`shape-rectangular` remap every radius tier.",
        f"- Shadow, text, type: `{UTILITIES_TXT}` at the tag.",
        "",
    ]
    lines += icon_lines(clone)
    return lines


def main():
    parser = argparse.ArgumentParser(description="Regenerate the OutSystems UI extracts (maintainer only).")
    parser.add_argument("tag", help="the outsystems-ui tag the clone has checked out, e.g. v3.0.0")
    parser.add_argument("clone", type=pathlib.Path, help="local clone of the tag, read as data")
    parser.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT, help="output directory")
    parser.add_argument(
        "--date",
        default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        help="date stamped in the extract header; default today, UTC",
    )
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error("needs Python 3.10 or later")
    if not re.fullmatch(r"v\d+\.\d+\.\d+", args.tag):
        parser.error(f"tag must look like v3.0.0, got {args.tag!r}")

    write_ascii(args.out / f"osui-{args.tag}-blocks.md", blocks_doc(args.clone, args.tag, args.date))
    write_ascii(args.out / f"osui-{args.tag}-theme.md", theme_doc(args.clone, args.tag, args.date))
    print(f"wrote osui-{args.tag}-blocks.md and osui-{args.tag}-theme.md to {args.out}")


if __name__ == "__main__":
    main()
