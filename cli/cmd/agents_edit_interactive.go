// Interactive TUI mode for `nova-os-cli agents edit` (slice 2 of #18).
//
// When invoked WITHOUT scriptable flags and with stdin attached to a
// terminal, the subcommand walks every field declared by the live
// AgentDef JSON Schema via a charmbracelet/huh form: one prompt per
// field, with field type driving the input kind (string → input, bool
// → confirm, integer → numeric input with parse-validation, enum →
// select). The `system_prompt` field opens the operator's $EDITOR for
// multi-line composition (same pattern as `git commit`).
//
// Stdin not a terminal AND no scriptable flags = error — protects CI
// pipelines from blocking on prompts that will never receive input.

package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/charmbracelet/huh"
)

// interactiveCollect walks the schema in sorted order and prompts for
// each declared field. Returns a body map suitable for the same
// downstream markdown-preview + JSON-marshal + submit path as the
// scriptable mode.
//
// seed pre-fills body (e.g., from --template) so the operator sees
// template defaults already in the prompt and can accept or override
// per field. id is forced into body["name"] regardless of seed.
//
// skills, when non-nil, swaps the `tools` field's free-text prompt
// for a huh.NewMultiSelect populated from the live skill catalog.
// nil skills = free-text fallback (e.g., when /api/skills is
// unreachable).
func interactiveCollect(schema map[string]any, skills []string, id string, seed map[string]any) (map[string]any, error) {
	body := map[string]any{}
	for k, v := range seed {
		body[k] = v
	}
	body["name"] = id

	props, ok := schema["properties"].(map[string]any)
	if !ok {
		return nil, fmt.Errorf("schema has no properties")
	}
	requiredSet := requiredFieldSet(schema)

	for _, name := range schemaFieldNames(schema) {
		fieldSchema, _ := props[name].(map[string]any)
		if fieldSchema == nil {
			continue
		}
		val, err := promptField(name, fieldSchema, requiredSet[name], body[name], skills)
		if err != nil {
			return nil, err
		}
		if val != nil {
			body[name] = val
		}
	}
	return body, nil
}

// requiredFieldSet pulls the "required" array out of a JSON Schema
// document into a quick-lookup set.
func requiredFieldSet(schema map[string]any) map[string]bool {
	out := map[string]bool{}
	req, _ := schema["required"].([]any)
	for _, r := range req {
		if s, ok := r.(string); ok {
			out[s] = true
		}
	}
	return out
}

