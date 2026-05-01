package cmd

import (
	"bytes"
	"strings"
	"testing"
)

// setTempHome overrides HOME (and USERPROFILE on Windows) to a temp dir so
// config tests don't touch the real ~/.nova-os/config.yaml.
func setTempHome(t *testing.T) string {
	t.Helper()
	tmp := t.TempDir()
	t.Setenv("HOME", tmp)
	t.Setenv("USERPROFILE", tmp) // Windows compat
	return tmp
}

func runConfigCmd(t *testing.T, args ...string) string {
	t.Helper()
	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs(args)
	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("Execute(%v): %v", args, err)
	}
	return buf.String()
}

func TestConfig_SetListDelete(t *testing.T) {
	setTempHome(t)

	// Set a profile
	out := runConfigCmd(t, "config", "set", "partner-prod",
		"--url", "https://nova.example.com",
		"--api-key-env", "NOVA_PROD_KEY",
	)
	if !strings.Contains(out, "partner-prod") {
		t.Fatalf("expected 'partner-prod' in set output, got: %q", out)
	}

	// List should show the profile
	out = runConfigCmd(t, "config", "list")
	if !strings.Contains(out, "partner-prod") {
		t.Fatalf("expected 'partner-prod' in list output, got: %q", out)
	}
	if !strings.Contains(out, "https://nova.example.com") {
		t.Fatalf("expected URL in list output, got: %q", out)
	}

	// Get should show the single profile
	out = runConfigCmd(t, "config", "get", "partner-prod")
	if !strings.Contains(out, "NOVA_PROD_KEY") {
		t.Fatalf("expected api_key_env in get output, got: %q", out)
	}

	// Delete the profile
	out = runConfigCmd(t, "config", "delete", "partner-prod")
	if !strings.Contains(out, "deleted") {
		t.Fatalf("expected 'deleted' in output, got: %q", out)
	}

	// List should now say no profiles
	out = runConfigCmd(t, "config", "list")
	if !strings.Contains(out, "no profiles") {
		t.Fatalf("expected 'no profiles' after delete, got: %q", out)
	}
}

func TestConfig_Default(t *testing.T) {
	setTempHome(t)

	// Create two profiles
	runConfigCmd(t, "config", "set", "staging",
		"--url", "https://staging.example.com",
		"--api-key-env", "NOVA_STAGING_KEY",
	)
	runConfigCmd(t, "config", "set", "prod",
		"--url", "https://prod.example.com",
		"--api-key-env", "NOVA_PROD_KEY",
	)

	// Explicitly set default to prod
	out := runConfigCmd(t, "config", "default", "prod")
	if !strings.Contains(out, "prod") {
		t.Fatalf("expected 'prod' in default output, got: %q", out)
	}

	// List should show prod as default
	out = runConfigCmd(t, "config", "list")
	if !strings.Contains(out, "prod") {
		t.Fatalf("expected 'prod' in list output: %q", out)
	}
}

func TestConfig_Roundtrip(t *testing.T) {
	setTempHome(t)

	// set -> read back via loadProfile
	runConfigCmd(t, "config", "set", "acme",
		"--url", "https://acme.nova.com",
		"--api-key-env", "ACME_KEY",
		"--callback-url", "https://partner.acme.com/nova",
	)

	p, ok := loadProfile("acme")
	if !ok {
		t.Fatal("loadProfile returned not-ok after config set")
	}
	if p.URL != "https://acme.nova.com" {
		t.Fatalf("expected URL 'https://acme.nova.com', got %q", p.URL)
	}
	if p.APIKeyEnv != "ACME_KEY" {
		t.Fatalf("expected APIKeyEnv 'ACME_KEY', got %q", p.APIKeyEnv)
	}
	if p.CallbackURL != "https://partner.acme.com/nova" {
		t.Fatalf("expected CallbackURL, got %q", p.CallbackURL)
	}
}
