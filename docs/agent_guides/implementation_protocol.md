# Implementation Protocol Guide

Use this guide for multi-step implementation tasks.

## Before editing

Confirm:
- current task from `tasks.md`;
- expected behavior;
- what must remain unchanged;
- likely files to touch;
- success criteria;
- verification commands.

Check:
- `git status`;
- active OpenSpec change;
- relevant source files;
- relevant tests;
- existing project style.

## During editing

Work top-to-bottom through `tasks.md`.

For each task:
1. mark `[~]`;
2. make the smallest necessary change;
3. add or update tests;
4. run narrow verification;
5. review diff;
6. update docs/specs;
7. mark `[x]`.

## Change discipline

One task should produce one logical change.

Avoid:
- unrelated refactors;
- broad rewrites;
- formatting-only noise;
- speculative abstractions;
- casual dependency updates;
- changing public behavior without OpenSpec.

## Simplicity rule

Prefer:
- small functions;
- explicit names;
- existing patterns;
- boring reliable code.

Avoid:
- new framework layers for one feature;
- factories/builders unless needed;
- premature plugins;
- unnecessary config toggles;
- “future-proofing” without spec.

## If design mismatch appears

If implementation reveals that `design.md` is wrong or incomplete:
1. stop coding;
2. update `design.md`;
3. update `tasks.md` if needed;
4. continue only after scope is clear.
