# Debug Playbook

Use this guide for logs, errors, failing tests, broken behavior, or screenshots.

## Debug process

1. Identify the symptom.
2. Locate the failure path.
3. Read relevant logs/code/config.
4. Form one or more hypotheses.
5. Prefer the smallest safe fix.
6. Verify with the narrowest command.
7. Update OpenSpec if behavior changes.

## Do not

- rewrite large modules for a narrow bug;
- change architecture during debugging;
- add broad exception handling to hide errors;
- remove validation without understanding why it fails;
- silence logs instead of fixing the cause;
- claim the issue is fixed without verification.

## Good debugging response

Include:
- likely cause;
- evidence;
- files inspected;
- proposed fix;
- verification command;
- risk/limitation.

## If logs contain secrets

Mask:
- tokens;
- passwords;
- API keys;
- cookies;
- private URLs with credentials;
- connection strings.

## If root cause is uncertain

Say so.

Use wording like:
- “Most likely cause...”
- “Evidence points to...”
- “I would verify by running...”

Do not present guesses as facts.
