package cmd

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

func TestAgentsList_HTTPIntegration(t *testing.T) {
	owner := "frontdesk"
	agentType := gen.AgentType("persona")
	payload := gen.AgentList{
		Data: []gen.Agent{
			{Id: "marketing-assistant", Name: "marketing-assistant", AgentType: &agentType, Owner: &owner},
		},
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/agents" {
			t.Errorf("path = %q, want /v1/agents", r.URL.Path)
		}
		if r.Header.Get("Authorization") != "Bearer test-agents-key" {
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		if r.Header.Get("anthropic-beta") != "managed-agents-2026-04-01" {
			t.Errorf("anthropic-beta = %q", r.Header.Get("anthropic-beta"))
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(payload)
	}))
	defer ts.Close()

	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-agents-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"agents", "list"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "marketing-assistant") {
		t.Fatalf("expected 'marketing-assistant' in output, got: %q", out)
	}
}

func TestPrintAgentList_Table(t *testing.T) {
	owner := "frontdesk"
	agentType := gen.AgentType("skill")
	list := &gen.AgentList{
		Data: []gen.Agent{
			{Id: "my-skill-agent", Name: "my-skill-agent", AgentType: &agentType, Owner: &owner},
		},
	}

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)

	origJSON := flagJSON
	flagJSON = false
	t.Cleanup(func() { flagJSON = origJSON })

	if err := printAgentList(rootCmd, list); err != nil {
		t.Fatalf("printAgentList: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "my-skill-agent") {
		t.Fatalf("expected 'my-skill-agent' in output, got: %q", out)
	}
	if !strings.Contains(out, "frontdesk") {
		t.Fatalf("expected 'frontdesk' in output, got: %q", out)
	}
}

func TestAgentsCreate_NormalizesLegacyAgentJSON(t *testing.T) {
	agentType := gen.AgentType("skill")
	created := false
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost || r.URL.Path != "/v1/agents" {
			t.Errorf("request = %s %s, want POST /v1/agents", r.Method, r.URL.Path)
		}
		if r.Header.Get("anthropic-beta") != managedAgentsBetaHeader {
			t.Errorf("anthropic-beta = %q, want %q", r.Header.Get("anthropic-beta"), managedAgentsBetaHeader)
		}
		var body map[string]any
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			t.Fatalf("decode body: %v", err)
		}
		if body["name"] != "intake" {
			t.Errorf("name = %v, want intake", body["name"])
		}
		if body["agent_type"] != "skill" {
			t.Errorf("agent_type = %v, want skill", body["agent_type"])
		}
		if _, ok := body["id"]; ok {
			t.Errorf("body should not include legacy id: %#v", body)
		}
		if _, ok := body["type"]; ok {
			t.Errorf("body should not include legacy type: %#v", body)
		}
		created = true
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(gen.Agent{Id: "intake", Name: "intake", AgentType: &agentType})
	}))
	defer ts.Close()

	dir := t.TempDir()
	path := filepath.Join(dir, "agent.json")
	if err := os.WriteFile(path, []byte(`{"id":"intake","type":"skill"}`), 0o644); err != nil {
		t.Fatal(err)
	}

	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-agents-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"agents", "create", "-f", path})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v\n%s", err, buf.String())
	}
	if !created {
		t.Fatal("expected create request")
	}
}
