# Deployment

How to run Nova OS in production. For first-time install / evaluation, start with [`docs.meganova.ai/nova-os/install`](https://docs.meganova.ai/nova-os/install) — this doc covers what changes when you go from "kick the tires" to "production traffic."

## TL;DR

- **Self-hosted is the v1 default.** Partner runs the binary; data never leaves your network.
- **Three deploy shapes:** single-instance Docker, multi-service compose (recommended), Kubernetes.
- **Postgres is required.** No SQLite fallback. Schema migrations run automatically on first boot.
- **TLS terminates at your edge.** Nova OS speaks plain HTTP on `:8900`. Put Caddy / nginx / Traefik in front.
- **SSE flags are load-bearing** for streaming through Cloudflare / nginx.

## Self-hosted vs cloud

| Concern | Self-hosted | MegaNova-managed |
|---|---|---|
| **Data residency** | Stays on your network | MegaNova infrastructure (region-pinnable) |
| **Operator burden** | You patch / scale / monitor | MegaNova handles it |
| **Customization** | Full — modify `mesh.yaml`, swap providers, custom OIDC | Limited to what the surface exposes |
| **Cost** | Your infra bill + LLM API costs | MegaNova fee + LLM passthrough |
| **Compliance** | You own SOC2 / HIPAA / FedRAMP scope | Inherits MegaNova's posture |
| **Onboarding speed** | Hours-days for first deploy | Minutes |

**Pick self-hosted** when data residency, compliance posture, or LLM provider routing flexibility is the dominant constraint. **Pick managed** for fast iteration on the SDK surface without infrastructure work.

## Three deploy shapes

### Shape 1 — Single-instance Docker (small partner deployments)

Recommended for production traffic up to roughly 50 concurrent SSE streams or 10 RPS sustained — enough for a small partner integration where Nova OS isn't the bottleneck.

```bash
docker run -d --name nova-os \
  --restart=unless-stopped \
  -p 127.0.0.1:8900:8900 \
  -e NOVA_OS_DATABASE_URL="postgres://nova:secret@db.internal:5432/nova_os" \
  -e NOVA_OS_JWT_SECRET="$(openssl rand -hex 32)" \
  -e OPENAI_API_KEY="msk_live_..." \
  -e NOVA_OS_ADMIN_EMAIL="ops@partner.example" \
  -e NOVA_OS_ADMIN_PASSWORD="$(openssl rand -hex 16)" \
  ghcr.io/meganovaai/nova-os:v0.1.5
```

Bind to `127.0.0.1` and let the reverse proxy expose it. Don't expose `:8900` to the public internet directly.

### Shape 2 — Compose with companion apps (recommended)

Use [`MeganovaAI/nova-os-stack`](https://github.com/MeganovaAI/nova-os-stack) — pre-built compose manifests for Nova OS + Postgres + SurrealDB + 8 optional companion apps (LibreChat chat UI, SearXNG, crawl4ai, Firecrawl, Docling, FlashRank, Phoenix, Hermes). Required secrets use the fail-fast `${VAR:?required - hint}` pattern instead of insecure inline defaults.

```bash
git clone https://github.com/MeganovaAI/nova-os-stack
cd nova-os-stack
cp .env.example .env
# edit .env with your secrets

docker compose up -d
```

Add overlay files for the companion apps you want:

```bash
# Add LibreChat chat UI
docker compose -f docker-compose.yml -f overlays/librechat.yml up -d
```

### Shape 3 — Kubernetes (multi-tenant scale)

For partners running multi-tenant SaaS or scale beyond what compose handles.

```yaml
# nova-os-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nova-os
spec:
  replicas: 1   # see "Multi-replica gotchas" below
  selector:
    matchLabels:
      app: nova-os
  template:
    metadata:
      labels:
        app: nova-os
    spec:
      containers:
        - name: nova-os
          image: ghcr.io/meganovaai/nova-os:v0.1.5
          ports:
            - containerPort: 8900
          env:
            - name: NOVA_OS_DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: nova-os-secrets
                  key: database-url
            - name: NOVA_OS_JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: nova-os-secrets
                  key: jwt-secret
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: nova-os-secrets
                  key: openai-api-key
          resources:
            requests:
              cpu: 500m
              memory: 1Gi
            limits:
              cpu: 2000m
              memory: 4Gi
          readinessProbe:
            httpGet:
              path: /api/health
              port: 8900
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /api/health
              port: 8900
            periodSeconds: 30
            failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: nova-os
spec:
  selector:
    app: nova-os
  ports:
    - port: 80
      targetPort: 8900
```

Drop into your existing Ingress / TLS chain. See "Reverse proxy" below for the SSE flags.

## Reverse proxy

Nova OS speaks plain HTTP. TLS terminates at your edge. Three streaming-related flags are required for `/v1/messages` and `/v1/chat/completions` to work over HTTP/2 + Cloudflare — without them, Cloudflare returns `ERR_HTTP2_PROTOCOL_ERROR` mid-stream.

### Caddy (simplest)

Automatic Let's Encrypt + reasonable streaming defaults out of the box:

```caddy
nova-os.your-company.example {
    reverse_proxy localhost:8900 {
        # SSE-friendly defaults
        flush_interval -1
    }
}
```

### nginx (when you have nginx infra)

```nginx
server {
    server_name nova-os.your-company.example;
    listen 443 ssl http2;
    ssl_certificate     /etc/letsencrypt/live/nova-os/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nova-os/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8900;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE streaming endpoints — these flags are load-bearing
        proxy_buffering            off;
        proxy_cache                off;
        chunked_transfer_encoding  off;
        proxy_read_timeout         600s;

        # Cloudflare-fronted deployments need these too:
        gzip                       off;
        # add_header X-Accel-Buffering no;
    }
}
```

### Cloudflare-specific gotchas

If you front nginx with Cloudflare, the SSE behaviour breaks unless **all three** of these hold:

1. `gzip off` in nginx (Cloudflare's compression layer doesn't play well with chunked SSE)
2. `chunked_transfer_encoding off`
3. `X-Accel-Buffering: no` on streaming responses

Symptom of any one being wrong: `ERR_HTTP2_PROTOCOL_ERROR` mid-stream, often after the first few hundred bytes. We've seen this in production multiple times — these flags are not optional.

For partner self-signed deployments using Cloudflare's Full mode, nginx can run with self-signed dummy certs on port 443; Cloudflare terminates the public TLS.

## Postgres

### Sizing

| Workload | RAM | Disk | Notes |
|---|---|---|---|
| Single-tenant evaluation | 1 GB | 5 GB | SQLite-replacement size; default config is fine |
| Small partner (≤1K users) | 4 GB | 50 GB | Bump `shared_buffers` to 1 GB, `work_mem` to 16 MB |
| Multi-tenant SaaS | 16 GB+ | 200 GB+ | Tune per-workload; consider read replicas |
| High-volume report generation | 16 GB+ | 500 GB+ | Most disk goes to vector store + audit log |

Schema migrations run on container start. **For multi-replica deploys, run one replica at a time across an upgrade boundary** — concurrent migrations on the same database race.

### Backup

Standard Postgres patterns. Nova OS data is in a single database; `pg_dump` works. Key tables to verify after restore:

| Table | Contents |
|---|---|
| `users` | Auth identities |
| `agents` | Agent definitions |
| `employees` | Employee definitions |
| `messages` | Chat history |
| `documents` | Document metadata + storage refs |
| `audit_log` | Compliance audit trail (append-only) |

Vector embeddings live in a separate Chroma / pgvector store depending on deploy shape — back that up alongside Postgres.

## Secrets management

Three classes of secrets:

| Secret | Where |
|---|---|
| `NOVA_OS_JWT_SECRET` | Signs user JWTs. Lose it and all existing tokens become invalid. ≥32 hex chars. Use `openssl rand -hex 32`. |
| LLM provider API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`) | Pass through to upstream. Use the MegaNova gateway's `msk_...` key for one-key-fits-all. |
| Webhook callback secrets | Per-tool HMAC-SHA256 secrets. Stored in Nova OS settings DB; partners set via dashboard or `c.settings.set(...)`. |

**Never inline secrets in compose YAML or Kubernetes manifests** — use Docker Secrets, Vault, AWS Secrets Manager, or Kubernetes Secrets. The compose file in [`docs.meganova.ai/nova-os/install`](https://docs.meganova.ai/nova-os/install) is for evaluation only.

### Admin credentials guardrail

Since the `v0.1.5-week-2026-05-09` weekly tag, the daemon **refuses to start with the leaked-default admin email/password** unless `NOVA_OS_ALLOW_INSECURE_DEFAULTS=1` is set. Production deploys should never set that escape hatch:

```bash
# Production (correct):
-e NOVA_OS_ADMIN_EMAIL="ops@partner.example" \
-e NOVA_OS_ADMIN_PASSWORD="$(openssl rand -hex 16)" \

# Local dev only:
-e NOVA_OS_ALLOW_INSECURE_DEFAULTS=1 \
```

If you see `NOVA_OS_ADMIN_EMAIL is unset or matches the insecure default` in startup logs, that's the guardrail firing.

## Observability

### Health endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Liveness — returns `{status: ok, version, build_sha}`. Use as Kubernetes liveness/readiness probe. |
| `GET /api/health/agents_registered` | Returns the count of registered agents. Useful for verifying registry loaded cleanly post-restart. |

### Logs

Plain stdout/stderr — Docker / Kubernetes log collection picks them up unchanged. Key log lines for ops:

| Log line | Means |
|---|---|
| `planner_decision skills=[...] count=N source=structured ... route_hint=<kind>:<detail>` | Brain dispatched these skills; route_hint informs partner-side rendering |
| `skill_completed name=<X> model=<vendor/model> duration=<ms>` | Skill finished successfully |
| `skill_failed name=<X> reason=<...>` | Skill failure — paged by ops |
| `brain bypassed via persona.triage_mode=never` | Per-persona planner-skip; expected for triage agents |
| `deep_research: per-call backend=<name> (from persona web_search_config; defaultBackend=<...>)` | Per-call search-backend resolution |

Grep these for ops dashboards.

### Metrics

Nova OS exposes Prometheus metrics at `/metrics` (when `NOVA_OS_METRICS_ENABLED=true`):

| Metric | Notes |
|---|---|
| `nova_os_chat_requests_total{persona,status}` | Per-persona chat request counter |
| `nova_os_chat_duration_seconds{persona,model_used}` | Chat latency histogram |
| `nova_os_skill_runs_total{name,status}` | Skill execution counter |
| `nova_os_fallback_triggered_total{slot,from_model,to_model}` | Multi-model fallback counter |
| `nova_os_webhook_delivery_total{tool,attempt,outcome}` | Mode B webhook delivery counter |

Wire these into your Grafana / Datadog / alerting stack.

## Upgrades

Nova OS follows semver. Stable tags update `:latest` automatically; weekly partner-validation tags (`vX.Y.Z-week-YYYY-MM-DD`) do not. See [`docs.meganova.ai/nova-os/releases`](https://docs.meganova.ai/nova-os/releases) for the cadence.

**Recommended upgrade path:**

1. **Pin to a specific tag in production**, not `:latest`. Pin format: `vX.Y.Z` (stable) or `vX.Y.Z-week-YYYY-MM-DD` (partner-validation weekly).
2. Test the new tag in a staging environment first. Run the partner's smoke-test scenarios against the new build.
3. **Roll out one replica at a time across an upgrade boundary** — schema migrations run on container start, and concurrent migrations race.
4. Verify `/api/health` returns 200 with the new `build_sha` before draining traffic to the upgraded replica.
5. Monitor `nova_os_chat_requests_total{status="error"}` for a sustained jump post-upgrade.

**Rollback** is a tag downgrade — pull the previous image, restart. Schema migrations are forward-only; if a migration changed something you depend on, restore from backup. Pre-upgrade backup is non-negotiable for major version bumps.

## Multi-replica gotchas

| Gotcha | Mitigation |
|---|---|
| Schema migrations race on first-boot of two replicas | Run one replica at a time across upgrade boundaries. |
| In-memory caches (persona manifest ETag, hook subscription registry) diverge across replicas | Persona manifest re-reads on each `If-None-Match` mismatch — partners using ETag tolerate this. Hook subscriptions are per-replica until [`#177`](https://github.com/MeganovaAI/nova-os/issues/177) follow-up wires persistence. |
| WebSocket / SSE sticky sessions needed | Use `ip_hash` (nginx) or session affinity (Kubernetes Service `sessionAffinity: ClientIP`). |
| Audit log inserts contend on advisory lock | Postgres serializable isolation handles it — don't optimize away. |

For multi-tenant SaaS that spans multiple instances, each tenant should pin to a single Nova OS instance (no cross-instance routing) — per-tenant filesystem and per-tenant agent overrides exist within an instance, not across.

## See also

- [`docs.meganova.ai/nova-os/install`](https://docs.meganova.ai/nova-os/install) — first-time install + evaluation
- [`docs.meganova.ai/nova-os/releases`](https://docs.meganova.ai/nova-os/releases) — tag cadence + migration notes
- [`MeganovaAI/nova-os-stack`](https://github.com/MeganovaAI/nova-os-stack) — production compose manifests + 8 companion apps
- [`getting-started.md`](getting-started.md) — front-door + scenario matrix
- [`multi-model.md`](multi-model.md) — model routing in production
- [`web-search.md`](web-search.md) — backend env vars per provider
