// Schema-driven guided agent authoring (libraos-sdk#18).
//
// This subcommand consumes GET /v1/agents/schema (kernel surface
// shipped in MeganovaAI/nova-os#393) so the CLI knows which fields are
// valid on an AgentDef without code-duplicating the field list. Operators
// `--set key=value` (scalars) or `--set-list key=a,b,c` (string lists)
// and the CLI rejects unknown keys with a "did you mean…?" suggestion
// before any HTTP write.
//
// Slice 1 (this file): scriptable mode only — `--set` / `--set-list` /
// `--system-prompt-file` / `--dry-run` / `--confirm`. The interactive
// TUI walk-through (charmbracelet/huh) is slice 2; template gallery +
// skill autocomplete + alias warnings are slice 3+. See #18.

package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"sort"
	"strings"

	"github.com/charmbracelet/huh"
	"github.com/spf13/cobra"
	"gopkg.in/yaml.v3"

	gen "github.com/libraos/sdk/cli/internal/client"
)

var (
	editSetVals          []string
	editSetListVals      []string
	editSystemPromptFile string
	editTemplate         string
	editDryRun           bool
	editConfirm          bool
	editNew              bool
)

var agentsEditCmd = &cobra.Command{
	Use:   "edit <id>",
	Short: "Schema-driven agent authoring (consumes GET /v1/agents/schema)",
	Long: `Guided agent authoring driven by the live AgentDef JSON Schema.

The schema is fetched from GET /v1/agents/schema at run time, so
field validation always matches what the server enforces — no code
duplication, no drift. Unknown --set keys are rejected before any HTTP
write, with a "did you mean…?" suggestion drawn from the schema.

Two modes share the schema-driven validation core:

  • Interactive (default when stdin is a terminal AND no --set flags
    are given). Walks every schema field via a huh form; system_prompt
    opens $EDITOR. Confirms via prompt before submitting.

  • Scriptable / CI-friendly (when any --set / --set-list /
    --system-prompt-file flag is given OR stdin isn't a terminal). All
    fields must come from flags. --confirm is required for the actual
    write; --dry-run prints the would-be markdown without submitting.

Examples:
  # Interactive: walk every schema field with a guided form
  nova-os-cli agents edit my-frontdesk-agent

  # Scripted / CI-friendly: set fields explicitly, skip the confirm prompt
  nova-os-cli agents edit my-frontdesk-agent \
      --set model=gemini/gemini-3.1-pro-preview \
      --set agent_type=persona \
      --set-list tools=knowledge_search,human_handoff \
      --system-prompt-file ./prompt.md \
      --confirm

  # Inspect without writing
  nova-os-cli agents edit my-agent \
      --set model=gemini/gemini-3.1-pro-preview \
      --dry-run

  # Create a new agent (POST) instead of editing an existing one (PUT)
  nova-os-cli agents edit my-new-agent --new \
      --set model=gemini/gemini-2.5-flash \
      --set agent_type=skill \
      --confirm

Slice 3 polish (all active):

  • --template <name> seeds the body from a baked starter persona
    (customer-support, legal-assistant, data-analyst, dev-assistant).
    --set / interactive input overrides template values per field.

  • Skill autocomplete — interactive mode's tools field is a multi-
    select populated from GET /api/skills; scriptable mode validates
    --set-list tools=... items against the live skill catalog with a
    "did you mean…?" suggestion. Falls back to free-text input + a
    once-per-run warning when /api/skills is unreachable.

  • Legacy-alias auto-mapping — --set skills=..., --set id=...,
    --set type=..., --set max_turns=... all auto-map to their canonical
    field names (tools / name / agent_type / maxTurns) with a once-per-
    run deprecation warning citing the schema's x-deprecation-target.`,
	Args: cobra.ExactArgs(1),
	RunE: runAgentsEdit,
}

