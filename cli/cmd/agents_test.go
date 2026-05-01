package cmd

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

func TestAgentsList_HTTPIntegration(t *testing.T) {
	owner := "frontdesk"
	agentType := gen.AgentType("persona")
	payload := gen.AgentList{
		Data: []gen.Agent{
			{Id: "marketing-assistant", Type: agentType, OwnerEmployee: &owner},
		},
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer test-agents-key" {
			w.WriteHeader(http.StatusUnauthorized)
			return
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
			{Id: "my-skill-agent", Type: agentType, OwnerEmployee: &owner},
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
