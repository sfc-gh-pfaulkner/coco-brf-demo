---
name: target-check
description: Enforce environment targeting, provide correct procedure calls, and manage session context for clone operations.
---

# When to use

Use this whenever the user asks to:
- Start a new piece of work (create issue, clone, branch)
- Edit Snowflake objects, run DCM, commit changes, or create a PR
- Create or drop a clone database
- Deploy DCM definitions
- Promote code between environments

# Accounts and roles

| Account | Identifier | Role | Warehouse | Stages |
|---------|-----------|------|-----------|--------|
| DEV | DEVACC | DEV_BRF_ETL | BRF_WH | WIP, TEST |
| PROD | PRODACC | PROD_BRF_ETL | BRF_WH | UAT, PREPROD, Production |

Warehouses are unprefixed (same name in both accounts) for dynamic table DDL portability.

# Connections

Each developer needs two entries in `~/.snowflake/connections.toml`:
- One for DEVACC (referenced as `CONNECTION_DEV` in workspace.env)
- One for PRODACC (referenced as `CONNECTION_PROD` in workspace.env)

IMPORTANT: Do NOT switch connections or modify connections.toml from CoCo.

# Promotion workflow

```
feature/<id>-<topic>-WIP  -->  test/<id>-<topic>-TEST  -->  uat/<id>-<topic>-UAT
                                                                    |
                                                                    v
                                                    preprod/<id>-<topic>-PREPROD  -->  main
```

| Stage | Account | Clone Prefix | Source DB | Branch Pattern |
|-------|---------|--------------|-----------|----------------|
| Development | DEVACC | WIP_ | DEV_BRF_CORE_DB | feature/<id>-<topic>-WIP |
| Testing | DEVACC | TEST_ | DEV_BRF_CORE_DB | test/<id>-<topic>-TEST |
| UAT | PRODACC | UAT_ | PROD_BRF_CORE_DB | uat/<id>-<topic>-UAT |
| Pre-prod | PRODACC | PREPROD_ | PROD_BRF_CORE_DB | preprod/<id>-<topic>-PREPROD |
| Production | PRODACC | — | PROD_BRF_CORE_DB | main |

# Session context

Set session context based on the current target:

```sql
-- DEVACC (WIP/TEST targets)
USE ROLE DEV_BRF_ETL;
USE WAREHOUSE BRF_WH;
USE DATABASE <WIP|TEST>_<ISSUE_ID>_BRF_CORE_DB;

-- PRODACC (UAT/PREPROD targets)
USE ROLE PROD_BRF_ETL;
USE WAREHOUSE BRF_WH;
USE DATABASE <UAT|PREPROD>_<ISSUE_ID>_BRF_CORE_DB;
```

IMPORTANT: The database is set via USE DATABASE, never in the connection definition.

# Clone procedures

ADMIN_DB is replicated in both accounts. The same procedure is available everywhere.

```sql
-- Create a clone (DEVACC)
USE ROLE DEV_BRF_ETL;
USE WAREHOUSE BRF_WH;
CALL ADMIN_DB.DEPLOY.DEPLOY_CLONE('<issue_id>', 'DEV', 'BRF', 'CORE', '<WIP|TEST>');

-- Create a clone (PRODACC)
USE ROLE PROD_BRF_ETL;
USE WAREHOUSE BRF_WH;
CALL ADMIN_DB.DEPLOY.DEPLOY_CLONE('<issue_id>', 'PROD', 'BRF', 'CORE', '<UAT|PREPROD>');

-- Drop a clone (DEVACC)
CALL ADMIN_DB.DEPLOY.DROP_CLONE('<issue_id>', 'DEV', 'BRF', 'CORE', '<WIP|TEST>');

-- Drop a clone (PRODACC)
CALL ADMIN_DB.DEPLOY.DROP_CLONE('<issue_id>', 'PROD', 'BRF', 'CORE', '<UAT|PREPROD>');
```

IMPORTANT:
- The procedure is `DEPLOY_CLONE`, NOT `DEPLOY_DEV_CLONE` or `DEPLOY_TEST_CLONE`.
- The ETL role has USAGE on these procedures — no need to switch to SYSADMIN.
- The second parameter is the environment ('DEV' or 'PROD') — determines the source database.
- The fifth parameter is the clone type: 'WIP', 'TEST', 'UAT', or 'PREPROD'.

# DCM deployment

Deploy to the appropriate target:

```
# Deploy to DEV account (WIP/TEST clones)
snow dcm deploy --target DEV --connection <CONNECTION_DEV value>

# Deploy to PROD account (UAT/PREPROD clones or production)
snow dcm deploy --target PROD --connection <CONNECTION_PROD value>
```

# New issue setup checklist

When starting a new piece of work, CoCo must perform ALL of the following steps:

1. Create a GitHub Issue (`gh issue create`)
2. Capture the issue number
3. Set session context: USE ROLE DEV_BRF_ETL, USE WAREHOUSE BRF_WH
4. Create the WIP clone: `CALL ADMIN_DB.DEPLOY.DEPLOY_CLONE('<id>', 'DEV', 'BRF', 'CORE', 'WIP')`
5. USE DATABASE on the new WIP clone
6. Create `.cortex/workspace.env` with ISSUE_ID, DOMAIN, DB_NAME, CONNECTION_DEV, CONNECTION_PROD
7. Create `.cortex/target-env` containing `WIP`
8. Create the feature branch: `feature/<issue>-<topic>-WIP`
9. Create a test script at `tests/Issue_<issue>/Issue_<issue>_tests.sql`

The `tests/` directory is gitignored — test scripts are local to the developer.

# Promotion checklist

## Feature -> Test (DEV account)
1. Create PR from `feature/<id>-<topic>-WIP` to `test/<id>-<topic>-TEST`
2. CI creates TEST clone and deploys DCM
3. Update `.cortex/target-env` to `TEST`
4. Switch to `test/<id>-<topic>-TEST` branch locally

## Test -> UAT (DEV -> PROD account)
1. Create PR from `test/<id>-<topic>-TEST` to `uat/<id>-<topic>-UAT`
2. CI creates UAT clone in PRODACC and deploys DCM
3. Update `.cortex/target-env` to `UAT`
4. Switch connection to CONNECTION_PROD
5. Switch to `uat/<id>-<topic>-UAT` branch locally

## UAT -> Pre-prod (PROD account)
1. Create PR from `uat/<id>-<topic>-UAT` to `preprod/<id>-<topic>-PREPROD`
2. CI creates PREPROD clone in PRODACC and deploys DCM
3. Update `.cortex/target-env` to `PREPROD`
4. Switch to `preprod/<id>-<topic>-PREPROD` branch locally

## Pre-prod -> Production (PROD account)
1. Create PR from `preprod/<id>-<topic>-PREPROD` to `main`
2. CI deploys DCM directly to PROD_BRF_CORE_DB
3. CI drops UAT and PREPROD clones (cleanup)
4. Reset `.cortex/target-env` to `WIP` for next piece of work

# Environment validation

* Read `.cortex/workspace.env` to get ISSUE_ID, DOMAIN, DB_NAME, CONNECTION_DEV, CONNECTION_PROD.
* The target environment comes from `.cortex/target-env`.
* Derive the expected database: `<TARGET>_<ISSUE_ID>_BRF_CORE_DB`
* Derive the expected connection: WIP/TEST -> CONNECTION_DEV, UAT/PREPROD -> CONNECTION_PROD
* Confirm the current branch suffix matches the target.
* Confirm any database references match the expected database.
* Confirm the connection matches the expected account.
* If there is any mismatch, stop and explain the mismatch.