func init() {
	agentsEditCmd.Flags().StringSliceVar(&editSetVals, "set", nil, "Set a scalar field — repeatable: --set key=value")
	agentsEditCmd.Flags().StringSliceVar(&editSetListVals, "set-list", nil, "Set a list field — repeatable: --set-list key=a,b,c")
	agentsEditCmd.Flags().StringVar(&editSystemPromptFile, "system-prompt-file", "", "Path to a file whose contents become the agent's system_prompt body")
	agentsEditCmd.Flags().StringVar(&editTemplate, "template", "", "Seed body from a starter persona (customer-support|legal-assistant|data-analyst|dev-assistant). --set / interactive overrides template values.")
	agentsEditCmd.Flags().BoolVar(&editDryRun, "dry-run", false, "Print the would-be markdown + JSON body without submitting")
	agentsEditCmd.Flags().BoolVar(&editConfirm, "confirm", false, "Skip the interactive confirmation prompt (required for scripted submit)")
	agentsEditCmd.Flags().BoolVar(&editNew, "new", false, "Create a new agent (POST) instead of updating an existing one (PUT)")

	agentsCmd.AddCommand(agentsEditCmd)
}

func runAgentsEdit(cmd *cobra.Command, args []string) error {
	id := args[0]
	ctx := context.Background()

	url, apiKey, err := globalConfig()
	if err != nil {
		return err
	}

	schema, err := fetchAgentSchema(ctx, url, apiKey)
	if err != nil {
		return fmt.Errorf("fetch agent schema: %w", err)
	}
	fields := schemaFieldNames(schema)
	aliases := legacyAliases(schema)
	warner := newAliasWarner(cmd.ErrOrStderr(), deprecationTarget(schema))

	// Skills are fetched best-effort: drives the `tools` multi-select in
	// interactive mode + validates `tools` items in scriptable mode.
	// Endpoint unreachable / non-200 → fall back to free-text input with
	// a once-per-run warning. Authoring never blocks on this.
	skills, skillsErr := fetchSkills(ctx, url, apiKey)
	if skillsErr != nil {
		fmt.Fprintf(cmd.ErrOrStderr(),
			"⚠ /api/skills unreachable (%v); tools field falls back to free-text input + skipped validation.\n",
			skillsErr,
		)
		skills = nil
	}

	// Mode dispatch:
	//   - any scriptable flag set OR --template given → scriptable mode
	//   - else if stdin is a TTY → interactive (huh walk-through)
	//   - else → error (no flags + no TTY would block forever on prompts)
	hasScriptable := len(editSetVals) > 0 || len(editSetListVals) > 0 || editSystemPromptFile != "" || editTemplate != ""

	var body map[string]any
	switch {
	case hasScriptable:
		body = map[string]any{"name": id}
		if editTemplate != "" {
			tmpl, err := loadTemplate(editTemplate)
			if err != nil {
				return err
			}
			applyTemplate(tmpl, body)
			body["name"] = id // template's own name field never wins over positional arg
		}
		if err := applySetFlags(editSetVals, editSetListVals, fields, aliases, warner, body); err != nil {
			return err
		}
		if editSystemPromptFile != "" {
			data, err := os.ReadFile(editSystemPromptFile)
			if err != nil {
				return fmt.Errorf("read --system-prompt-file %q: %w", editSystemPromptFile, err)
			}
			body["system_prompt"] = string(data)
		}
		if names := extractToolNames(body); len(names) > 0 {
			if err := validateSkillNames(names, skills); err != nil {
				return err
			}
		}
	case isInteractive():
		seed := map[string]any{"name": id}
		if editTemplate != "" {
			tmpl, err := loadTemplate(editTemplate)
			if err != nil {
				return err
			}
			applyTemplate(tmpl, seed)
			seed["name"] = id
		}
		body, err = interactiveCollect(schema, skills, id, seed)
		if err != nil {
			return fmt.Errorf("interactive collect: %w", err)
		}
	default:
		return fmt.Errorf("no scriptable flags given and stdin isn't a terminal — pass --set / --set-list / --system-prompt-file / --template, or run from an interactive shell")
	}

	mdPreview, err := renderMarkdownPreview(body)
	if err != nil {
		return fmt.Errorf("render markdown preview: %w", err)
	}
	jsonBody, err := json.MarshalIndent(body, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal request body: %w", err)
	}

	cmd.Println("--- would write data/agents/_runtime/" + id + ".md ---")
	cmd.Print(mdPreview)
	cmd.Println("--- API request body ---")
	cmd.Println(string(jsonBody))

	if editDryRun {
		return nil
	}
	// In interactive mode, ask via huh confirm; in scriptable mode
	// require the explicit --confirm flag (CI safety: no terminal to
	// answer the prompt).
	if !editConfirm {
		if !isInteractive() {
			return fmt.Errorf("submit requires --confirm (or pass --dry-run to inspect without writing)")
		}
		var ok bool
		if err := huh.NewConfirm().
			Title("Submit to nova-os?").
			Description(fmt.Sprintf("Will %s agent %q.",
				map[bool]string{true: "CREATE", false: "UPDATE"}[editNew], id)).
			Affirmative("Yes, submit").
			Negative("No, abort").
			Value(&ok).
			Run(); err != nil {
			return err
		}
		if !ok {
			cmd.Println("aborted; nothing written")
			return nil
		}
	}

	c, err := newClient()
	if err != nil {
		return err
	}
	apiBody := agentEditAPIBody(body)
	if editNew {
		var createBody gen.CreateAgentJSONRequestBody
		if err := mapToStruct(apiBody, &createBody); err != nil {
			return fmt.Errorf("marshal create body: %w", err)
		}
		resp, err := c.CreateAgentWithResponse(ctx, createBody)
		if err != nil {
			return fmt.Errorf("create agent: %w", err)
		}
		if resp.JSON201 == nil {
			return fmt.Errorf("unexpected status %s: %s", resp.Status(), string(resp.Body))
		}
		cmd.Println("✓ created", id)
	} else {
		var updateBody gen.UpdateAgentJSONRequestBody
		if err := mapToStruct(apiBody, &updateBody); err != nil {
			return fmt.Errorf("marshal update body: %w", err)
		}
		resp, err := c.UpdateAgentWithResponse(ctx, id, updateBody)
		if err != nil {
			return fmt.Errorf("update agent: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s: %s", resp.Status(), string(resp.Body))
		}
		cmd.Println("✓ updated", id)
	}
	return nil
}

