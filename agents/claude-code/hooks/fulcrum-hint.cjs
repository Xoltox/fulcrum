#!/usr/bin/env node
// fulcrum-hint.cjs - opt-in Claude Code hook. Prints a one-line hint to load the
// fulcrum skill, or nothing. Wire it to SessionStart and UserPromptSubmit;
// INSTALL.md, heading "Automatic triggers", has the settings entries.
//
// SessionStart      hints when `.fulcrum/` exists in cwd or a parent.
// UserPromptSubmit  hints when the prompt names outsystems or odc, or names
//                   mentor while `.fulcrum/` exists in cwd or a parent.
// Anything else     prints nothing, so no context is added.
//
// Hint only: always exits 0, so it can never block a session or a prompt. Any
// error, including bad input, is silent. No network, no writes, no state, reads
// nothing but stdin and the existence of `.fulcrum/`.
//
// Node, not Python: `node` is one command name on Windows, macOS and Linux, while
// Python is `python3` on some and `python` on others and a Windows `python3` can be
// a store stub. `.cjs` keeps it CommonJS under a `"type": "module"` package.json.

'use strict';

const fs = require('fs');
const path = require('path');

const PROJECT_WORDS = /\b(outsystems|odc)\b/i;
const MENTOR_WORD = /\bmentor\b/i;
const MAX_LEVELS = 64;

const STATE_HINT = 'Fulcrum: a .fulcrum/ directory is present. Load the fulcrum skill before any OutSystems work; otherwise ignore this hint.';
const PROMPT_HINT = 'Fulcrum: if this is OutSystems, ODC or Mentor work, load the fulcrum skill first; otherwise ignore this hint.';

function hasFulcrumDir(start) {
  let dir = path.resolve(start);
  for (let i = 0; i < MAX_LEVELS; i++) {
    try {
      if (fs.statSync(path.join(dir, '.fulcrum')).isDirectory()) return true;
    } catch (e) {
      // Absent or unreadable: keep walking up.
    }
    const parent = path.dirname(dir);
    if (parent === dir) return false;
    dir = parent;
  }
  return false;
}

function hintFor(input) {
  const cwd = typeof input.cwd === 'string' && input.cwd ? input.cwd : process.cwd();
  if (input.hook_event_name === 'SessionStart') {
    return hasFulcrumDir(cwd) ? STATE_HINT : '';
  }
  if (input.hook_event_name === 'UserPromptSubmit') {
    const prompt = typeof input.prompt === 'string' ? input.prompt : '';
    if (PROJECT_WORDS.test(prompt)) return PROMPT_HINT;
    if (MENTOR_WORD.test(prompt) && hasFulcrumDir(cwd)) return PROMPT_HINT;
  }
  return '';
}

try {
  const hint = hintFor(JSON.parse(fs.readFileSync(0, 'utf8')));
  if (hint) process.stdout.write(hint + '\n');
} catch (e) {
  // A hint is never worth a failure.
}
