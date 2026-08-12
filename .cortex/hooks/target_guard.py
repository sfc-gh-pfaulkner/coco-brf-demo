import json
import pathlib
import subprocess
import sys

TARGET_FILE = pathlib.Path('.cortex/target-env')
WORKSPACE_FILE = pathlib.Path('.cortex/workspace.env')

VALID_TARGETS = ('WIP', 'TEST', 'UAT', 'PREPROD')

# Maps each target to the account it operates in and the workspace.env connection key
TARGET_ACCOUNT_MAP = {
    'WIP': 'CONNECTION_DEV',
    'TEST': 'CONNECTION_DEV',
    'UAT': 'CONNECTION_PROD',
    'PREPROD': 'CONNECTION_PROD',
}


def emit_block(message: str):
    print(json.dumps({
        'decision': 'block',
        'reason': message,
    }))
    sys.exit(2)


def read_workspace() -> dict:
    if not WORKSPACE_FILE.exists():
        emit_block('Missing .cortex/workspace.env. Copy from workspace.env.example and set your ISSUE_ID.')
    config = {}
    for line in WORKSPACE_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    return config


def current_branch() -> str:
    return subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
        text=True,
    ).strip()


def derive_database(config: dict, target: str) -> str:
    issue_id = config.get('ISSUE_ID', '')
    domain = config.get('DOMAIN', '')
    db_name = config.get('DB_NAME', '')
    if not issue_id or not domain or not db_name:
        emit_block('workspace.env must define ISSUE_ID, DOMAIN, and DB_NAME.')
    return f'{target}_{issue_id}_{domain}_{db_name}_DB'


def expected_connection(config: dict, target: str) -> str:
    conn_key = TARGET_ACCOUNT_MAP[target]
    conn = config.get(conn_key, '')
    if not conn:
        emit_block(f'workspace.env must define {conn_key} for target {target}.')
    return conn


# --- Main ---

if not TARGET_FILE.exists():
    emit_block('Missing .cortex/target-env. Set it to WIP, TEST, UAT, or PREPROD.')

target = TARGET_FILE.read_text().strip().upper()
if target not in VALID_TARGETS:
    emit_block(f'Target environment must be one of: {", ".join(VALID_TARGETS)}.')

config = read_workspace()
expected_db = derive_database(config, target)
expected_conn = expected_connection(config, target)

# Build list of wrong databases (all other clone types)
wrong_dbs = [derive_database(config, t) for t in VALID_TARGETS if t != target]

# Also block references to the base DEV/PROD databases when working in a clone
wrong_dbs.append(f'DEV_{config.get("DOMAIN", "")}_{config.get("DB_NAME", "")}_DB')
wrong_dbs.append(f'PROD_{config.get("DOMAIN", "")}_{config.get("DB_NAME", "")}_DB')

branch = current_branch()
if not branch.endswith(target):
    emit_block(f'Branch "{branch}" does not end with target "{target}".')

payload = json.load(sys.stdin)
tool_name = payload.get('tool_name', '')
tool_input = payload.get('tool_input', {})
serialized = json.dumps(tool_input)

# Block references to wrong databases
for wrong_db in wrong_dbs:
    if wrong_db in serialized:
        emit_block(
            f'Target is {target} ({expected_db}), but the pending action references {wrong_db}.'
        )

# Block Snowflake tool calls using the wrong connection
if tool_name.startswith('snowflake_'):
    conn_in_input = tool_input.get('connection', '')
    if conn_in_input and conn_in_input != expected_conn:
        emit_block(
            f'Target {target} requires connection "{expected_conn}", '
            f'but the action uses "{conn_in_input}".'
        )

if tool_name.startswith('mcp__github__'):
    if not branch.endswith(target):
        emit_block(f'GitHub action blocked: branch "{branch}" does not match target "{target}".')
