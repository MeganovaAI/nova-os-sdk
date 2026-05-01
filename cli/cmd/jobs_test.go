package cmd

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

func TestJobsList_HTTPIntegration(t *testing.T) {
	now := time.Now().UTC()
	payload := gen.JobList{
		Data: []gen.Job{
			{JobId: "job-abc-123", AgentId: "marketing-assistant", Status: gen.JobStatus("running"), CreatedAt: now},
		},
	}
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer test-jobs-key" {
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
	flagAPIKey = "test-jobs-key"
	t.Cleanup(func() {
		flagURL = origURL
		flagAPIKey = origKey
	})

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"jobs", "list"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "job-abc-123") {
		t.Fatalf("expected 'job-abc-123' in output, got: %q", out)
	}
	if !strings.Contains(out, "running") {
		t.Fatalf("expected 'running' in output, got: %q", out)
	}
}

func TestPrintJobList_Table(t *testing.T) {
	now := time.Now().UTC()
	list := &gen.JobList{
		Data: []gen.Job{
			{JobId: "job-xyz-456", AgentId: "test-agent", Status: gen.JobStatus("completed"), CreatedAt: now},
		},
	}

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)

	origJSON := flagJSON
	flagJSON = false
	t.Cleanup(func() { flagJSON = origJSON })

	if err := printJobList(rootCmd, list); err != nil {
		t.Fatalf("printJobList: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "job-xyz-456") {
		t.Fatalf("expected 'job-xyz-456' in output, got: %q", out)
	}
	if !strings.Contains(out, "completed") {
		t.Fatalf("expected 'completed' in output, got: %q", out)
	}
}
