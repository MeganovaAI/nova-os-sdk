package cmd

import (
	"bytes"
	"strings"
	"testing"
)

func TestVersionCmd_Plain(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{"version"})

	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	// Verify the version constant lands in the output.
	// Hash lookup is environment-dependent so we don't assert on it.
	if !strings.Contains(out, CLIVersion) {
		t.Fatalf("missing CLIVersion %q in output: %q", CLIVersion, out)
	}
}

func TestVersionCmd_JSON(t *testing.T) {
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	// Temporarily set flagJSON
	origJSON := flagJSON
	flagJSON = true
	t.Cleanup(func() { flagJSON = origJSON })

	rootCmd.SetArgs([]string{"version"})
	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, `"cli_version"`) {
		t.Fatalf("expected JSON output, got: %q", out)
	}
	if !strings.Contains(out, CLIVersion) {
		t.Fatalf("missing CLIVersion in JSON output: %q", out)
	}
}
