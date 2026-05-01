package cmd

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestValidate_CleanFolder(t *testing.T) {
	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "employees"), "frontdesk.md", `---
id: frontdesk
display_name: Front Desk
model_config:
  answer:
    primary: anthropic/claude-opus-4-7
---
`)
	mustMk(t, filepath.Join(dir, "agents"), "intake.md", `---
agent_id: intake
name: intake
agent_type: skill
owner_employee: frontdesk
---
`)

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"validate", dir})
	t.Cleanup(func() { rootCmd.SetArgs(nil) })

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("expected clean validate, got %v\n%s", err, buf.String())
	}
	if !strings.Contains(buf.String(), "OK") {
		t.Fatalf("expected OK in output, got %q", buf.String())
	}
}

func TestValidate_DetectsVertexSchemaBug(t *testing.T) {
	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "agents"), "broken.md", `---
agent_id: broken
name: broken
agent_type: skill
custom_tools:
  - name: fetch
    input_schema:
      type: object
      properties:
        results:
          type: array
---
`)

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"validate", dir})
	t.Cleanup(func() { rootCmd.SetArgs(nil) })

	if err := rootCmd.Execute(); err == nil {
		t.Fatal("expected error on missing items, got nil")
	}
	if !strings.Contains(buf.String(), "items") {
		t.Fatalf("expected items error in output, got %q", buf.String())
	}
}

func TestValidate_DetectsBareModelName(t *testing.T) {
	dir := t.TempDir()
	mustMk(t, filepath.Join(dir, "agents"), "bare.md", `---
agent_id: bare
name: bare
agent_type: skill
model_config:
  answer:
    primary: claude-opus-4-7
---
`)

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"validate", dir})
	t.Cleanup(func() { rootCmd.SetArgs(nil) })

	if err := rootCmd.Execute(); err == nil {
		t.Fatal("expected error on bare model name, got nil")
	}
}

func mustMk(t *testing.T, dir, name, content string) {
	t.Helper()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatalf("mkdir: %v", err)
	}
	if err := os.WriteFile(filepath.Join(dir, name), []byte(content), 0o644); err != nil {
		t.Fatalf("write: %v", err)
	}
}