// fetchAgentSchema does a raw GET on the beta-gated agents/schema
// endpoint. The raw request keeps this helper decoupled from generated
// client churn while still enforcing the same auth headers.
func fetchAgentSchema(ctx context.Context, baseURL, apiKey string) (map[string]any, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet,
		strings.TrimRight(baseURL, "/")+"/v1/agents/schema", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Accept", "application/json")
	req.Header.Set("anthropic-beta", managedAgentsBetaHeader)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, body)
	}
	var schema map[string]any
	if err := json.Unmarshal(body, &schema); err != nil {
		return nil, fmt.Errorf("parse schema JSON: %w", err)
	}
	return schema, nil
}

func agentEditAPIBody(body map[string]any) map[string]any {
	out := make(map[string]any, len(body))
	for k, v := range body {
		out[k] = v
	}
	if v, ok := out["id"]; ok {
		if _, exists := out["name"]; !exists {
			out["name"] = v
		}
		delete(out, "id")
	}
	if v, ok := out["type"]; ok {
		if _, exists := out["agent_type"]; !exists {
			out["agent_type"] = v
		}
		delete(out, "type")
	}
	if v, ok := out["system_prompt"]; ok {
		if _, exists := out["system"]; !exists {
			out["system"] = v
		}
		delete(out, "system_prompt")
	}
	if v, ok := out["maxTurns"]; ok {
		if _, exists := out["max_turns"]; !exists {
			out["max_turns"] = v
		}
		delete(out, "maxTurns")
	}
	if v, ok := out["tools"]; ok {
		out["tools"] = toolNamesForAPI(v)
	}
	return out
}

func toolNamesForAPI(v any) []string {
	switch tools := v.(type) {
	case []string:
		return tools
	case []map[string]any:
		out := make([]string, 0, len(tools))
		for _, t := range tools {
			if name, _ := t["name"].(string); name != "" {
				out = append(out, name)
			}
		}
		return out
	case []any:
		out := make([]string, 0, len(tools))
		for _, t := range tools {
			switch item := t.(type) {
			case string:
				if item != "" {
					out = append(out, item)
				}
			case map[string]any:
				if name, _ := item["name"].(string); name != "" {
					out = append(out, name)
				}
			}
		}
		return out
	default:
		return nil
	}
}

