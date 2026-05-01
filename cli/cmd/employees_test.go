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

func TestPrintEmployeeList_Table(t *testing.T) {
	name := "Front Desk"
	agents := []string{"agent-1"}
	list := &gen.EmployeeList{
		Data: []gen.Employee{
			{Id: "frontdesk", DisplayName: &name, Agents: &agents},
		},
	}

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)

	origJSON := flagJSON
	flagJSON = false
	t.Cleanup(func() { flagJSON = origJSON })

	// Use a fake cobra cmd that writes to buf via rootCmd.OutOrStdout()
	if err := printEmployeeList(rootCmd, list); err != nil {
		t.Fatalf("printEmployeeList: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "frontdesk") {
		t.Fatalf("expected 'frontdesk' in output, got: %q", out)
	}
	if !strings.Contains(out, "Front Desk") {
		t.Fatalf("expected 'Front Desk' in output, got: %q", out)
	}
}

func TestEmployeesList_HTTPIntegration(t *testing.T) {
	// Stub server returning a valid EmployeeList
	displayName := "Test Employee"
	agents := []string{"agent-a"}
	payload := gen.EmployeeList{
		Data: []gen.Employee{
			{Id: "test-emp-1", DisplayName: &displayName, Agents: &agents},
		},
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer test-key" {
			w.WriteHeader(http.StatusUnauthorized)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(payload)
	}))
	defer ts.Close()

	// Override global flags
	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"employees", "list"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "test-emp-1") {
		t.Fatalf("expected 'test-emp-1' in output, got: %q", out)
	}
}
