package cmd

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestRequiredFieldSet(t *testing.T) {
	schema := map[string]any{
		"required": []any{"name", "model"},
		"properties": map[string]any{
			"name":        map[string]any{"type": "string"},
			"model":       map[string]any{"type": "string"},
			"description": map[string]any{"type": "string"},
		},
	}
	got := requiredFieldSet(schema)
	if !got["name"] || !got["model"] {
		t.Errorf("expected name + model required, got %+v", got)
	}
	if got["description"] {
		t.Errorf("description should NOT be required, got %+v", got)
	}
}

func TestRequiredFieldSet_EmptyOrMissing(t *testing.T) {
	for _, schema := range []map[string]any{
		{},
		{"properties": map[string]any{"name": map[string]any{}}},
		{"required": []any{}},
	} {
		got := requiredFieldSet(schema)
		if len(got) != 0 {
			t.Errorf("expected empty set for schema=%v, got %v", schema, got)
		}
	}
}

// isInteractive() is not unit-tested — its result depends on the
// invoking environment's stdin (pipe vs TTY), which `go test` does
// not consistently normalize. The CI-blocking error path (no flags
// + no TTY → explicit error message) is documented and exercised
// via the manual smoke step in the PR test plan.

func TestEditInFile_RoundTrip(t *testing.T) {
	// Write a small shell script that overwrites the temp file with a
	// known string, point EDITOR at it, verify editInFile returns the
	// new content. This is the contract that real $EDITOR consumers
	// (vim/nano/code -w) follow.
	scriptDir := t.TempDir()
	scriptPath := filepath.Join(scriptDir, "fake-editor.sh")
	const newContent = "## You are a helpful assistant.\n\nBe concise."
	const script = `#!/bin/sh
cat > "$1" <<'EOF'
` + newContent + `
EOF
`
	if err := os.WriteFile(scriptPath, []byte(script), 0o755); err != nil {
		t.Fatalf("write fake editor: %v", err)
	}

	t.Setenv("EDITOR", scriptPath)

	got, err := editInFile("# stale initial content", "system-prompt.md")
	if err != nil {
		t.Fatalf("editInFile: %v", err)
	}
	if got != newContent {
		t.Errorf("got %q\nwant %q", got, newContent)
	}
}

func TestEditInFile_PreservesInitialWhenEditorIsNoop(t *testing.T) {
	// Editor = `true` (no-op; doesn't touch the file). The initial
	// content should round-trip unchanged.
	t.Setenv("EDITOR", "true")
	const initial = "preserve me"
	got, err := editInFile(initial, "any.md")
	if err != nil {
		t.Fatalf("editInFile: %v", err)
	}
	if got != initial {
		t.Errorf("noop editor should leave content alone; got %q want %q", got, initial)
	}
}

func TestEditInFile_EditorFailurePropagates(t *testing.T) {
	t.Setenv("EDITOR", "false") // /bin/false exits 1
	_, err := editInFile("", "any.md")
	if err == nil {
		t.Fatalf("expected error when editor exits non-zero")
	}
	if !strings.Contains(err.Error(), "editor") {
		t.Errorf("error should mention 'editor'; got: %v", err)
	}
}

func TestPromptField_SystemPromptUsesEditor(t *testing.T) {
	// system_prompt should bypass huh entirely and use $EDITOR. Test
	// the dispatch by setting EDITOR=true (no-op) and checking that
	// the initial value round-trips — proves we went through editInFile,
	// not huh (which would block waiting for terminal input).
	t.Setenv("EDITOR", "true")
	got, err := promptField(
		"system_prompt",
		map[string]any{"type": "string", "description": "the prompt"},
		false,
		"initial prompt body",
		nil, // skills not exercised by editor path
	)
	if err != nil {
		t.Fatalf("promptField: %v", err)
	}
	if got != "initial prompt body" {
		t.Errorf("expected EDITOR no-op to preserve initial; got %v", got)
	}
}

func TestPromptField_UnknownTypeReturnsNilNoError(t *testing.T) {
	// A schema extension introducing an unknown type shouldn't break
	// the walk — promptField returns (nil, nil) and the caller skips.
	got, err := promptField(
		"future_field",
		map[string]any{"type": "geometry-blob"},
		false,
		nil,
		nil,
	)
	if err != nil {
		t.Fatalf("unknown type should not error, got: %v", err)
	}
	if got != nil {
		t.Errorf("expected nil for unknown type, got %v", got)
	}
}
