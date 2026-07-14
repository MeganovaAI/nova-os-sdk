# LibraOS Employees Playbook

A catalog of persona templates partners install into their LibraOS deployment's `data/agents/` directory.

The LibraOS GHCR image (`ghcr.io/meganovaai/nova-os:v0.1.6+`) ships with a small set of generic personas baked in: `business-assistant`, `marketing-assistant`, `legal-assistant`. This catalog provides specialized templates partners can adopt and adapt when they outgrow the generic personas.

Each template uses the runtime YAML frontmatter LibraOS's loader parses — `cp employees/<vertical>/<name>.md ./data/agents/` works directly without conversion.

---

## Catalog

| Persona | Vertical | What it does | Recommended skills |
|---|---|---|---|
| [`content-strategist`](marketing/content-strategist.md) | Marketing | Editorial calendars, briefs, brand-voice review | `skill_deep_research` |
| [`market-researcher`](marketing/market-researcher.md) | Marketing | Competitive analysis, trend reports, sizing | `skill_deep_research`, `skill_report` |
| [`customer-support`](support/customer-support.md) | Support | Inquiry triage, troubleshooting, ticket summaries | — |
| [`data-analyst`](analytics/data-analyst.md) | Analytics | CSV/Excel analysis, statistical summaries, viz planning | `skill_report` |
| [`project-manager`](operations/project-manager.md) | Operations | Planning, status reports, risk surfacing | `skill_report` |
| [`technical-writer`](operations/technical-writer.md) | Operations | API docs, runbooks, README polish | — |
| [`financial-analyst`](finance/financial-analyst.md) | Finance | Model reviews, variance analysis, KPI summaries | `skill_deep_research`, `skill_report` |
| [`compliance-officer`](finance/compliance-officer.md) | Finance | Policy interpretation, regulatory mapping, audit prep | `skill_deep_research` |
| [`email-classifier`](communications/email-classifier.md) | Communications | Inbox triage, intent classification, response stubs | — |

9 generic specialist templates across 6 verticals.

**Vertical specialists not in this catalog** — BI, intake, legal-specialist, and other domain-specific personas tend to carry partner-tenant-specific phrasing (Quebec defaults, internal product names, custom KPI definitions). The LibraOS image bakes a generic `business-assistant` as the BI starting point; partners who want their own BI / intake / legal-specialist personas author them privately and install via the slice-2 CLI's external-source flags (`--from-file`, `--from-url`, `--from-repo <github-org>/<repo>/<path>`).

---

## Install

### Universal — git clone + copy

Works in any environment (CI, ansible, docker-compose volumes, no-CLI hosts).

```bash
# Pin to the SDK release matching your LibraOS version
git clone --branch v0.1.7 https://github.com/libraos/sdk
cd libraos-sdk

# Pick individual templates
cp employees/bi/bi-director.md /path/to/your/data/agents/

# Or whole vertical bundles
cp employees/marketing/*.md /path/to/your/data/agents/

# Or vendor the whole catalog
cp employees/*/*.md /path/to/your/data/agents/
```

Then either restart LibraOS (the loader scans `data/agents/` at boot) OR `POST /v1/agents` for hot reload via the SDK / API.

### docker-compose volume mount

Drop the cloned repo into a docker-compose volume:

```yaml
services:
  nova-os:
    image: ghcr.io/meganovaai/nova-os:v0.1.7
    volumes:
      # Mount specific verticals you want
      - ./libraos-sdk/employees/bi:/app/data/agents/bi
      - ./libraos-sdk/employees/marketing:/app/data/agents/marketing
```

Image's 7 baked personas are always available; mounted templates layer on top.

### CLI convenience

(Slice 2 — coming in libraos-sdk@v0.1.8. Tracked separately.)

```bash
libraos-sdk catalog list
libraos-sdk catalog install bi-director
libraos-sdk catalog install --bundle bi
libraos-sdk catalog install --target /opt/nova-os/data/agents bi-director
```

CLI embeds the catalog at build time so installed CLI version === catalog version.

---

## Customizing a template

Templates are starting points — partners customize freely. The recommended pattern is:

1. **Copy** the template into your `data/agents/`.
2. **Rename** if you want to keep the original side-by-side (e.g., `bi-director-customized.md`). The `name:` field in the YAML frontmatter is the canonical ID; rename both the file AND the `name:` field together.
3. **Edit** the system prompt body, capabilities, default model, etc.
4. **Restart** LibraOS or POST the new persona via the SDK.

If you keep the original filename, future `git pull` of the SDK followed by re-copying will overwrite your edits. The rename pattern protects against that.

---

## Schema + versioning

Templates use LibraOS's runtime YAML frontmatter shape (`agent_type: persona`, `brain: true`, `capabilities`, `skills`, `model`, `connectors`, etc.). Full schema: see [`docs/agents.md`](https://github.com/MeganovaAI/nova-os/blob/master/docs/agents.md) (in the nova-os repo).

SDK release tags align with LibraOS release tags — `nova-os@v0.1.7` ↔ `libraos-sdk@v0.1.7`. Pin via `git checkout v0.1.7` or by installing the matching CLI version. LibraOS's YAML loader is forward-tolerant (`omitempty`, missing fields zero-value), so older catalog content keeps working on newer LibraOS versions.

---

## Out of scope (future)

- **Web-based catalog browser** at catalog.meganova.ai — v1 is git-repo and CLI; hosted browse comes later.
- **Per-template `schema_version` field** — runtime YAML loader is forward-tolerant; YAGNI.
- **Multi-tenant catalog hosting** — partners with private catalogs fork this repo or run their own copy.
- **Catalog-publish-to-server** (`libraos-sdk catalog publish-to-server <url>`) — runtime install via `POST /v1/agents`. Slice 4 if partners ask.

---

## Spec

[`docs/superpowers/specs/2026-05-06-employees-playbook-design.md`](https://github.com/MeganovaAI/nova-os/blob/master/docs/superpowers/specs/2026-05-06-employees-playbook-design.md) (in the nova-os repo).
