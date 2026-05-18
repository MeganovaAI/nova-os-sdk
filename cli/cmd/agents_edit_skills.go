// Skill autocomplete + validation for `nova-os-cli agents edit`
// (slice 3 of nova-os-sdk#18).
//
// `GET /api/skills` returns the skills available on the running
// Nova OS. We use it two ways:
//
//   - Interactive mode: the `tools` field's prompt becomes a
//     huh.NewMultiSelect populated from the live skill list instead of
//     plain free-text input. (Wired in agents_edit_interactive.go.)
//
//   - Scriptable mode: `--set-list tools=a,b,c` items are validated
//     against the known skills with a "did you mean…?" suggestion
//     when they miss.
//
// Fail-soft: if /api/skills returns non-200 (deployment misconfig,
// admin-scope issue, nginx proxy hiccup like today's 502s at
// 40.49.6.2:8443), the autocomplete falls back to free-text input
// with a once-per-run warning. Authoring is never blocked by an
// unreachable skills endpoint.

package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
)

// fetchSkills calls GET /api/skills on the partner-prefix nova-os
// endpoint and returns the sorted list of skill names. Non-200
// responses return (nil, error) — the caller decides whether to
// fail-soft (interactive mode does; scriptable mode reports the
// underlying error).
func fetchSkills(ctx context.Context, baseURL, apiKey string) ([]string, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet,
		strings.TrimRight(baseURL, "/")+"/api/skills", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Accept", "application/json")

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

	var payload struct {
		Skills []struct {
			Name string `json:"name"`
		} `json:"skills"`
	}
	if err := json.Unmarshal(body, &payload); err != nil {
		return nil, fmt.Errorf("parse /api/skills response: %w", err)
	}
	names := make([]string, 0, len(payload.Skills))
	for _, s := range payload.Skills {
		if s.Name != "" {
			names = append(names, s.Name)
		}
	}
	return names, nil
}

// validateSkillNames checks each requested skill against the known
// list and returns an error naming the first unknown one (with a
// "did you mean…?" suggestion using the same 2-char-prefix matcher
// validateField uses for schema field names). knownSkills==nil means
// the skills endpoint was unreachable; validation is skipped and the
// authoring proceeds.
func validateSkillNames(requested, knownSkills []string) error {
	if knownSkills == nil {
		return nil
	}
	known := make(map[string]bool, len(knownSkills))
	for _, s := range knownSkills {
		known[s] = true
	}
	for _, r := range requested {
		if known[r] {
			continue
		}
		// Reuse the field-validator's suggestion heuristic.
		for _, s := range knownSkills {
			if len(r) >= 2 && strings.HasPrefix(s, r[:2]) {
				return fmt.Errorf("unknown skill %q (did you mean %q?)", r, s)
			}
		}
		return fmt.Errorf("unknown skill %q (available: %s)", r, strings.Join(knownSkills, ", "))
	}
	return nil
}

// extractToolNames returns the bare skill names from a body's tools
// field, whether it's a []string (--set-list shortcut) or the
// canonical []{name: string} schema shape. Returns nil if tools isn't
// set or isn't a recognized shape.
func extractToolNames(body map[string]any) []string {
	v, ok := body["tools"]
	if !ok {
		return nil
	}
	switch x := v.(type) {
	case []string:
		return x
	case []map[string]any:
		out := make([]string, 0, len(x))
		for _, item := range x {
			if name, ok := item["name"].(string); ok {
				out = append(out, name)
			}
		}
		return out
	case []any:
		// Templates parsed from YAML can land as []any here.
		out := make([]string, 0, len(x))
		for _, item := range x {
			switch t := item.(type) {
			case string:
				out = append(out, t)
			case map[string]any:
				if name, ok := t["name"].(string); ok {
					out = append(out, name)
				}
			}
		}
		return out
	}
	return nil
}
