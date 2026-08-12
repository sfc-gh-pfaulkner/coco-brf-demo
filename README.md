# coco-brf-demo

BRF (Business & Retail Finance) domain DCM project for managing loan transaction ingestion pipelines.

## Structure

```
dcm/
├── manifest.yml                     DCM v2 manifest with Jinja templating
└── sources/definitions/
    └── raw/                         Raw ingestion layer
        ├── loan_transactions_ff.sql File format for CSV ingestion
        ├── loan_transactions_raw.sql Target table
        └── ingest_loan_transactions_task.sql  30-min scheduled COPY INTO
```

## Getting Started

1. Copy `.cortex/workspace.env.example` to `.cortex/workspace.env`
2. Set your `ISSUE_ID`
3. Create your WIP clone: `CALL ADMIN_DB.DEPLOY.DEPLOY_CLONE('<issue_id>', 'DEV', 'BRF', 'CORE', 'WIP')`
4. Deploy: `cd dcm && snow dcm deploy --connection FCRICKDEMO_DEV`
