# Plan: Standalone RBAC Framework Project

## Context

The RBAC framework currently lives in `/Users/pfaulkner/Documents/Francis Crick Institute/RBAC/Deploy/`. It contains:
- **Scripts 00-19**: Infrastructure (session policy, ADMIN_DB, schemas, roles, tags, tables, procedures including DEPLOY_CLONE)
- **Script 20**: Main deployment (calls DEPLOY_ENVIRONMENT/DOMAIN/DATABASE/SCHEMA/WAREHOUSE to set up actual environments) — **excluded per your request**
- **Scripts 21-23**: Demo data (HR, FANDI, GENERAL) — **excluded** (demo-specific)
- **Script 24**: DROP_CLONE procedure
- **Script 26**: FIND_CLONE_BLOCKERS diagnostic procedure
- **functional_roles/**: DCM sub-project managing grants for ANALYST/MANAGER/DATASTEWARD/POWERBI/DEVELOPER roles
- **create_functional_roles_temp.sql**: Temp script simulating SCIM provisioning — **excluded** (demo-specific)
- **go.ps1**: PowerShell runner — will be recreated for the new structure

## Proposed Project Structure

```
snowflake-rbac-framework/
├── README.md                          # Setup guide (adapted from existing)
├── .gitignore
├── scripts/
│   ├── 00_session_policy.sql
│   ├── 01_deployment_admin.sql
│   ├── 02_admin_db.sql
│   ├── 03_admin_db_deploy_schema.sql
│   ├── 04_admin_db_tags_schema.sql
│   ├── 05_admin_db_database_roles.sql
│   ├── 06_admin_db_deploy_schema_roles.sql
│   ├── 07_admin_db_tags_schema_roles.sql
│   ├── 08_admin_wh.sql
│   ├── 09_admin_db_environments_table.sql
│   ├── 10_admin_db_domains_table.sql
│   ├── 11_admin_db_environment_tag.sql
│   ├── 12_admin_db_domain_tag.sql
│   ├── 13_admin_db_deploy_environment_proc.sql
│   ├── 14_admin_db_deploy_domain_proc.sql
│   ├── 15_admin_db_deploy_database_proc.sql
│   ├── 16_admin_db_deploy_schema_proc.sql
│   ├── 17_admin_db_deploy_warehouse_proc.sql
│   ├── 18_admin_db_deploy_dp_role_proc.sql
│   ├── 19_admin_db_deploy_clone.sql
│   ├── 24_admin_db_drop_clone.sql
│   └── 26_admin_db_find_clone_blockers.sql
├── functional_roles/                  # DCM project for functional role grants
│   ├── manifest.yml
│   ├── pre_deploy.sql
│   ├── post_deployment_grants.sql
│   └── sources/definitions/access.sql
├── deploy.ps1                         # PowerShell runner (scripts/ in order)
└── deploy.sh                          # Bash runner (for CI/CD / Mac / Linux)
```

## Key Decisions

1. **Script 20 excluded** — it's the actual deployment call (DEPLOY_ENVIRONMENT, DEPLOY_DOMAIN, etc.) which is specific to each customer's environments and domains. Users write their own after running the framework scripts.
2. **Demo scripts (21-23) excluded** — those are sample data, not framework infrastructure.
3. **create_functional_roles_temp.sql excluded** — it simulates SCIM and is temporary.
4. **functional_roles/ included** — the DCM project for managing functional role grants is reusable framework code. The `manifest.yml` will need the account identifier and domain list updated per deployment.
5. **No hardcoded account identifiers** — the manifest and README will use placeholders.

## Implementation Steps

### 1. Create the project directory and initialize git

Create `/Users/pfaulkner/Documents/GitHub/snowflake-rbac-framework/`, `git init`, set up `.gitignore`.

### 2. Copy framework scripts (00-19, 24, 26)

Copy all SQL scripts verbatim from the Deploy folder. These are already account-agnostic (they use roles and dynamic naming, not hardcoded identifiers).

### 3. Copy functional_roles/ DCM sub-project

Copy the manifest.yml, pre_deploy.sql, post_deployment_grants.sql, and sources/ directory. Update manifest.yml to remove the hardcoded account identifier and replace with a placeholder.

### 4. Create deploy scripts (PowerShell + Bash)

Adapted from `go.ps1`. Will run scripts 00-19, 24, 26 in order using `snow sql -f`.

### 5. Create README.md

Adapt from the existing README with:
- Prerequisites (SnowCLI, key-pair setup)
- Connection setup
- Script reference table (without demo scripts)
- Functional roles deployment instructions
- How to write your own "script 20" (deploying environments, domains, databases)

## Verification

- All scripts should be syntactically valid (already tested in your existing deployment)
- `functional_roles/manifest.yml` should have placeholder account identifier
- deploy.sh should reference all scripts in correct order
- README should document the full workflow

## Critical Files

- `scripts/19_admin_db_deploy_clone.sql` — DEPLOY_CLONE procedure (core of the multi-environment workflow)
- `scripts/24_admin_db_drop_clone.sql` — DROP_CLONE procedure (cleanup)
- `functional_roles/sources/definitions/access.sql` — Jinja-templated DCM grants
- `functional_roles/manifest.yml` — DCM config needing placeholder account ID
- `README.md` — Installation and usage guide
