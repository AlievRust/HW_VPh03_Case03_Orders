# AGENTS.md — OpenSpec + Codex Workflow

This file defines the always-on rules for AI coding agents in this repository.

Primary environment:
- VS Code
- Codex
- OpenSpec workflow
- Python-first projects, unless the project spec says otherwise

All answers, comments, docs, and user-facing summaries must be in Russian.

---

## 1. Core rule: spec-first

OpenSpec is the source of truth, not agent assumptions.

If the answer should be in the spec but is missing:
1. stop;
2. state what is missing;
3. ask the user or propose a spec update.

Do not silently invent:
- architecture;
- behavior;
- APIs;
- data models;
- configs;
- deployment rules;
- user flows.

Spec drift is a serious error.

---

## 2. Instruction priority

Use this priority order:

1. Current explicit user instruction.
2. This `AGENTS.md`.
3. Active OpenSpec change:
   - `openspec/changes/<change-id>/proposal.md`
   - `openspec/changes/<change-id>/design.md`
   - `openspec/changes/<change-id>/tasks.md`
4. Project-wide spec:
   - `openspec/project.md`
5. Repository docs:
   - `README.md`
   - `docs/technical_overview.md`
   - `docs/changelog.md`
   - `docs/roadmap.md`
6. Existing code patterns.
7. General best practices.

If sources conflict, do not resolve silently. Explain the conflict and ask the user, unless a higher-priority source clearly decides it.

---

## 3. Startup reading order

Before editing, inspect the repository and read existing docs in this order if they exist:

1. `README.md`
2. `docs/technical_overview.md`
3. `docs/changelog.md`
4. `docs/roadmap.md`, if planning is affected
5. `openspec/project.md`
6. Active change files:
   - `proposal.md`
   - `design.md`
   - `tasks.md`
7. Relevant source files and tests
8. `git status`, if git is available

For complex multi-step work, also read relevant files from:

- `docs/agent_guides/openspec_workflow.md`
- `docs/agent_guides/implementation_protocol.md`
- `docs/agent_guides/review_and_verification.md`
- `docs/agent_guides/debug_playbook.md`
- `docs/agent_guides/subagents.md`

Do not edit files before understanding the active change and current repository state.

---

## 4. Work modes

### Idea / proposal mode

Use when the user describes an idea without a chosen technical solution.

Do not write implementation code.

Instead:
1. restate the goal;
2. propose 2–3 implementation options;
3. list dependencies, pros, cons, risks, and complexity;
4. recommend one option;
5. ask only questions that block correct specification.

### Spec writing mode

Use when creating or updating OpenSpec.

Create or update:

- `openspec/changes/<number-change-id>/proposal.md`
- `openspec/changes/<number-change-id>/design.md`
- `openspec/changes/<number-change-id>/tasks.md`

Change id format:

- `NNNN-short-kebab-slug`

Example:

- `0001-snake-mvp`

The spec should define:
- goal;
- scope;
- out of scope;
- user-visible behavior;
- technical design;
- affected files/modules;
- risks;
- verification plan;
- task checklist.

### Implementation mode

Use only when coding conditions are met.

Implementation means changing:
- source code;
- tests;
- database schema;
- APIs;
- runtime behavior;
- config behavior;
- deployment behavior.

### Debug / investigation mode

Use when the user provides logs, errors, failing tests, screenshots, or broken behavior.

Process:
1. identify the failure path;
2. inspect relevant code/config;
3. propose the smallest safe fix;
4. update OpenSpec if behavior changes;
5. verify with the narrowest relevant command.

Do not rewrite large parts of the system to fix a narrow bug.

---

## 5. Conditions to start coding

Do not write implementation code until all conditions are met:

- [ ] User explicitly approved implementation.
- [ ] Active OpenSpec change exists, unless the task is tiny docs-only or investigation-only.
- [ ] `tasks.md` exists and contains a checklist.
- [ ] `design.md` answers the technical questions.
- [ ] Ambiguities are resolved.
- [ ] Success criteria are clear.
- [ ] Verification method is clear.

If these conditions are not met, work on missing spec/design/tasks first.

---

## 6. Engineering guardrails

Before coding, state briefly:
- concrete goal;
- expected behavior change;
- what must remain unchanged;
- files likely to be touched;
- success criteria;
- verification commands.

Prefer the simplest solution that satisfies the spec.

Do not add:
- unrequested features;
- speculative abstractions;
- unnecessary dependencies;
- broad rewrites;
- configurability not requested by the spec.

Touch only files and lines required by the current task.

Do not:
- refactor unrelated code;
- reformat unrelated files;
- rename unrelated symbols;
- move files without a spec reason;
- delete historical artifacts unless explicitly requested.

Every changed line must be traceable to:
- current `tasks.md`;
- explicit spec requirement;
- test/verification need;
- cleanup directly caused by the current change.

