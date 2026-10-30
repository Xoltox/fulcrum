# Third-party notice

Two sources, two licences.

## outsystems-design-to-app (MIT)

The files below are derived from the `outsystems-design-to-app` skill (v1.4.1) of the OutSystems MCP skills repository (outsystems-mcp-skills), which is licensed under the MIT License. They are condensed, rephrased and modified for Fulcrum: procedure was dropped, Fulcrum conflict resolutions were applied, and tenant-specific facts were replaced by pointers to tenant-profile.md. All borrowed facts are tagged [UNVERIFIED] until observed on a tenant.

Derived files:
- `block-map.md`: condensed from the official SKILL.md block mapping pass, `references/outsystems-ui/ui-reference.md`, `layouts.md`, and `references/gotchas/*`.
- `screen-archetypes.md`: condensed from the official `references/screen-guides/*`.
- `capture-recipes.md`: condensed from the official `references/design-capture.md` (the two anatomy recipes, KPI-source decision, sizing completeness) and the SKILL.md Figma extraction notes.
- `design-spec-format.md`: condensed from the official `references/design-capture.md` (anatomy format and its gate) and the SKILL.md block mapping, anatomy verification and acceptance-item steps; Fulcrum replaced the single JSON spec with per-screen Markdown files.

The official gotchas themselves cite the claude-oml-tool corpus as their origin.

### MIT License text

MIT License

Copyright (c) 2026 OutSystems

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## OutSystems UI (BSD 3-Clause)

The files below contain condensed extracts of OutSystems UI (repository OutSystems/outsystems-ui), tag `v3.0.0`, taken 2026-10-30, reduced to names, defaults and values and modified for Fulcrum. They are not generated, reviewed or endorsed by OutSystems, and the OutSystems name is used here only to identify the source.

Derived files:
- `osui-v3.0.0-blocks.md`: condensed from `docs-ai/osui.blocks.json`.
- `osui-v3.0.0-theme.md`: condensed from `docs-ai/llms-tokens.txt`, `docs-ai/llms-utilities.txt`, `docs-ai/osui.icons.json`, `src/scss/01-foundations/_root.scss` and `stories/_helpers/token-data/*.ts`.
- `block-map.md`: the library keys and the "More library blocks" table.

Refresh path, maintainer only: `scripts/gen-osui-ref.py` at the repository root regenerates the two `osui-<tag>-*.md` files from a local clone of the tag, read as data. Nothing runs at install.

### BSD 3-Clause License text

BSD 3-Clause License

Copyright (c) 2023, OutSystems

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
