package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
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

// TestSync_PruneDeletesAbsentResources — server has employees + agents
// the folder doesn't reference; --prune deletes them.
func TestSync_PruneDeletesAbsentResources(t *testing.T) {
	deletedEmps := []string{}
	deletedAgents := []string{}

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		// GET /v1/managed/employees — server lists frontdesk + stale-emp.
		case r.Method == http.MethodGet && r.URL.Path == "/v1/managed/employees":
			json.NewEncoder(w).Encode(gen.EmployeeList{
				Data: []gen.Employee{{Id: "frontdesk"}, {Id: "stale-emp"}},
			})
		// GET /v1/managed/agents — server lists intake + stale-agent.
		case r.Method == http.MethodGet && r.URL.Path == "/v1/managed/agents":
			json.NewEncoder(w).Encode(gen.AgentList{
				Data: []gen.Agent{{Id: "intake", Type: gen.AgentTypeSkill}, {Id: "stale-agent", Type: gen.AgentTypeSkill}},
			})
		// GET /v1/managed/employees/{id} → returns the requested entry
		// so the create/update pass nops on local IDs.
		case r.Method == http.MethodGet && strings.HasPrefix(r.URL.Path, "/v1/managed/employees/"):
			id := strings.TrimPrefix(r.URL.Path, "/v1/managed/employees/")
			json.NewEncoder(w).Encode(gen.Employee{Id: id, DisplayName: ptrStr("Front Desk")})
		case r.Method == http.MethodGet && strings.HasPrefix(r.URL.Path, "/v1/managed/agents/"):
			id := strings.TrimPrefix(r.URL.Path, "/v1/managed/agents/")
			json.NewEncoder(w).Encode(gen.Agent{Id: id, Type: gen.AgentTypeSkill})
		case r.Method == http.MethodDelete && strings.HasPrefix(r.URL.Path, "/v1/managed/employees/"):
			deletedEmps = append(deletedEmps, strings.TrimPrefix(r.URL.Path, "/v1/managed/employees/"))
			w.WriteHeader(http.StatusNoContent)
		case r.Method == http.MethodDelete && strings.HasPrefix(r.URL.Path, "/v1/managed/agents/"):
			deletedAgents = append(deletedAgents, strings.TrimPrefix(r.URL.Path, "/v1/managed/agents/"))
			w.WriteHeader(http.StatusNoContent)
		// PUT — accepted no-op for whichever upstream (the create/update
		// pass may PUT local resources whose minimal GET shape differs
		// from frontmatter; we don't care about the diff path here, only
		// that prune ran correctly).
		case r.Method == http.MethodPut:
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, `{}`)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer ts.Close()

	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "employees"), "frontdesk.md", "---\nid: frontdesk\ndisplay_name: Front Desk\n---\n")
	mustMk(t, filepath.Join(dir, "agents"), "intake.md", "---\nagent_id: intake\ntype: skill\n---\n")

	origURL, origKey, origPrune := flagURL, flagAPIKey, syncFlagPrune
	flagURL, flagAPIKey, syncFlagPrune = ts.URL, "test-key", true
	t.Cleanup(func() {
		flagURL, flagAPIKey, syncFlagPrune = origURL, origKey, origPrune
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", "--prune", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync --prune: %v\n%s", err, buf.String())
	}
	if len(deletedEmps) != 1 || deletedEmps[0] != "stale-emp" {
		t.Errorf("deleted employees = %v, want [stale-emp]", deletedEmps)
	}
	if len(deletedAgents) != 1 || deletedAgents[0] != "stale-agent" {
		t.Errorf("deleted agents = %v, want [stale-agent]", deletedAgents)
	}
	if !strings.Contains(buf.String(), "PRUNED employee stale-emp") {
		t.Errorf("output missing PRUNED line: %s", buf.String())
	}
}

// TestSync_PruneDryRunDoesNotDelete — --prune --dry-run prints the plan
// but does not issue DELETE requests.
func TestSync_PruneDryRunDoesNotDelete(t *testing.T) {
	deleted := false
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		switch {
		case r.Method == http.MethodGet && r.URL.Path == "/v1/managed/employees":
			json.NewEncoder(w).Encode(gen.EmployeeList{
				Data: []gen.Employee{{Id: "stale-emp"}},
			})
		case r.Method == http.MethodGet && r.URL.Path == "/v1/managed/agents":
			json.NewEncoder(w).Encode(gen.AgentList{Data: []gen.Agent{}})
		case r.Method == http.MethodDelete:
			deleted = true
			w.WriteHeader(http.StatusNoContent)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer ts.Close()

	dir := t.TempDir()
	// Empty folders → every server-side resource looks stale.
	if err := os.MkdirAll(filepath.Join(dir, "employees"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Join(dir, "agents"), 0o755); err != nil {
		t.Fatal(err)
	}

	origURL, origKey, origPrune, origDry := flagURL, flagAPIKey, syncFlagPrune, syncFlagDry
	flagURL, flagAPIKey, syncFlagPrune, syncFlagDry = ts.URL, "test-key", true, true
	t.Cleanup(func() {
		flagURL, flagAPIKey, syncFlagPrune, syncFlagDry = origURL, origKey, origPrune, origDry
		rootCmd.SetArgs(nil)
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"sync", "--prune", "--dry-run", dir})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("sync --prune --dry-run: %v\n%s", err, buf.String())
	}
	if deleted {
		t.Fatal("dry-run must not DELETE")
	}
	if !strings.Contains(buf.String(), "[dry-run] PRUNE employee stale-emp") {
		t.Errorf("expected dry-run prune line, got %s", buf.String())
	}
}

func ptrStr(s string) *string { return &s }