If unrelated problems are found, mention them instead of fixing silently.

---

## 7. When to stop and ask

Stop and ask if:

- `design.md` lacks an answer to a technical question.
- The task requires choosing between valid architectural options.
- The change affects behavior not described in the spec.
- Scope is unclear.
- The request conflicts with OpenSpec.
- A dependency, framework, DB, API style, or deployment pattern must be selected.
- The task requires deleting or rewriting significant existing work.
- The operation may be destructive or irreversible.

Do not ask unnecessary questions when the answer is already in the repo or the issue is local, obvious, and reversible.

---

## 8. Task execution protocol

Follow `tasks.md` top-to-bottom.

For each task:
1. mark it `[~]` in progress;
2. define success criteria;
3. make the smallest necessary change;
4. add/update tests for behavior changes;
5. run relevant checks;
6. review the diff;
7. remove unrelated changes;
8. update docs/specs if needed;
9. mark it `[x]` done.

Keep diffs small.

One task = one logical change.

Do not commit unless the user explicitly asks. Suggest a commit message instead.

---

## 9. Subagents policy

Default to a single agent.

Use subagents only for bounded parallel tasks:
- repo exploration;
- independent test runs;
- log analysis;
- summarizing separate modules;
- comparing approaches.

Avoid subagents for:
- small fixes;
- overlapping edits;
- shared-file refactors;
- tasks requiring one consistent design decision.

No more than 2 subagents at a time unless the user asks otherwise.

Return concise summaries, not raw logs.

---

## 10. Documentation rules

After implementation, update docs if behavior changed.

Check:
- `README.md` — setup, usage, commands, behavior, navigation;
- `docs/technical_overview.md` — architecture/modules/data flow;
- `docs/changelog.md` — observable behavior changes;
- `docs/roadmap.md` — planning changes;
- `openspec/project.md` — project-wide rules/constraints;
- active OpenSpec files — if implementation differs from design/tasks.

Docs must not describe features that do not exist.

---

## 11. Code requirements

Default rules:

- readable, structured code;
- follow existing project style;
- Python code should be PEP8-compliant;
- use type hints where useful;
- avoid hidden global state;
- avoid broad `except Exception` unless justified;
- avoid magic constants;
- avoid duplicated business logic;
- keep I/O, business logic, and API/UI layers separated when practical;
- docstrings and inline comments must be in Russian;
- comments should explain why, not restate obvious code.

For Python projects, prefer:
- `python -m pytest`
- `python -m compileall .`
- `python -m ruff check .`

Use project-specific commands if defined.

---

## 12. Dependencies, DB, config, secrets

Do not add dependencies casually.

Before adding a dependency:
1. check whether existing tools are enough;
2. explain why the dependency is needed;
3. update dependency files;
4. update setup docs.

For database changes:
- do not change schema silently;
- add migrations if the project uses migrations;
- preserve existing data unless destructive change is explicitly approved;
- document manual SQL if no migration tool exists.

For config/secrets:
- never hardcode secrets;
- never print secrets in logs/responses;
- use env vars or existing config system;
- update `.env.example` if config changes;
- mask secrets seen in logs.

---

## 13. Verification

Never claim tests, linters, builds, migrations, or manual checks passed unless actually run.

After implementation:
1. run syntax checks for changed files;
2. run relevant tests;
3. run linters/format checks if configured;
4. review final diff.

Final diff must have:
- no unrelated refactors;
- no unrelated formatting changes;
- no speculative abstractions;
- no accidental dependency changes;
- no deleted historical artifacts;
- no generated junk files;
- no secrets;
- no behavior change missing from OpenSpec.

If verification could not be run, state:
- what was not run;
- why;
- exact command the user should run.

---

## 14. Git workflow

Before editing:
- check `git status`, if available;
- do not overwrite user changes.

During work:
- keep changes commit-sized;
- avoid noisy formatting-only diffs.

After work:
- summarize changed files;
- suggest a concise commit message;
- do not commit unless asked.

Recommended branch:
- `chg-<number>-<short-slug>`

Recommended commit:
- `CHG-<number>: short summary`

---

## 15. Response format

Default structure:

План
- ...

Изменения
- ...

Проверка
- ...

Команды
- ...

For small answers, be shorter.

For implementation reports, include:
- what changed;
- which files changed;
- what checks were run;
- what passed/failed;
- what remains;
- manual verification commands;
- suggested commit message.

Do not paste huge logs unless asked. Summarize and include only relevant fragments.

---

## 16. Definition of done

A task is done only when:

- requested behavior is implemented;
- implementation matches OpenSpec;
- related task checklist items are marked `[x]`;
- tests/checks were run or limitations were stated;
- docs were updated or explicitly deemed unnecessary;
- final diff contains no unrelated changes;
- user receives verification commands;
- remaining risks or limitations are disclosed.
