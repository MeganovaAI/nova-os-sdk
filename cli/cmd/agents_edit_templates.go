// Starter persona templates for `nova-os-cli agents edit --template`
// (slice 3 of nova-os-sdk#18).
//
// Hand-curated short personas baked into the CLI binary as Go string
// constants — no embed-path acrobatics (the employees/ catalog lives
// outside the cli/ Go module and can't be //go:embed-ed directly).
// Partners who want richer templates can `cp employees/<vertical>/<name>.md
// data/agents/_runtime/` per the existing employees/README.md flow; this
// gallery is the fast-path for "create a new agent in 30 seconds with
// sensible defaults."
//
// Each template parses into the same body map shape the schema-driven
// form produces — so --template seed values can be overridden by --set
// flags or interactive form input.

package cmd

import (
	"fmt"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

// agentTemplate holds the frontmatter + system-prompt body for a
// starter persona. Parsing happens once at template-fetch time; the
// fields are exposed already-parsed so the caller can copy them
// directly into the body map.
type agentTemplate struct {
	frontmatter  map[string]any
	systemPrompt string
}

// builtinTemplates maps `--template <name>` values to their inline
// markdown. Keep this short and curated — four starter personas that
// demonstrate the schema's required fields + the most common shape
// choices (persona vs skill agent_type, model selection, tool list).
var builtinTemplates = map[string]string{
	"customer-support": `---
name: customer-support
description: Customer support specialist — handles inquiries, troubleshoots issues, manages tickets with empathy and efficiency.
agent_type: persona
brain: true
model: gemini/gemini-2.5-flash
maxTurns: 8
capabilities:
  - support_qa
  - troubleshooting
  - ticket_summarization
---
You are a Customer Support Specialist. Acknowledge the customer's frustration before solving. Provide step-by-step troubleshooting, use simple language, set timeline expectations on escalations. Never blame the customer; mask sensitive data in logs; verify resolution before closing.`,

	"legal-assistant": `---
name: legal-assistant
description: Legal research assistant — retrieves cited answers from the partner's curated legal corpus.
agent_type: persona
brain: true
model: anthropic/claude-opus-4-7
maxTurns: 6
capabilities:
  - legal_research
  - case_summarization
  - citation_grounding
---
You are a Legal Research Assistant. Every claim must cite a source from the provided corpus. Never speculate beyond what's cited. Flag conflicting authority and surface jurisdiction explicitly. Output cited_text plus the source URL on every assertion.`,

	"data-analyst": `---
name: data-analyst
description: Data analyst — CSV/Excel analysis, statistical summaries, visualization planning with cited methodology.
agent_type: persona
brain: true
model: gemini/gemini-2.5-flash
maxTurns: 6
capabilities:
  - csv_analysis
  - excel_analysis
  - statistical_summary
  - viz_planning
---
You are a Data Analyst. State your methodology before showing results. Cite the column / cell / range you're computing over. Flag missing data and explain how you handled it. Recommend visualizations with a one-line rationale for each chart type chosen.`,

	"dev-assistant": `---
name: dev-assistant
description: Developer assistant — code review, documentation drafting, refactoring proposals across multiple languages.
agent_type: persona
brain: true
model: anthropic/claude-opus-4-7
maxTurns: 8
capabilities:
  - code_review
  - documentation
  - refactoring
---
You are a Developer Assistant. Read code carefully before commenting. Distinguish between "this works but" (style/maintainability) and "this is broken" (correctness/security). Show diffs, not just prose. Cite the file:line you're referring to. Never silently change behavior in a refactor — call out behavioral diffs explicitly.`,
}

// listTemplates returns the sorted list of available --template names.
func listTemplates() []string {
	names := make([]string, 0, len(builtinTemplates))
	for k := range builtinTemplates {
		names = append(names, k)
	}
	sort.Strings(names)
	return names
}

// loadTemplate parses a builtin template by name and returns the
// frontmatter map + system-prompt body. Used to seed the body before
// --set flags / interactive form fill.
func loadTemplate(name string) (*agentTemplate, error) {
	raw, ok := builtinTemplates[name]
	if !ok {
		return nil, fmt.Errorf("unknown template %q (available: %s)",
			name, strings.Join(listTemplates(), ", "))
	}
	return parseTemplate(raw)
}

// parseTemplate splits frontmatter from body and unmarshals the
// frontmatter as YAML. Lenient on trailing whitespace; rejects missing
// or malformed frontmatter delimiters loudly so we don't silently load
// a half-template.
func parseTemplate(raw string) (*agentTemplate, error) {
	// Expect leading "---\n", a YAML block, "---\n", then markdown body.
	if !strings.HasPrefix(raw, "---\n") {
		return nil, fmt.Errorf("template missing leading frontmatter delimiter")
	}
	rest := raw[len("---\n"):]
	close := strings.Index(rest, "\n---\n")
	if close == -1 {
		return nil, fmt.Errorf("template missing closing frontmatter delimiter")
	}
	yamlPart := rest[:close]
	bodyPart := strings.TrimSpace(rest[close+len("\n---\n"):])

	var fm map[string]any
	if err := yaml.Unmarshal([]byte(yamlPart), &fm); err != nil {
		return nil, fmt.Errorf("parse template frontmatter: %w", err)
	}
	return &agentTemplate{frontmatter: fm, systemPrompt: bodyPart}, nil
}

// applyTemplate seeds body with the template's frontmatter and stores
// system_prompt under the conventional key. Pre-existing body keys are
// preserved (so --template can be combined with --set: template provides
// defaults, --set overrides).
func applyTemplate(tmpl *agentTemplate, body map[string]any) {
	for k, v := range tmpl.frontmatter {
		if _, present := body[k]; present {
			continue
		}
		body[k] = v
	}
	if _, present := body["system_prompt"]; !present && tmpl.systemPrompt != "" {
		body["system_prompt"] = tmpl.systemPrompt
	}
}
