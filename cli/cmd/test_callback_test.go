package cmd

import (
	"bytes"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
)

func TestTestCallback_PostsSignedPayload(t *testing.T) {
	var capturedSig, capturedIdem string
	var capturedBody []byte

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		capturedSig = r.Header.Get("X-Nova-Signature")
		capturedIdem = r.Header.Get("X-Nova-Idempotency-Key")
		capturedBody, _ = io.ReadAll(r.Body)
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"output":"ok","is_error":false}`))
	}))
	defer srv.Close()

	t.Setenv("NOVA_CB_TEST_SECRET", "test-secret-123456")

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{
		"test-callback",
		"--target", srv.URL,
		"--tool", "fetch_invoice",
		"--input", `{"invoice_id":"INV-9912"}`,
		"--secret-env", "NOVA_CB_TEST_SECRET",
		"--tool-use-id", "toolu_test_42",
		"--agent-id", "invoice-bot",
	})

	resetTestCallbackFlags()
	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("execute: %v\n%s", err, buf.String())
	}

	// Headers landed
	if capturedSig == "" {
		t.Fatal("X-Nova-Signature header empty")
	}
	if capturedIdem != "toolu_test_42" {
		t.Fatalf("X-Nova-Idempotency-Key = %q, want toolu_test_42", capturedIdem)
	}

	// Body shape
	var payload map[string]any
	if err := json.Unmarshal(capturedBody, &payload); err != nil {
		t.Fatalf("body not JSON: %v", err)
	}
	if payload["tool_use_id"] != "toolu_test_42" {
		t.Errorf("tool_use_id = %v", payload["tool_use_id"])
	}
	if payload["name"] != "fetch_invoice" {
		t.Errorf("name = %v", payload["name"])
	}
	if input, _ := payload["input"].(map[string]any); input["invoice_id"] != "INV-9912" {
		t.Errorf("input.invoice_id = %v", input["invoice_id"])
	}

	// Verify signature reproduces correctly
	parts := strings.SplitN(capturedSig, ",", 2)
	tsStr := strings.TrimPrefix(parts[0], "t=")
	v1 := strings.TrimPrefix(parts[1], "v1=")

	signInput := tsStr + ".toolu_test_42." + string(capturedBody)
	mac := hmac.New(sha256.New, []byte("test-secret-123456"))
	mac.Write([]byte(signInput))
	expected := hex.EncodeToString(mac.Sum(nil))
	if expected != v1 {
		t.Errorf("signature didn't reproduce — got v1=%q expected %q", v1, expected)
	}
}

func TestTestCallback_RepeatPostsMultiple(t *testing.T) {
	calls := 0
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		calls++
		w.WriteHeader(http.StatusOK)
	}))
	defer srv.Close()

	t.Setenv("NOVA_CB_TEST_SECRET", "s")

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{
		"test-callback",
		"--target", srv.URL,
		"--tool", "x",
		"--secret-env", "NOVA_CB_TEST_SECRET",
		"--repeat", "3",
	})

	resetTestCallbackFlags()
	if err := rootCmd.Execute(); err != nil {
		t.Fatalf("execute: %v\n%s", err, buf.String())
	}
	if calls != 3 {
		t.Fatalf("expected 3 calls, got %d", calls)
	}
}

func TestTestCallback_FailsOnNon2xx(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadRequest)
	}))
	defer srv.Close()

	t.Setenv("NOVA_CB_TEST_SECRET", "s")

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{
		"test-callback",
		"--target", srv.URL,
		"--tool", "x",
		"--secret-env", "NOVA_CB_TEST_SECRET",
	})

	resetTestCallbackFlags()
	if err := rootCmd.Execute(); err == nil {
		t.Fatal("expected error on 400 response, got nil")
	}
}

func TestTestCallback_FailsOnEmptySecret(t *testing.T) {
	t.Setenv("NOVA_CB_TEST_SECRET", "")

	var buf bytes.Buffer
	rootCmd.SetOut(&buf)
	rootCmd.SetErr(&buf)
	rootCmd.SetArgs([]string{
		"test-callback",
		"--target", "http://example.com",
		"--tool", "x",
		"--secret-env", "NOVA_CB_TEST_SECRET",
	})

	resetTestCallbackFlags()
	if err := rootCmd.Execute(); err == nil {
		t.Fatal("expected error on empty secret, got nil")
	}
	_ = os.Setenv // keep import
}

// resetTestCallbackFlags resets package-level flag vars between tests
// so cobra doesn't carry state across tests in the same process.
func resetTestCallbackFlags() {
	tcFlagTarget = ""
	tcFlagTool = ""
	tcFlagInput = "{}"
	tcFlagSecretEnv = "NOVA_CB_SECRET"
	tcFlagToolUseID = ""
	tcFlagAgentID = "test-agent"
	tcFlagEmployee = ""
	tcFlagRepeat = 1
	tcFlagTimeoutSec = 30
}