// promptField builds the appropriate huh element for a single schema
// field and runs it. The `current` argument is the existing value (if
// any) used to seed the prompt. `skills`, when non-nil and the field
// is `tools`, drives a multi-select populated from the live skill
// catalog instead of plain free-text input. Returns the user's
// response or nil if they skipped.
func promptField(name string, fieldSchema map[string]any, required bool, current any, skills []string) (any, error) {
	ftype, _ := fieldSchema["type"].(string)
	desc, _ := fieldSchema["description"].(string)
	title := name
	if required {
		title += " *"
	}

	// system_prompt and other long-text fields open $EDITOR. Anything
	// that names itself a *_prompt or system body falls into this bucket
	// to keep the multi-line authoring out of the single-line input.
	if name == "system_prompt" {
		initial, _ := current.(string)
		text, err := editInFile(initial, name+".md")
		if err != nil {
			return nil, fmt.Errorf("%s: %w", name, err)
		}
		if text == "" {
			return nil, nil
		}
		return text, nil
	}

	// Enum → select. Non-required enums get a leading "(skip)" entry
	// so the operator can leave the field blank.
	if enumVals, ok := fieldSchema["enum"].([]any); ok {
		opts := make([]huh.Option[string], 0, len(enumVals)+1)
		if !required {
			opts = append(opts, huh.NewOption("(skip)", ""))
		}
		for _, v := range enumVals {
			if s, ok := v.(string); ok {
				opts = append(opts, huh.NewOption(s, s))
			}
		}
		var choice string
		if s, ok := current.(string); ok {
			choice = s
		}
		if err := huh.NewSelect[string]().
			Title(title).
			Description(desc).
			Options(opts...).
			Value(&choice).
			Run(); err != nil {
			return nil, err
		}
		if choice == "" {
			return nil, nil
		}
		return choice, nil
	}

	switch ftype {
	case "string":
		var input string
		if s, ok := current.(string); ok {
			input = s
		}
		if err := huh.NewInput().
			Title(title).
			Description(desc).
			Value(&input).
			Validate(func(s string) error {
				if required && strings.TrimSpace(s) == "" {
					return fmt.Errorf("required")
				}
				return nil
			}).
			Run(); err != nil {
			return nil, err
		}
		if strings.TrimSpace(input) == "" {
			return nil, nil
		}
		return input, nil

	case "boolean":
		var b bool
		if v, ok := current.(bool); ok {
			b = v
		}
		if err := huh.NewConfirm().
			Title(title).
			Description(desc).
			Value(&b).
			Run(); err != nil {
			return nil, err
		}
		return b, nil

	case "integer", "number":
		var input string
		switch v := current.(type) {
		case int:
			input = strconv.Itoa(v)
		case float64:
			input = strconv.FormatFloat(v, 'g', -1, 64)
		}
		if err := huh.NewInput().
			Title(title).
			Description(desc + " (integer)").
			Value(&input).
			Validate(func(s string) error {
				if strings.TrimSpace(s) == "" {
					if required {
						return fmt.Errorf("required")
					}
					return nil
				}
				if _, err := strconv.Atoi(s); err != nil {
					return fmt.Errorf("expected integer, got %q", s)
				}
				return nil
			}).
			Run(); err != nil {
			return nil, err
		}
		if strings.TrimSpace(input) == "" {
			return nil, nil
		}
		n, _ := strconv.Atoi(input)
		return n, nil

	case "array":
		// `tools` with live skills available → multi-select from the
		// catalog (slice 3 of #18). Pre-tick anything already in current
		// (e.g., from --template seed). Falls through to free-text input
		// for non-tools arrays or when skills==nil (endpoint unreachable).
		if name == "tools" && len(skills) > 0 {
			preselected := map[string]bool{}
			for _, s := range extractToolNames(map[string]any{"tools": current}) {
				preselected[s] = true
			}
			opts := make([]huh.Option[string], 0, len(skills))
			for _, s := range skills {
				opts = append(opts, huh.NewOption(s, s).Selected(preselected[s]))
			}
			var picked []string
			if err := huh.NewMultiSelect[string]().
				Title(title).
				Description(desc + " (space to toggle, enter to confirm)").
				Options(opts...).
				Value(&picked).
				Run(); err != nil {
				return nil, err
			}
			if len(picked) == 0 {
				return nil, nil
			}
			tools := make([]map[string]any, len(picked))
			for i, p := range picked {
				tools[i] = map[string]any{"name": p}
			}
			return tools, nil
		}

		// Plain comma-separated input for non-tools arrays AND for
		// tools when /api/skills was unreachable (fail-soft).
		var input string
		if err := huh.NewInput().
			Title(title).
			Description(desc + " (comma-separated)").
			Value(&input).
			Run(); err != nil {
			return nil, err
		}
		if strings.TrimSpace(input) == "" {
			return nil, nil
		}
		items := splitTrim(input, ",")
		if name == "tools" {
			tools := make([]map[string]any, len(items))
			for i, it := range items {
				tools[i] = map[string]any{"name": it}
			}
			return tools, nil
		}
		return items, nil
	}

	// Unknown type: skip gracefully so a schema extension doesn't break
	// the flow. The scriptable path can still set the field via --set.
	return nil, nil
}

// editInFile opens the user's $EDITOR (or vim as fallback) on a temp
// file pre-populated with `initial`, returning the file contents after
// the editor exits. Same pattern as `git commit`.
//
// The temp file is removed on exit; the editor inherits stdin/stdout
// /stderr so terminal editors (vim, nano, emacs -nw) work correctly.
func editInFile(initial, filename string) (string, error) {
	editor := os.Getenv("EDITOR")
	if editor == "" {
		editor = "vim"
	}

	tmpDir, err := os.MkdirTemp("", "nova-os-cli-edit-")
	if err != nil {
		return "", err
	}
	defer os.RemoveAll(tmpDir)

	tmpFile := filepath.Join(tmpDir, filename)
	if err := os.WriteFile(tmpFile, []byte(initial), 0o600); err != nil {
		return "", err
	}

	cmd := exec.Command(editor, tmpFile) //nolint:gosec // $EDITOR is operator-controlled
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return "", fmt.Errorf("editor %q failed: %w", editor, err)
	}

	data, err := os.ReadFile(tmpFile)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}

// isInteractive reports whether stdin is attached to a terminal. Uses
// os.ModeCharDevice (stdlib) so we don't pull golang.org/x/term and
// force a Go version bump for this one check. Pipes, redirects, and CI
// environments all return false.
func isInteractive() bool {
	fi, err := os.Stdin.Stat()
	if err != nil {
		return false
	}
	return (fi.Mode() & os.ModeCharDevice) != 0
}
