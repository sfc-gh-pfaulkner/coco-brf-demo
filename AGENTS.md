# Project rules

This project manages Snowflake objects through DCM and Git.

## Constraints

* Always work from a feature branch, never directly from main.
* The target environment must always be explicit (read from `.cortex/target-env`).
* If the branch suffix, target-env, or referenced database disagree, stop and warn.
* Do not guess the environment from context — always check.
* Do not switch Snowflake connections or modify connections.toml.
* Do not hardcode database names in definition files — DCM handles targeting.
* Prefer DCM plan before deploy.

## What goes where

| Question | Answer |
|----------|--------|
| How do I create a clone? | See `.cortex/skills/target-check/SKILL.md` |
| What SQL syntax do I use? | See `.cortex/skills/target-check/SKILL.md` |
| What's the setup checklist? | See `.cortex/skills/target-check/SKILL.md` |
| What clone types are allowed? | Controlled by `ADMIN_DB.TAGS.CLONE_TYPES` |
| How does CI deploy to TEST? | See `.github/workflows/deploy-test.yml` |
