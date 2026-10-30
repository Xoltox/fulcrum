#!/usr/bin/env node
// Trigger and routing evals for Fulcrum's skills. Claude Code only: it drives
// `claude -p` in a throwaway project holding a copy of skills/, with no MCP
// servers, so no case can reach a tenant. Each run costs API usage.
//
//   node evals/run-triggers.cjs [--models haiku,sonnet,opus] [--only <id>]
//                               [--budget 0.50] [--out <file>]
//
// A case passes when the first skill fired is in expectSkill (an empty list
// means no Fulcrum skill may fire) and the reply matches expectText, if set.
// Exit 1 on any failure.
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

function arg(name, fallback) {
  const i = process.argv.indexOf(`--${name}`);
  return i > 0 ? process.argv[i + 1] : fallback;
}

const REPO = path.resolve(__dirname, '..');
const CASES = JSON.parse(fs.readFileSync(path.join(__dirname, 'cases.json'), 'utf8'));
const MODELS = arg('models', 'sonnet').split(',');
const ONLY = arg('only', null);
const BUDGET = arg('budget', '0.50');
const OUT = arg('out', null);
const TIMEOUT_MS = 300000;

function scaffold(testCase) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fulcrum-eval-'));
  fs.cpSync(path.join(REPO, 'skills'), path.join(dir, '.claude', 'skills'), { recursive: true });
  for (const [rel, body] of Object.entries(testCase.files)) {
    const file = path.join(dir, rel);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, body);
  }
  return dir;
}

function firstSkill(lines) {
  for (const line of lines) {
    let event;
    try {
      event = JSON.parse(line);
    } catch {
      continue;
    }
    if (event.type !== 'assistant') continue;
    for (const block of event.message?.content ?? []) {
      if (block.type === 'tool_use' && block.name === 'Skill') return block.input?.skill ?? '';
    }
  }
  return null;
}

function finalText(lines) {
  for (const line of lines.slice().reverse()) {
    try {
      const event = JSON.parse(line);
      if (event.type === 'result') return { text: event.result ?? '', cost: event.total_cost_usd ?? 0 };
    } catch {
      continue;
    }
  }
  return { text: '', cost: 0 };
}

function run(testCase, model) {
  const dir = scaffold(testCase);
  const args = [
    '-p', testCase.prompt,
    '--model', model,
    '--tools', 'Skill,Read,Glob,Grep',
    '--allowedTools', 'Skill,Read,Glob,Grep',
    '--permission-mode', 'dontAsk',
    '--strict-mcp-config',
    '--setting-sources', 'project',
    '--no-session-persistence',
    '--max-budget-usd', BUDGET,
    '--output-format', 'stream-json',
    '--verbose',
  ];
  const child = spawnSync('claude', args, { cwd: dir, encoding: 'utf8', timeout: TIMEOUT_MS, maxBuffer: 1 << 28 });
  fs.rmSync(dir, { recursive: true, force: true });
  if (child.error) console.error(`${testCase.id}: ${child.error.message}`);
  const lines = (child.stdout ?? '').split('\n');
  const skill = firstSkill(lines);
  const { text, cost } = finalText(lines);
  const skillOk = testCase.expectSkill.length === 0
    ? !(skill ?? '').startsWith('fulcrum')
    : testCase.expectSkill.includes(skill);
  const textOk = !testCase.expectText || new RegExp(testCase.expectText, 'i').test(text);
  return { id: testCase.id, model, skill, skillOk, textOk, pass: skillOk && textOk, cost, text };
}

const results = [];
for (const model of MODELS) {
  for (const testCase of CASES) {
    if (ONLY && testCase.id !== ONLY) continue;
    const result = run(testCase, model);
    results.push(result);
    console.log(`${result.pass ? 'PASS' : 'FAIL'} ${model} ${result.id}: skill=${result.skill} text=${result.textOk} cost=${result.cost.toFixed(3)}`);
  }
}
if (OUT) fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
process.exit(results.length > 0 && results.every((r) => r.pass) ? 0 : 1);
