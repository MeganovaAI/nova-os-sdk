# nova-os-cli

Single static Go binary for managing Nova OS employees, agents, and jobs from the terminal.

## Install

Pre-built binaries for linux/darwin/windows ship on the GitHub Releases page (multi-arch build pipeline coming soon). For now, install from source:

```bash
go install github.com/MeganovaAI/nova-os-sdk/cli@latest
mv $(go env GOPATH)/bin/cli $(go env GOPATH)/bin/nova-os-cli
```

Or build locally:

```bash
git clone https://github.com/MeganovaAI/nova-os-sdk.git
cd nova-os-sdk/cli
go build -o nova-os-cli .
```

## Quick start

```bash
# One-time profile setup
nova-os-cli config set partner-prod \
  --url https://nova.partner.com \
  --api-key-env NOVA_PROD_KEY

nova-os-cli config default partner-prod
export NOVA_PROD_KEY=<your-bearer-token>

# Verify connection
nova-os-cli version

# Day-to-day
nova-os-cli employees list
nova-os-cli employees get frontdesk
nova-os-cli employees create -f frontdesk.json

nova-os-cli agents list --owner-employee frontdesk
nova-os-cli agents get marketing-assistant

nova-os-cli jobs list --status running
nova-os-cli jobs get job_abc123

# Validate + sync a local folder of agent/employee definitions
nova-os-cli validate ./data/
nova-os-cli sync ./data/
nova-os-cli sync --watch ./data/

nova-os-cli version --json
```

## Profile config

Profiles are stored at `~/.nova-os/config.yaml`:

```yaml
default: partner-prod
profiles:
  partner-prod:
    url: https://nova.partner.com
    api_key_env: NOVA_PROD_KEY
  customer-acme:
    url: https://nova.acme.example.com
    api_key_env: NOVA_ACME_KEY
    callback_url: https://partner.example.com/nova/acme
```

Manage profiles with the `config` subcommand:

```bash
nova-os-cli config set staging --url https://staging.example.com --api-key-env NOVA_STAGING_KEY
nova-os-cli config list
nova-os-cli config get staging
nova-os-cli config default staging
nova-os-cli config delete staging
```

## Auth resolution order

For each command, credentials are resolved in this priority order:

1. `--url` / `--api-key` flags
2. `NOVA_OS_URL` / `NOVA_OS_API_KEY` env vars
3. Profile in `~/.nova-os/config.yaml` (selected by `--profile` flag or `NOVA_OS_PROFILE` env var, falls back to `default:`)

## Global flags

| Flag | Description |
|------|-------------|
| `--profile <name>` | Override active profile |
| `--url <url>` | Nova OS server URL |
| `--api-key <token>` | Bearer token |
| `--json` | Emit JSON output (one object per record, suitable for piping to `jq`) |

## Subcommands

### employees

```bash
nova-os-cli employees list
nova-os-cli employees get <id>
nova-os-cli employees create -f <definition.json>
nova-os-cli employees update <id> -f <patch.json>
nova-os-cli employees delete <id>
```

### agents

```bash
nova-os-cli agents list [--owner-employee <employee-id>]
nova-os-cli agents get <id>
nova-os-cli agents create -f <definition.json>
nova-os-cli agents update <id> -f <patch.json>
nova-os-cli agents delete <id>
```

### jobs

```bash
nova-os-cli jobs list [--status queued|running|completed|failed|cancelled] [--agent-id <id>]
nova-os-cli jobs get <job-id>
nova-os-cli jobs create -f <job.json>
nova-os-cli jobs cancel <job-id>
```

### config

```bash
nova-os-cli config list
nova-os-cli config get <profile>
nova-os-cli config set <profile> --url <url> --api-key-env <ENV_VAR> [--callback-url <url>]
nova-os-cli config default <profile>
nova-os-cli config delete <profile>
```

### validate (offline CI gate)

```bash
nova-os-cli validate ./data/
```

Walks `./data/employees/*.md` and `./data/agents/*.md`, runs the rule chain on each, exits non-zero if any issue is found. Use it as your CI pre-deploy gate.

Rules checked:

- Frontmatter parses cleanly
- `model_config.{answer,planner,skill}.primary` matches `<vendor>/<model>` shape (e.g. `anthropic/claude-opus-4-7`)
- `custom_tools[].input_schema` recursively contains no `type: array` without `items` (catches the deterministic Vertex AI 400 class before runtime)
- `callback.url` is HTTPS (localhost is allowed for dev)
- `agent.owner_employee` references resolve within the validated folder

Exit 0 = green. Exit 1 = block deploy.

```bash
# Machine-readable (suitable for piping to jq)
nova-os-cli validate ./data/ --json
```

### sync (folder → server)

```bash
# One-shot
nova-os-cli sync ./data/

# Watch mode — re-run on every change, 300ms debounce
nova-os-cli sync --watch ./data/

# Preview the plan without executing
nova-os-cli sync --dry-run ./data/
```

Diffs `./data/employees/` and `./data/agents/` against the server, computes a forward-only plan (create/update), and executes it. Server-side resources missing from the folder are NOT deleted (destructive `--prune` is a planned future addition).

### test-callback (Mode B webhook smoke)

Forges a Nova-OS-shaped signed webhook POST to your partner endpoint. Use it to smoke-test your `WebhookRouter` handler before exposing it to live traffic.

```bash
export NOVA_CB_SECRET=your-shared-hmac-secret
nova-os-cli test-callback \
  --target https://partner.example.com/nova/cb \
  --tool fetch_invoice \
  --input '{"invoice_id":"INV-9912"}'

# Same shape Nova OS's Mode B dispatcher would send. Verify your handler
# returns 200 with {"output":"...","is_error":false}.

# Test idempotency dedup — POST 3x with the same tool_use_id, your handler
# should run exactly once
nova-os-cli test-callback --target ... --tool ... --repeat 3 --tool-use-id toolu_dedupe_test
```

The signature scheme is `t=<unix_ts>,v1=<hex(hmac_sha256(secret, ts + "." + tool_use_id + "." + body))>` — matches what `nova_os.callbacks.WebhookRouter` (Python SDK) verifies.

| Flag | Default | Description |
|------|---------|-------------|
| `--target` | (required) | Partner endpoint URL |
| `--tool` | (required) | Tool name to send in the payload |
| `--input` | `{}` | Tool input args as a JSON object |
| `--secret-env` | `NOVA_CB_SECRET` | Name of the env var holding the HMAC secret |
| `--tool-use-id` | random | Fixed `tool_use_id` (useful for idempotency tests) |
| `--agent-id` | `test-agent` | `agent_id` field in the payload |
| `--employee-id` | (empty) | `employee_id` field in the payload |
| `--repeat` | `1` | POST N times to test partner-side idempotency dedup |
| `--timeout` | `30` | Per-request timeout in seconds |

### version

```bash
nova-os-cli version         # human-readable
nova-os-cli version --json  # machine-readable
```

## Coming soon

- `nova-os-cli sync --prune` — destructive sync (removes server-side resources absent from the folder)
- Pre-built binaries for linux/darwin/windows (amd64 + arm64)
