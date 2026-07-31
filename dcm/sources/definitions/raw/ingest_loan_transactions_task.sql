DEFINE TASK {{db}}.RAW.INGEST_LOAN_TRANSACTIONS
    WAREHOUSE = BRF_INGEST_WH
    SCHEDULE = '30 MINUTE'
    STARTED
AS
    COPY INTO {{db}}.RAW.LOAN_TRANSACTIONS_RAW (
        TRANSACTION_ID, LOAN_ID, APPLICANT_ID, EVENT_TYPE,
        EVENT_TIMESTAMP, PRODUCT_TYPE, CHANNEL, AMOUNT,
        CURRENCY, OFFICER_ID, BRANCH_CODE, STATUS, NOTES,
        _LOADED_AT, _SOURCE_FILE
    )
    FROM (
        select
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
            current_timestamp(),
            METADATA$FILENAME
        from @{{source_stage_db}}.RAW.LOAN_TRANSACTIONS_STG
    )
    FILE_FORMAT = (FORMAT_NAME = '{{db}}.RAW.LOAN_TRANSACTIONS_FF')
    PATTERN = '.*\.csv\.gz';
