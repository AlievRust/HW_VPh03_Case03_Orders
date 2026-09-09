# OpenSpec Workflow Guide

Use this guide for new features, behavior changes, architecture changes, or unclear tasks.

## Purpose

OpenSpec prevents spec drift. The agent must not treat code as the only source of truth when user-visible behavior, architecture, data, APIs, deployment, or configuration changes.

## Change folder

Use:

- `openspec/changes/<number-change-id>/proposal.md`
- `openspec/changes/<number-change-id>/design.md`
- `openspec/changes/<number-change-id>/tasks.md`

Change id format:

- `NNNN-short-kebab-slug`

Example:

- `0004-add-admin-auth`

## proposal.md should contain

- Problem
- Goal
- Scope
- Out of scope
- User-visible behavior
- Risks
- Acceptance criteria

## design.md should contain

- Current behavior
- Target behavior
- Affected modules/files
- Data model changes
- API changes
- Config changes
- DB/migration notes
- Error handling
- Security implications
- Verification plan

## tasks.md should contain

A concrete checklist.

Example:

- [ ] Inspect existing auth flow
- [ ] Add password hashing utility
- [ ] Add login endpoint
- [ ] Add tests
- [ ] Update README
- [ ] Update changelog

## When OpenSpec is required

Create or update OpenSpec for:
- new feature;
- changed user flow;
- API contract change;
- DB schema change;
- config behavior change;
- logging format change;
- validation change;
- deployment behavior change;
- data import/export change;
- security/auth change.

## When OpenSpec may be skipped

OpenSpec may be skipped only for:
- tiny typo fixes;
- docs-only edits that do not describe new behavior;
- local investigation without code changes;
- internal refactor with no behavior/API/config/data change.

When in doubt, update OpenSpec.
