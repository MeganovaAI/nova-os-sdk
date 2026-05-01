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

### version

```bash
nova-os-cli version         # human-readable
nova-os-cli version --json  # machine-readable
```

## Coming soon

- `nova-os-cli sync --watch ./data/` — live folder-to-server sync
- `nova-os-cli validate ./data/` — offline frontmatter validation
- `nova-os-cli test-callback` — forge signed webhook for partner endpoint smoke tests
- Pre-built binaries for linux/darwin/windows (amd64 + arm64)