// schemaFieldNames extracts the top-level property names from a JSON
// Schema document. Returns them sorted for deterministic error messages.
func schemaFieldNames(schema map[string]any) []string {
	props, _ := schema["properties"].(map[string]any)
	names := make([]string, 0, len(props))
	for k := range props {
		names = append(names, k)
	}
	sort.Strings(names)
	return names
}

// applySetFlags walks --set / --set-list flags and writes into body,
// rejecting any key the schema doesn't declare. `tools` is the one
// special-case: schema declares it as []{name: string}; --set-list
// tools=a,b expands to [{name:a},{name:b}].
//
// aliases (legacy → canonical) and warner (once-per-key deprecation
// emitter) handle the schema's x-legacy-aliases extension: operators
// can still pass --set skills=... or --set id=... and get an auto-
// mapped result plus a one-line warning citing the deprecation target.
// Both nil = no alias handling (used by older test paths).
func applySetFlags(setVals, setListVals []string, fields []string, aliases map[string]string, warner *aliasWarner, body map[string]any) error {
	for _, kv := range setVals {
		k, v, ok := strings.Cut(kv, "=")
		if !ok {
			return fmt.Errorf("--set requires key=value, got %q", kv)
		}
		k = strings.TrimSpace(k)
		canonical, wasLegacy := mapAlias(k, aliases)
		if wasLegacy {
			warner.warn(k, canonical)
		}
		if err := validateField(canonical, fields); err != nil {
			return err
		}
		body[canonical] = v
	}
	for _, kv := range setListVals {
		k, v, ok := strings.Cut(kv, "=")
		if !ok {
			return fmt.Errorf("--set-list requires key=a,b,c, got %q", kv)
		}
		k = strings.TrimSpace(k)
		canonical, wasLegacy := mapAlias(k, aliases)
		if wasLegacy {
			warner.warn(k, canonical)
		}
		if err := validateField(canonical, fields); err != nil {
			return err
		}
		items := splitTrim(v, ",")
		if canonical == "tools" {
			tools := make([]map[string]any, len(items))
			for i, item := range items {
				tools[i] = map[string]any{"name": item}
			}
			body[canonical] = tools
		} else {
			body[canonical] = items
		}
	}
	return nil
}

// validateField is a small "did you mean…?" check against the schema's
// declared property names. Suggestion is a 2-char-prefix match (good
// enough for typos like 'mode' → 'model'); falls back to the full field
// list when no near-match exists.
func validateField(k string, fields []string) error {
	for _, f := range fields {
		if f == k {
			return nil
		}
	}
	for _, f := range fields {
		if len(k) >= 2 && strings.HasPrefix(f, k[:2]) {
			return fmt.Errorf("unknown field %q (did you mean %q?)", k, f)
		}
	}
	return fmt.Errorf("unknown field %q (valid fields: %s)", k, strings.Join(fields, ", "))
}

// renderMarkdownPreview emits the agent markdown shape: YAML frontmatter
// for the declared fields, then the system_prompt as the markdown body.
// Mirrors what data/agents/_runtime/<id>.md looks like on disk so the
// operator can see exactly what they're about to write.
func renderMarkdownPreview(body map[string]any) (string, error) {
	yamlPart := make(map[string]any, len(body))
	promptBody := ""
	for k, v := range body {
		if k == "system_prompt" {
			if s, ok := v.(string); ok {
				promptBody = s
				continue
			}
		}
		yamlPart[k] = v
	}
	yamlBytes, err := yaml.Marshal(yamlPart)
	if err != nil {
		return "", err
	}
	out := "---\n" + string(yamlBytes) + "---\n"
	if promptBody != "" {
		out += "\n" + strings.TrimRight(promptBody, "\n") + "\n"
	}
	return out, nil
}

// mapToStruct re-marshals a map[string]any through JSON to populate the
// generated request body struct. The generated types carry their own
// field validators; this hop lets us build the body dynamically (via
// --set) and still hand a typed value to the generated client.
func mapToStruct(m map[string]any, out any) error {
	b, err := json.Marshal(m)
	if err != nil {
		return err
	}
	return json.Unmarshal(b, out)
}

// splitTrim splits on sep and trims spaces from each element.
func splitTrim(s, sep string) []string {
	parts := strings.Split(s, sep)
	out := make([]string, 0, len(parts))
	for _, p := range parts {
		out = append(out, strings.TrimSpace(p))
	}
	return out
}
