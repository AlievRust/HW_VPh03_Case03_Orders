# Review and Verification Guide

Use this guide before reporting completion.

## No fake verification

Never claim a check passed unless it was actually run.

If a check was not run, state:
- what was not run;
- why;
- exact command the user should run.

## Recommended Python checks

Use project-specific commands if defined.

Common defaults:
- `python -m compileall .`
- `python -m pytest`
- `python -m ruff check .`

For Docker projects:
- `docker compose config`
- `docker compose up -d --build`
- `docker compose logs --tail=100 <service>`

For DB changes:
- migration command;
- schema check;
- rollback note if relevant.

## Final diff review

Before final response, check that the diff has:

- no unrelated refactors;
- no unrelated formatting changes;
- no speculative abstractions;
- no accidental dependency updates;
- no deleted historical artifacts;
- no generated junk files;
- no secrets;
- no behavior changes missing from OpenSpec;
- no docs describing features that do not exist.

## Final report format

Include:

- changed files;
- what changed;
- what checks were run;
- what passed;
- what failed or was not run;
- manual verification commands;
- remaining risks;
- suggested commit message.

## Suggested commit message

Format:

- `CHG-<number>: short summary`

Example:

- `CHG-0004: add admin login endpoint`
