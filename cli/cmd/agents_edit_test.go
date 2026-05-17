package cmd

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestSchemaFieldNames(t *testing.T) {
	schema := map[string]any{
		"properties": map[string]any{
			"name":       map[string]any{"type": "string"},
			"model":      map[string]any{"type": "string"},
			"tools":      map[string]any{"type": "array"},
			"brain":      map[string]any{"type": "boolean"},
			"agent_type": map[string]any{"type": "string"},
		},
	}
	got := schemaFieldNames(schema)
	want := []string{"agent_type", "brain", "model", "name", "tools"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Errorf("got %v, want %v (must be sorted)", got, want)
	}
}

func TestValidateField_Accept(t *testing.T) {
	fields := []string{"agent_type", "brain", "model", "name", "tools"}
	if err := validateField("model", fields); err != nil {
		t.Errorf("expected accept for declared field, got %v", err)
	}
}

func TestValidateField_RejectWithSuggestion(t *testing.T) {
	fields := []string{"agent_type", "brain", "model", "name", "tools"}
	err := validateField("mode", fields)
	if err == nil {
		t.Fatalf("expected reject for typo'd field")
	}
	if !strings.Contains(err.Error(), `"mode"`) || !strings.Contains(err.Error(), `"model"`) {
		t.Errorf("error should suggest 'model' for typo 'mode'; got: %v", err)
	}
}

func TestValidateField_RejectWithFullList(t *testing.T) {
	fields := []string{"agent_type", "brain", "model", "name", "tools"}
	err := validateField("xyz", fields)
	if err == nil {
		t.Fatalf("expected reject for unrelated field")
	}
	if !strings.Contains(err.Error(), "valid fields:") {
		t.Errorf("error should fall back to full field list when no suggestion; got: %v", err)
	}
}

func TestApplySetFlags_Scalar(t *testing.T) {
	fields := []string{"agent_type", "model", "name"}
	body := map[string]any{}
	err := applySetFlags(
		[]string{"model=anthropic/claude-opus-4-7", "agent_type=persona"},
		nil,
		fields,
		nil, nil,
		body,
	)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if body["model"] != "anthropic/claude-opus-4-7" {
		t.Errorf("model not set; body=%+v", body)
	}
	if body["agent_type"] != "persona" {
		t.Errorf("agent_type not set; body=%+v", body)
	}
}

func TestApplySetFlags_List(t *testing.T) {
	fields := []string{"capabilities", "name"}
	body := map[string]any{}
	err := applySetFlags(nil, []string{"capabilities=intake, triage, routing"}, fields, nil, nil, body)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	got, ok := body["capabilities"].([]string)
	if !ok {
		t.Fatalf("capabilities should be []string, got %T", body["capabilities"])
	}
	want := []string{"intake", "triage", "routing"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Errorf("got %v want %v (whitespace must be trimmed)", got, want)
	}
}

func TestApplySetFlags_ToolsExpandsToObjectShape(t *testing.T) {
	fields := []string{"name", "tools"}
	body := map[string]any{}
	err := applySetFlags(nil, []string{"tools=knowledge_search,human_handoff"}, fields, nil, nil, body)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	got, ok := body["tools"].([]map[string]any)
	if !ok {
		t.Fatalf("tools should be []map[string]any (schema shape), got %T", body["tools"])
	}
	if len(got) != 2 || got[0]["name"] != "knowledge_search" || got[1]["name"] != "human_handoff" {
		t.Errorf("tools expansion wrong: %+v", got)
	}
}

func TestApplySetFlags_RejectsUnknownField(t *testing.T) {
	fields := []string{"model", "name"}
	body := map[string]any{}
	err := applySetFlags([]string{"made_up_field=value"}, nil, fields, nil, nil, body)
	if err == nil {
		t.Fatalf("expected reject for unknown field")
	}
	if !strings.Contains(err.Error(), "made_up_field") {
		t.Errorf("error should name the offending field; got: %v", err)
	}
}

func TestApplySetFlags_RejectsMalformed(t *testing.T) {
	fields := []string{"name"}
	body := map[string]any{}
	err := applySetFlags([]string{"no_equals_sign"}, nil, fields, nil, nil, body)
	if err == nil {
		t.Fatalf("expected reject for malformed --set")
	}
	if !strings.Contains(err.Error(), "key=value") {
		t.Errorf("error should describe expected shape; got: %v", err)
	}
}

func TestRenderMarkdownPreview_FrontmatterAndBody(t *testing.T) {
	body := map[string]any{
		"name":          "my-agent",
		"model":         "anthropic/claude-opus-4-7",
		"system_prompt": "You are a helpful assistant.\nBe concise.",
	}
	got, err := renderMarkdownPreview(body)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !strings.HasPrefix(got, "---\n") {
		t.Errorf("missing frontmatter opener; got: %q", got)
	}
	if !strings.Contains(got, "name: my-agent") {
		t.Errorf("frontmatter missing name; got: %q", got)
	}
	if !strings.Contains(got, "model: anthropic/claude-opus-4-7") {
		t.Errorf("frontmatter missing model; got: %q", got)
	}
	// system_prompt must NOT be in frontmatter; it's the body
	if strings.Contains(got, "system_prompt:") {
		t.Errorf("system_prompt should be in body, not YAML; got: %q", got)
	}
	if !strings.Contains(got, "You are a helpful assistant.") {
		t.Errorf("body missing system_prompt content; got: %q", got)
	}
	if !strings.Contains(got, "---\n\nYou are") {
		t.Errorf("expected blank line between frontmatter close and body; got: %q", got)
	}
}

func TestRenderMarkdownPreview_NoSystemPromptOmitsBody(t *testing.T) {
	body := map[string]any{"name": "my-agent", "model": "gemini/gemini-2.5-flash"}
	got, err := renderMarkdownPreview(body)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if strings.Count(got, "---") != 2 {
		t.Errorf("expected exactly 2 frontmatter delimiters; got: %q", got)
	}
}

func TestFetchAgentSchema_HappyPath(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/agents/schema" {
			t.Errorf("unexpected path: %s", r.URL.Path)
		}
		if r.Header.Get("Authorization") != "Bearer test-key" {
			t.Errorf("missing/wrong bearer header: %q", r.Header.Get("Authorization"))
		}
		if r.Header.Get("anthropic-beta") != "managed-agents-2026-04-01" {
			t.Errorf("missing/wrong beta header: %q", r.Header.Get("anthropic-beta"))
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"$schema": "https://json-schema.org/draft/2020-12/schema",
			"properties": map[string]any{
				"name":  map[string]any{"type": "string"},
				"model": map[string]any{"type": "string"},
			},
		})
	}))
	defer srv.Close()

	schema, err := fetchAgentSchema(context.Background(), srv.URL, "test-key")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	names := schemaFieldNames(schema)
	if strings.Join(names, ",") != "model,name" {
		t.Errorf("unexpected field set: %v", names)
	}
}

func TestFetchAgentSchema_PropagatesNon200(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusForbidden)
		_, _ = w.Write([]byte(`{"error":"admin_required"}`))
	}))
	defer srv.Close()

	_, err := fetchAgentSchema(context.Background(), srv.URL, "non-admin-key")
	if err == nil {
		t.Fatalf("expected error on 403")
	}
	if !strings.Contains(err.Error(), "403") || !strings.Contains(err.Error(), "admin_required") {
		t.Errorf("error should surface status + body: %v", err)
	}
}

func TestSplitTrim(t *testing.T) {
	got := splitTrim("  a , b ,c", ",")
	want := []string{"a", "b", "c"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Errorf("got %v want %v", got, want)
	}
}
