import json
import pathlib
import subprocess
import sys

TARGET_FILE = pathlib.Path('.cortex/target-env')
WORKSPACE_FILE = pathlib.Path('.cortex/workspace.env')

VALID_TARGETS = ('WIP', 'TEST', 'UAT', 'PREPROD')


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


# --- Main ---

if not TARGET_FILE.exists():
    emit_block('Missing .cortex/target-env. Set it to WIP, TEST, UAT, or PREPROD.')

target = TARGET_FILE.read_text().strip().upper()
if target not in VALID_TARGETS:
    emit_block(f'Target environment must be one of: {", ".join(VALID_TARGETS)}.')

config = read_workspace()
expected_db = derive_database(config, target)

# Build list of wrong databases (all other clone types)
wrong_dbs = [derive_database(config, t) for t in VALID_TARGETS if t != target]

branch = current_branch()
if not branch.endswith(target):
    emit_block(f'Branch "{branch}" does not end with target "{target}".')

payload = json.load(sys.stdin)
tool_name = payload.get('tool_name', '')
tool_input = payload.get('tool_input', {})
serialized = json.dumps(tool_input)

for wrong_db in wrong_dbs:
    if wrong_db in serialized:
        emit_block(
            f'Target is {target} ({expected_db}), but the pending action references {wrong_db}.'
        )

if tool_name.startswith('mcp__github__'):
    if not branch.endswith(target):
        emit_block(f'GitHub action blocked: branch "{branch}" does not match target "{target}".')
