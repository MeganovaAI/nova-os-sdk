package cmd

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"strings"
	"testing"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

// TestSync_CreatesNewEmployee — server returns 404 on GET, sync POSTs.
func TestSync_CreatesNewEmployee(t *testing.T) {
	created := false
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case r.Method == http.MethodGet && strings.Contains(r.URL.Path, "/employees/"):
			w.WriteHeader(http.StatusNotFound)
			json.NewEncoder(w).Encode(map[string]any{"message": "not found"})
		case r.Method == http.MethodPost && strings.Contains(r.URL.Path, "/employees"):
			created = true
			emp := gen.Employee{Id: "frontdesk"}
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(emp)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer ts.Close()

	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "employees"), "frontdesk.md", `---
id: frontdesk
display_name: Front Desk
---
`)

	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync: %v\n%s", err, buf.String())
	}
	if !created {
		t.Fatal("expected POST to /employees, but it was not called")
	}
	if !strings.Contains(buf.String(), "CREATED") {
		t.Fatalf("expected CREATED in output, got %q", buf.String())
	}
}

// TestSync_UpdatesChangedEmployee — server returns 200 with different body, sync PUTs.
func TestSync_UpdatesChangedEmployee(t *testing.T) {
	updated := false
	existingName := "Old Name"
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case r.Method == http.MethodGet && strings.Contains(r.URL.Path, "/employees/"):
			emp := gen.Employee{Id: "frontdesk", DisplayName: &existingName}
			json.NewEncoder(w).Encode(emp)
		case r.Method == http.MethodPut && strings.Contains(r.URL.Path, "/employees/"):
			updated = true
			emp := gen.Employee{Id: "frontdesk"}
			json.NewEncoder(w).Encode(emp)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer ts.Close()

	dir := t.TempDir()
	// Local file has different display_name than server — should trigger UPDATE.
	mustMk(t, filepath.Join(dir, "employees"), "frontdesk.md", `---
id: frontdesk
display_name: New Name
---
`)

	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync: %v\n%s", err, buf.String())
	}
	if !updated {
		t.Fatal("expected PUT to /employees/:id, but it was not called")
	}
	if !strings.Contains(buf.String(), "UPDATED") {
		t.Fatalf("expected UPDATED in output, got %q", buf.String())
	}
}

// TestSync_NoOpWhenIdentical — server returns 200 with identical body, sync skips.
func TestSync_NoOpWhenIdentical(t *testing.T) {
	putCalled := false
	displayName := "Front Desk"
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case r.Method == http.MethodGet && strings.Contains(r.URL.Path, "/employees/"):
			// Return exactly what the local file describes.
			emp := gen.Employee{Id: "frontdesk", DisplayName: &displayName}
			json.NewEncoder(w).Encode(emp)
		case r.Method == http.MethodPut:
			putCalled = true
			w.WriteHeader(http.StatusInternalServerError)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer ts.Close()

	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "employees"), "frontdesk.md", `---
id: frontdesk
display_name: Front Desk
---
`)

	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync: %v\n%s", err, buf.String())
	}
	if putCalled {
		t.Fatal("expected no PUT for identical content, but PUT was called")
	}
	if !strings.Contains(buf.String(), "no-op 1") {
		t.Fatalf("expected no-op 1 in output, got %q", buf.String())
	}
}

// TestSync_CreatesNewAgent — server returns 404 on GET agent, sync POSTs.
func TestSync_CreatesNewAgent(t *testing.T) {
	created := false
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case r.Method == http.MethodGet && strings.Contains(r.URL.Path, "/agents/"):
			w.WriteHeader(http.StatusNotFound)
			json.NewEncoder(w).Encode(map[string]any{"message": "not found"})
		case r.Method == http.MethodPost && strings.Contains(r.URL.Path, "/agents"):
			created = true
			agent := gen.Agent{Id: "intake", Type: gen.AgentTypeSkill}
			w.WriteHeader(http.StatusCreated)
			json.NewEncoder(w).Encode(agent)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer ts.Close()

	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "agents"), "intake.md", `---
id: intake
type: skill
---
`)

	origURL := flagURL
	origKey := flagAPIKey
	flagURL = ts.URL
	flagAPIKey = "test-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync: %v\n%s", err, buf.String())
	}
	if !created {
		t.Fatal("expected POST to /agents, but it was not called")
	}
	if !strings.Contains(buf.String(), "CREATED") {
		t.Fatalf("expected CREATED in output, got %q", buf.String())
	}
}

// TestSync_DryRunDoesNotMutate — --dry-run prints plan without executing.
func TestSync_DryRunDoesNotMutate(t *testing.T) {
	mutated := false
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		if r.Method == http.MethodGet {
			w.WriteHeader(http.StatusNotFound)
			json.NewEncoder(w).Encode(map[string]any{"message": "not found"})
			return
		}
		mutated = true
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer ts.Close()

	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "employees"), "emp.md", `---
id: emp
display_name: Test
---
`)

	origURL := flagURL
	origKey := flagAPIKey
	origDry := syncFlagDry
	flagURL = ts.URL
	flagAPIKey = "test-key"
	syncFlagDry = true
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
		syncFlagDry = origDry
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", "--dry-run", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync dry-run: %v\n%s", err, buf.String())
	}
	if mutated {
		t.Fatal("dry-run must not mutate: a POST/PUT was issued")
	}
	if !strings.Contains(buf.String(), "dry-run") {
		t.Fatalf("expected dry-run in output, got %q", buf.String())
	}
}
