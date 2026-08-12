# Project rules

This project manages Snowflake objects through DCM and Git across two accounts (DEVACC and PRODACC).

## Accounts

| Account | Identifier | Purpose | Targets |
|---------|-----------|---------|---------|
| DEV | DEVACC | Development and testing | WIP_, TEST_ |
| PROD | PRODACC | UAT, pre-prod, and production | UAT_, PREPROD_, PROD |

## Promotion flow

```
feature/<id>-<topic>-WIP  -->  test/<id>-<topic>-TEST  -->  uat/<id>-<topic>-UAT  -->  preprod/<id>-<topic>-PREPROD  -->  main
       (DEVACC)                     (DEVACC)                  (PRODACC)                      (PRODACC)                 (PRODACC)
```

## Constraints

* Always work from a feature branch, never directly from main.
* The target environment must always be explicit (read from `.cortex/target-env`).
* If the branch suffix, target-env, or referenced database disagree, stop and warn.
* Do not guess the environment from context — always check.
* Do not switch Snowflake connections or modify connections.toml.
* Do not hardcode database names in definition files — DCM handles targeting via `{{db}}` and `{{wh}}`.
* Prefer DCM plan before deploy.
* WIP/TEST targets use CONNECTION_DEV; UAT/PREPROD targets use CONNECTION_PROD.

## What goes where

| Question | Answer |
|----------|--------|
| How do I create a clone? | See `.cortex/skills/target-check/SKILL.md` |
| What SQL syntax do I use? | See `.cortex/skills/target-check/SKILL.md` |
| What's the setup checklist? | See `.cortex/skills/target-check/SKILL.md` |
| What clone types are allowed? | Controlled by `ADMIN_DB.TAGS.CLONE_TYPES` |
| How does CI deploy to TEST? | See `.github/workflows/deploy-test.yml` |
| How does CI deploy to UAT? | See `.github/workflows/deploy-uat.yml` |
| How does CI deploy to PREPROD? | See `.github/workflows/deploy-preprod.yml` |
| How does CI deploy to PROD? | See `.github/workflows/deploy-prod.yml` |
| Full promotion workflow? | See `.cortex/skills/target-check/SKILL.md` |
