package sign

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"strings"
	"testing"
	"time"
)

func TestSign_Format(t *testing.T) {
	now := time.Date(2026, 5, 1, 12, 0, 0, 0, time.UTC)
	sig := Sign("secret", "toolu_test", []byte(`{"x":1}`), now)
	if !strings.HasPrefix(sig, "t=") {
		t.Fatalf("missing t= prefix: %q", sig)
	}
	if !strings.Contains(sig, ",v1=") {
		t.Fatalf("missing ,v1= part: %q", sig)
	}
}

func TestSign_BindsToolUseID(t *testing.T) {
	now := time.Date(2026, 5, 1, 12, 0, 0, 0, time.UTC)
	sig1 := Sign("secret", "toolu_a", []byte(`{"x":1}`), now)
	sig2 := Sign("secret", "toolu_b", []byte(`{"x":1}`), now)
	if sig1 == sig2 {
		t.Fatalf("signatures must differ when tool_use_id differs (binds idempotency key)")
	}
}

func TestSign_Verifiable(t *testing.T) {
	// External verifier reproduces the signing input and checks HMAC.
	now := time.Date(2026, 5, 1, 12, 0, 0, 0, time.UTC)
	body := []byte(`{"tool_use_id":"toolu_x"}`)
	sig := Sign("verify-test-secret", "toolu_x", body, now)

	parts := strings.SplitN(sig, ",", 2)
	tsStr := strings.TrimPrefix(parts[0], "t=")
	v1 := strings.TrimPrefix(parts[1], "v1=")

	signInput := []byte(tsStr + ".toolu_x." + string(body))
	mac := hmac.New(sha256.New, []byte("verify-test-secret"))
	mac.Write(signInput)
	expected := hex.EncodeToString(mac.Sum(nil))
	if expected != v1 {
		t.Fatalf("v1 didn't match expected — sig=%q", sig)
	}
}
