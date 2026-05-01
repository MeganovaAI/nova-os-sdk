// Package sign produces Stripe-style HMAC-SHA256 signatures for
// outgoing test-callback webhooks. The signing scheme matches the
// receiver-side verification in nova_os.callbacks.WebhookRouter
// (Python SDK):
//
//	signed input = "<unix_ts>.<tool_use_id>.<body>"
//	header value = "t=<unix_ts>,v1=<hex(hmac_sha256(secret, signed_input))>"
//
// Binding tool_use_id into the HMAC defeats idempotency-key tampering
// (a malicious party can't reuse a valid signature with a different key).
package sign

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"strconv"
	"time"
)

// Sign returns the canonical X-Nova-Signature header value.
func Sign(secret, toolUseID string, body []byte, now time.Time) string {
	ts := strconv.FormatInt(now.Unix(), 10)
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(ts))
	mac.Write([]byte("."))
	mac.Write([]byte(toolUseID))
	mac.Write([]byte("."))
	mac.Write(body)
	return fmt.Sprintf("t=%s,v1=%s", ts, hex.EncodeToString(mac.Sum(nil)))
}
