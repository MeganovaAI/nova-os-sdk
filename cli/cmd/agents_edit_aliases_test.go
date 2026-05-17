package cmd

import (
	"bytes"
	"strings"
	"testing"
)

func TestLegacyAliases_ExtractsExtension(t *testing.T) {
	// JSON-unmarshalled schemas land aliases as map[string]any.
	schema := map[string]any{
		"x-legacy-aliases": map[string]any{
			"id":        "name",
			"skills":    "tools",
			"max_turns": "maxTurns",
		},
	}
	got := legacyAliases(schema)
	if got["id"] != "name" || got["skills"] != "tools" || got["max_turns"] != "maxTurns" {
		t.Errorf("got %+v", got)
	}
}

func TestLegacyAliases_MissingReturnsNil(t *testing.T) {
	if got := legacyAliases(map[string]any{}); got != nil {
		t.Errorf("expected nil for missing extension, got %v", got)
	}
}

func TestLegacyAliases_MalformedReturnsNil(t *testing.T) {
	schema := map[string]any{"x-legacy-aliases": "not a map"}
	if got := legacyAliases(schema); got != nil {
		t.Errorf("expected nil for malformed extension, got %v", got)
	}
}

func TestDeprecationTarget(t *testing.T) {
	if got := deprecationTarget(map[string]any{"x-deprecation-target": "v0.2.0"}); got != "v0.2.0" {
		t.Errorf("got %q", got)
	}
	if got := deprecationTarget(map[string]any{}); got != "" {
		t.Errorf("expected empty for missing, got %q", got)
	}
}

func TestMapAlias_LegacyMapsToCanonical(t *testing.T) {
	aliases := map[string]string{"skills": "tools", "id": "name"}
	canonical, wasLegacy := mapAlias("skills", aliases)
	if canonical != "tools" || !wasLegacy {
		t.Errorf("got (%q, %v); want (\"tools\", true)", canonical, wasLegacy)
	}
}

func TestMapAlias_CanonicalPassesThrough(t *testing.T) {
	aliases := map[string]string{"skills": "tools"}
	canonical, wasLegacy := mapAlias("tools", aliases)
	if canonical != "tools" || wasLegacy {
		t.Errorf("got (%q, %v); want (\"tools\", false)", canonical, wasLegacy)
	}
}

func TestMapAlias_NilAliasesIsNoop(t *testing.T) {
	canonical, wasLegacy := mapAlias("anything", nil)
	if canonical != "anything" || wasLegacy {
		t.Errorf("nil aliases should pass through; got (%q, %v)", canonical, wasLegacy)
	}
}

func TestAliasWarner_FiresOncePerKey(t *testing.T) {
	var buf bytes.Buffer
	w := newAliasWarner(&buf, "v0.2.0")
	w.warn("skills", "tools")
	w.warn("skills", "tools") // 2nd call should be silent
	w.warn("skills", "tools") // 3rd same
	w.warn("id", "name")      // different key → 1 line

	out := buf.String()
	if strings.Count(out, "skills") != 1 {
		t.Errorf("expected exactly 1 warning for 'skills'; got: %q", out)
	}
	if !strings.Contains(out, "v0.2.0") {
		t.Errorf("warning should cite deprecation target; got: %q", out)
	}
	if !strings.Contains(out, "id") || !strings.Contains(out, "name") {
		t.Errorf("expected warning for 'id'; got: %q", out)
	}
}

func TestAliasWarner_FallbackTargetWhenAbsent(t *testing.T) {
	var buf bytes.Buffer
	w := newAliasWarner(&buf, "")
	w.warn("skills", "tools")
	if !strings.Contains(buf.String(), "a future version") {
		t.Errorf("missing-target should fall back; got: %q", buf.String())
	}
}

func TestAliasWarner_NilWriterIsNoop(t *testing.T) {
	w := newAliasWarner(nil, "v0.2.0")
	w.warn("skills", "tools") // must not panic
}

// End-to-end: applySetFlags accepts a legacy alias, auto-maps it, warns.
func TestApplySetFlags_AliasAutoMapsAndWarns(t *testing.T) {
	var buf bytes.Buffer
	aliases := map[string]string{"skills": "tools", "id": "name"}
	warner := newAliasWarner(&buf, "v0.2.0")
	fields := []string{"name", "tools"}
	body := map[string]any{}

	// --set-list skills=knowledge_search → maps to tools=[{name:knowledge_search}]
	err := applySetFlags(nil, []string{"skills=knowledge_search,human_handoff"}, fields, aliases, warner, body)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	tools, ok := body["tools"].([]map[string]any)
	if !ok || len(tools) != 2 || tools[0]["name"] != "knowledge_search" {
		t.Errorf("expected tools auto-populated from skills alias; got: %+v", body)
	}
	if _, present := body["skills"]; present {
		t.Errorf("legacy 'skills' key should not appear in body; got: %+v", body)
	}
	if !strings.Contains(buf.String(), "skills") || !strings.Contains(buf.String(), "tools") {
		t.Errorf("warning should be emitted; got: %q", buf.String())
	}
}
