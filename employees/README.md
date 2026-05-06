# Nova OS Employees Playbook

A catalog of persona templates partners install into their Nova OS deployment's `data/agents/` directory.

The Nova OS GHCR image (`ghcr.io/meganovaai/nova-os:v0.1.6+`) ships with a small set of generic personas baked in: `business-assistant`, `marketing-assistant`, `legal-assistant`. This catalog provides specialized templates partners can adopt and adapt when they outgrow the generic personas.

Each template uses the runtime YAML frontmatter Nova OS's loader parses — `cp employees/<vertical>/<name>.md ./data/agents/` works directly without conversion.

---

## Catalog

| Persona | Vertical | What it does | Recommended skills |
|---|---|---|---|
| [`bi-director`](bi/bi-director.md) | BI | Executive-level BI summaries, multi-source reports | `skill_deep_research`, `skill_report` |
| [`bi-market-analyst`](bi/bi-market-analyst.md) | BI | Market-research-flavored BI; competitive analysis | `skill_deep_research` |
| [`content-strategist`](marketing/content-strategist.md) | Marketing | Editorial calendars, briefs, brand-voice review | `skill_deep_research` |
| [`market-researcher`](marketing/market-researcher.md) | Marketing | Competitive analysis, trend reports, sizing | `skill_deep_research`, `skill_report` |
| [`customer-support`](support/customer-support.md) | Support | Inquiry triage, troubleshooting, ticket summaries | — |
| [`data-analyst`](analytics/data-analyst.md) | Analytics | CSV/Excel analysis, statistical summaries, viz planning | `skill_report` |
| [`project-manager`](operations/project-manager.md) | Operations | Planning, status reports, risk surfacing | `skill_report` |
| [`technical-writer`](operations/technical-writer.md) | Operations | API docs, runbooks, README polish | — |
| [`financial-analyst`](finance/financial-analyst.md) | Finance | Model reviews, variance analysis, KPI summaries | `skill_deep_research`, `skill_report` |
| [`compliance-officer`](finance/compliance-officer.md) | Finance | Policy interpretation, regulatory mapping, audit prep | `skill_deep_research` |
| [`email-classifier`](communications/email-classifier.md) | Communications | Inbox triage, intent classification, response stubs | — |

11 templates across 7 verticals.

---

## Install

### Universal — git clone + copy

Works in any environment (CI, ansible, docker-compose volumes, no-CLI hosts).

```bash
# Pin to the SDK release matching your Nova OS version
git clone --branch v0.1.6 https://github.com/MeganovaAI/nova-os-sdk
cd nova-os-sdk

# Pick individual templates
cp employees/bi/bi-director.md /path/to/your/data/agents/

# Or whole vertical bundles
cp employees/marketing/*.md /path/to/your/data/agents/

# Or vendor the whole catalog
cp employees/*/*.md /path/to/your/data/agents/
```

Then either restart Nova OS (the loader scans `data/agents/` at boot) OR `POST /v1/agents` for hot reload via the SDK / API.

### docker-compose volume mount

Drop the cloned repo into a docker-compose volume:

```yaml
services:
  nova-os:
    image: ghcr.io/meganovaai/nova-os:v0.1.6
    volumes:
      # Mount specific verticals you want
      - ./nova-os-sdk/employees/bi:/app/data/agents/bi
      - ./nova-os-sdk/employees/marketing:/app/data/agents/marketing
```

Image's 7 baked personas are always available; mounted templates layer on top.

### CLI convenience

(Slice 2 — coming in nova-os-sdk@v0.1.7. Tracked separately.)

```bash
nova-os-sdk catalog list
nova-os-sdk catalog install bi-director
nova-os-sdk catalog install --bundle bi
nova-os-sdk catalog install --target /opt/nova-os/data/agents bi-director
```

CLI embeds the catalog at build time so installed CLI version === catalog version.

---

## Customizing a template

Templates are starting points — partners customize freely. The recommended pattern is:

1. **Copy** the template into your `data/agents/`.
2. **Rename** if you want to keep the original side-by-side (e.g., `bi-director-customized.md`). The `name:` field in the YAML frontmatter is the canonical ID; rename both the file AND the `name:` field together.
3. **Edit** the system prompt body, capabilities, default model, etc.
4. **Restart** Nova OS or POST the new persona via the SDK.

If you keep the original filename, future `git pull` of the SDK followed by re-copying will overwrite your edits. The rename pattern protects against that.

---

## Schema + versioning

Templates use Nova OS's runtime YAML frontmatter shape (`agent_type: persona`, `brain: true`, `capabilities`, `skills`, `model`, `connectors`, etc.). Full schema: see [`docs/agents.md`](https://github.com/MeganovaAI/nova-os/blob/master/docs/agents.md) (in the nova-os repo).

SDK release tags align with Nova OS release tags — `nova-os@v0.1.6` ↔ `nova-os-sdk@v0.1.6`. Pin via `git checkout v0.1.6` or by installing the matching CLI version. Nova OS's YAML loader is forward-tolerant (`omitempty`, missing fields zero-value), so older catalog content keeps working on newer Nova OS versions.

---

## Out of scope (future)

- **Web-based catalog browser** at catalog.meganova.ai — v1 is git-repo and CLI; hosted browse comes later.
- **Per-template `schema_version` field** — runtime YAML loader is forward-tolerant; YAGNI.
- **Multi-tenant catalog hosting** — partners with private catalogs fork this repo or run their own copy.
- **Catalog-publish-to-server** (`nova-os-sdk catalog publish-to-server <url>`) — runtime install via `POST /v1/agents`. Slice 4 if partners ask.

---

## Spec

[`docs/superpowers/specs/2026-05-06-employees-playbook-design.md`](https://github.com/MeganovaAI/nova-os/blob/master/docs/superpowers/specs/2026-05-06-employees-playbook-design.md) (in the nova-os repo).
