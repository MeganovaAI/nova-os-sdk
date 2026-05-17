package cmd

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestFetchSkills_HappyPath(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/skills" {
			t.Errorf("unexpected path: %s", r.URL.Path)
		}
		if r.Header.Get("Authorization") != "Bearer test-key" {
			t.Errorf("missing bearer: %q", r.Header.Get("Authorization"))
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{
			"skills": []map[string]any{
				{"name": "knowledge_search"},
				{"name": "human_handoff"},
				{"name": "deep_research"},
			},
			"total": 3,
		})
	}))
	defer srv.Close()

	skills, err := fetchSkills(context.Background(), srv.URL, "test-key")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(skills) != 3 {
		t.Errorf("expected 3 skills, got %d: %v", len(skills), skills)
	}
}

func TestFetchSkills_Non200ReturnsError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusForbidden)
		_, _ = w.Write([]byte(`{"error":"admin_required"}`))
	}))
	defer srv.Close()
	_, err := fetchSkills(context.Background(), srv.URL, "key")
	if err == nil {
		t.Fatalf("expected error on 403")
	}
	if !strings.Contains(err.Error(), "403") {
		t.Errorf("error should mention status; got: %v", err)
	}
}

func TestFetchSkills_SkipsEmptyNames(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"skills": []map[string]any{
				{"name": "valid"},
				{"name": ""},
				{"name": "also_valid"},
			},
		})
	}))
	defer srv.Close()
	skills, err := fetchSkills(context.Background(), srv.URL, "k")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(skills) != 2 {
		t.Errorf("expected 2 non-empty skills, got %v", skills)
	}
}

func TestValidateSkillNames_Accept(t *testing.T) {
	if err := validateSkillNames([]string{"a", "b"}, []string{"a", "b", "c"}); err != nil {
		t.Errorf("unexpected error: %v", err)
	}
}

func TestValidateSkillNames_RejectWithSuggestion(t *testing.T) {
	err := validateSkillNames([]string{"knwoledge_search"}, []string{"knowledge_search", "human_handoff"})
	if err == nil {
		t.Fatalf("expected reject")
	}
	if !strings.Contains(err.Error(), "knowledge_search") {
		t.Errorf("should suggest near-match; got: %v", err)
	}
}

func TestValidateSkillNames_NilKnownSkipsValidation(t *testing.T) {
	// /api/skills unreachable → knownSkills is nil → validation is a no-op
	// so the operator can still author. Lock that fail-soft contract.
	if err := validateSkillNames([]string{"whatever", "made_up"}, nil); err != nil {
		t.Errorf("nil knownSkills should skip validation; got: %v", err)
	}
}

func TestExtractToolNames_StringSlice(t *testing.T) {
	body := map[string]any{"tools": []string{"a", "b", "c"}}
	got := extractToolNames(body)
	if strings.Join(got, ",") != "a,b,c" {
		t.Errorf("got %v", got)
	}
}

func TestExtractToolNames_ObjectSlice(t *testing.T) {
	body := map[string]any{
		"tools": []map[string]any{
			{"name": "a"}, {"name": "b"},
		},
	}
	got := extractToolNames(body)
	if strings.Join(got, ",") != "a,b" {
		t.Errorf("got %v", got)
	}
}

func TestExtractToolNames_AnySliceMixedShapes(t *testing.T) {
	// Templates parsed from YAML can produce []any with either bare
	// strings or maps; extract should handle both transparently.
	body := map[string]any{
		"tools": []any{
			"a",
			map[string]any{"name": "b"},
		},
	}
	got := extractToolNames(body)
	if strings.Join(got, ",") != "a,b" {
		t.Errorf("got %v", got)
	}
}

func TestExtractToolNames_AbsentReturnsNil(t *testing.T) {
	got := extractToolNames(map[string]any{"name": "no-tools-here"})
	if got != nil {
		t.Errorf("expected nil when tools absent, got %v", got)
	}
}
