package cmd

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

func TestPrintKnowledgeChunks_Table(t *testing.T) {
	collection := "case-files"
	docID := "doc-7"
	score := float32(0.872)
	resp := &gen.KnowledgeSearchResponse{
		Data: []gen.KnowledgeChunk{
			{Content: "termination clause requires written notice", Collection: &collection, DocumentId: &docID, Score: &score},
		},
	}

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)

	origJSON := flagJSON
	flagJSON = false
	t.Cleanup(func() { flagJSON = origJSON })

	if err := printKnowledgeChunks(rootCmd, resp); err != nil {
		t.Fatalf("printKnowledgeChunks: %v", err)
	}
	out := buf.String()
	for _, want := range []string{"0.872", "case-files", "doc-7", "termination clause"} {
		if !strings.Contains(out, want) {
			t.Fatalf("expected %q in output, got: %q", want, out)
		}
	}
}

func TestPrintKnowledgeChunks_TruncatesLongContent(t *testing.T) {
	long := strings.Repeat("x", 200)
	resp := &gen.KnowledgeSearchResponse{
		Data: []gen.KnowledgeChunk{{Content: long}},
	}
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	origJSON := flagJSON
	flagJSON = false
	t.Cleanup(func() { flagJSON = origJSON })

	if err := printKnowledgeChunks(rootCmd, resp); err != nil {
		t.Fatalf("printKnowledgeChunks: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "...") {
		t.Fatalf("expected truncation marker '...', got: %q", out)
	}
	// 80-char cap (77 + "...") + headers + tabs; raw length should not contain
	// the full 200-char run.
	if strings.Count(out, "x") >= 200 {
		t.Fatalf("expected truncation at 77 chars, got full string: %d 'x's", strings.Count(out, "x"))
	}
}

func TestKnowledgeSearch_HTTPIntegration(t *testing.T) {
	score := float32(0.91)
	payload := gen.KnowledgeSearchResponse{
		Data: []gen.KnowledgeChunk{{Content: "match", Score: &score}},
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost || r.URL.Path != "/v1/managed/knowledge/search" {
			t.Errorf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		if r.Header.Get("Authorization") != "Bearer test-key" {
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		var body gen.KnowledgeSearchRequest
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			t.Errorf("decode body: %v", err)
		}
		if body.Query != "termination" {
			t.Errorf("expected query=termination, got %q", body.Query)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(payload)
	}))
	defer ts.Close()

	origURL, origKey := flagURL, flagAPIKey
	flagURL, flagAPIKey = ts.URL, "test-key"
	t.Cleanup(func() { flagURL, flagAPIKey = origURL, origKey })

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"knowledge", "search", "termination"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "match") {
		t.Fatalf("expected 'match' in output, got: %q", out)
	}
}

func TestKnowledgeCollections_HTTPIntegration(t *testing.T) {
	payload := gen.KnowledgeCollectionList{Data: []string{"default", "case-files", "policies"}}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet || r.URL.Path != "/v1/managed/knowledge/collections" {
			t.Errorf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(payload)
	}))
	defer ts.Close()

	origURL, origKey := flagURL, flagAPIKey
	flagURL, flagAPIKey = ts.URL, "test-key"
	t.Cleanup(func() { flagURL, flagAPIKey = origURL, origKey })

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"knowledge", "collections"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	for _, want := range []string{"default", "case-files", "policies"} {
		if !strings.Contains(out, want) {
			t.Fatalf("expected %q in output, got: %q", want, out)
		}
	}
}

func TestKnowledgeIngest_HTTPIntegration(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost || r.URL.Path != "/v1/managed/knowledge/ingest" {
			t.Errorf("unexpected request: %s %s", r.Method, r.URL.Path)
		}
		var body gen.KnowledgeIngestRequest
		raw, _ := io.ReadAll(r.Body)
		if err := json.Unmarshal(raw, &body); err != nil {
			t.Errorf("decode body: %v", err)
		}
		if body.Content != "this is a test document" {
			t.Errorf("unexpected content: %q", body.Content)
		}
		if body.Title == nil || *body.Title != "Test Doc" {
			t.Errorf("unexpected title: %v", body.Title)
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		w.Write([]byte(`{"document_id": "doc-1"}`))
	}))
	defer ts.Close()

	origURL, origKey := flagURL, flagAPIKey
	flagURL, flagAPIKey = ts.URL, "test-key"
	t.Cleanup(func() { flagURL, flagAPIKey = origURL, origKey })

	// Reset persistent flags from any prior test invocation.
	knowledgeIngestFile = ""
	knowledgeIngestTitle = "Test Doc"
	knowledgeIngestCollection = ""

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"knowledge", "ingest", "this is a test document", "--title", "Test Doc"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "ingested") && !strings.Contains(out, "doc-1") {
		t.Fatalf("expected success marker in output, got: %q", out)
	}
}
