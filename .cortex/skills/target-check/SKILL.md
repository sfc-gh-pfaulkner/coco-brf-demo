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

# Connection and session context

There is ONE Snowflake connection used for all work. The connection name is in `.cortex/workspace.env` (field: CONNECTION). Do NOT switch connections or modify connections.toml.

After connecting, set the session context based on workspace.env:

```sql
USE ROLE DEV_BRF_ETL;
USE WAREHOUSE BRF_DEV_WH;
USE DATABASE <CLONE_TYPE>_<ISSUE_ID>_BRF_CORE_DB;
```

IMPORTANT: The database is set via USE DATABASE, never in the connection definition.
IMPORTANT: The ETL role can do everything — clone operations, development, and DCM deploy. No need to switch roles.

# Clone procedures

```sql
-- Create a clone
USE ROLE DEV_BRF_ETL;
USE WAREHOUSE BRF_DEV_WH;
CALL ADMIN_DB.DEPLOY.DEPLOY_CLONE('<issue_id>', 'DEV', 'BRF', 'CORE', '<WIP|TEST|UAT|PREPROD>');

-- Drop a clone
CALL ADMIN_DB.DEPLOY.DROP_CLONE('<issue_id>', 'DEV', 'BRF', 'CORE', '<WIP|TEST|UAT|PREPROD>');
```

IMPORTANT:
- The procedure is `DEPLOY_CLONE`, NOT `DEPLOY_DEV_CLONE` or `DEPLOY_TEST_CLONE`.
- The ETL role has USAGE on these procedures — no need to switch to SYSADMIN.
- The fifth parameter is the clone type: 'WIP', 'TEST', 'UAT', or 'PREPROD'.
- WIP clones grant full RWC (read/write/create) to the ETL role.

# DCM deployment

The DCM project is deployed to the `DCM` schema within the clone database:

```
snow dcm deploy --connection FCRICKDEMO_DEV
```

# New issue setup checklist

When starting a new piece of work, CoCo must perform ALL of the following steps:

1. Create a GitHub Issue (`gh issue create`)
2. Capture the issue number
3. Set session context: USE ROLE DEV_BRF_ETL, USE WAREHOUSE BRF_DEV_WH
4. Create the WIP clone (CALL DEPLOY_CLONE)
5. USE DATABASE on the new WIP clone
6. Create `.cortex/workspace.env` with ISSUE_ID, DOMAIN, DB_NAME, CONNECTION
7. Create `.cortex/target-env` containing `WIP`
8. Create the feature branch: `feature/<issue>-<topic>-WIP`
9. Create a test script at `tests/Issue_<issue>/Issue_<issue>_tests.sql` with validation queries for the new/changed objects

The `tests/` directory is gitignored — test scripts are local to the developer.

# Environment validation

* Read `.cortex/workspace.env` to get the ISSUE_ID, DOMAIN, DB_NAME, and CONNECTION.
* The target environment comes from `.cortex/target-env`.
* Derive the expected database: `<TARGET>_<ISSUE_ID>_BRF_CORE_DB`
* Confirm the current branch suffix matches the target.
* Confirm any database references match the expected database.
* If there is any mismatch, stop and explain the mismatch.
