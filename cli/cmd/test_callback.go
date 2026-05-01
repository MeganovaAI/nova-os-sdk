package cmd

import (
	"bytes"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/spf13/cobra"

	"github.com/MeganovaAI/nova-os-sdk/cli/internal/sign"
)

var (
	tcFlagTarget     string
	tcFlagTool       string
	tcFlagInput      string
	tcFlagSecretEnv  string
	tcFlagToolUseID  string
	tcFlagAgentID    string
	tcFlagEmployee   string
	tcFlagRepeat     int
	tcFlagTimeoutSec int
)

var testCallbackCmd = &cobra.Command{
	Use:   "test-callback",
	Short: "Forge a Nova-OS-shaped signed webhook POST to a partner endpoint",
	Long: `Builds the same JSON payload Nova OS's Mode B custom-tool
dispatcher sends, signs it with HMAC-SHA256 over ts + "." + tool_use_id
+ "." + body, and POSTs to --target. Prints response status + body.

Use this to smoke-test a partner-side WebhookRouter handler before
exposing it to live traffic — same signing scheme, no Nova OS server
required.

The --secret-env flag names an environment variable holding the shared
HMAC secret. Must match the secret your WebhookRouter is configured
with (and the secret_ref Nova OS uses to dispatch).`,
	RunE: func(cmd *cobra.Command, args []string) error {
		if tcFlagTarget == "" {
			return fmt.Errorf("--target is required")
		}
		if tcFlagTool == "" {
			return fmt.Errorf("--tool is required")
		}
		if tcFlagSecretEnv == "" {
			return fmt.Errorf("--secret-env is required (name of env var holding HMAC secret)")
		}
		secret := os.Getenv(tcFlagSecretEnv)
		if secret == "" {
			return fmt.Errorf("env var %q is empty — set it before running", tcFlagSecretEnv)
		}

		// Parse --input as JSON (must be a JSON object).
		var inputObj map[string]any
		if tcFlagInput != "" {
			if err := json.Unmarshal([]byte(tcFlagInput), &inputObj); err != nil {
				return fmt.Errorf("--input is not valid JSON: %w", err)
			}
		} else {
			inputObj = map[string]any{}
		}

		toolUseID := tcFlagToolUseID
		if toolUseID == "" {
			toolUseID = "toolu_" + randHex(8)
		}

		payload := map[string]any{
			"tool_use_id": toolUseID,
			"agent_id":    tcFlagAgentID,
			"employee_id": tcFlagEmployee,
			"name":        tcFlagTool,
			"input":       inputObj,
		}
		body, err := json.Marshal(payload)
		if err != nil {
			return fmt.Errorf("marshal payload: %w", err)
		}

		client := &http.Client{Timeout: time.Duration(tcFlagTimeoutSec) * time.Second}
		repeat := tcFlagRepeat
		if repeat < 1 {
			repeat = 1
		}

		var lastStatus int
		for i := 0; i < repeat; i++ {
			now := time.Now().UTC()
			sig := sign.Sign(secret, toolUseID, body, now)

			req, err := http.NewRequestWithContext(cmd.Context(), http.MethodPost, tcFlagTarget, bytes.NewReader(body))
			if err != nil {
				return fmt.Errorf("build request: %w", err)
			}
			req.Header.Set("Content-Type", "application/json")
			req.Header.Set("X-Nova-Signature", sig)
			req.Header.Set("X-Nova-Idempotency-Key", toolUseID)

			resp, err := client.Do(req)
			if err != nil {
				return fmt.Errorf("attempt %d: %w", i+1, err)
			}
			respBody, _ := io.ReadAll(resp.Body)
			resp.Body.Close()
			lastStatus = resp.StatusCode

			cmd.Printf("attempt %d: %s %d\n", i+1, tcFlagTarget, resp.StatusCode)
			if flagJSON {
				cmd.Printf("  payload: %s\n", string(body))
				cmd.Printf("  signature: %s\n", sig)
				cmd.Printf("  idempotency_key: %s\n", toolUseID)
				cmd.Printf("  response: %s\n", truncate(string(respBody), 4096))
			} else {
				if len(respBody) > 0 {
					cmd.Printf("  response: %s\n", truncate(string(respBody), 1024))
				}
			}
		}

		if lastStatus < 200 || lastStatus >= 300 {
			return fmt.Errorf("non-2xx response on final attempt: %d", lastStatus)
		}
		return nil
	},
}

func init() {
	testCallbackCmd.Flags().StringVar(&tcFlagTarget, "target", "", "Partner endpoint URL (required)")
	testCallbackCmd.Flags().StringVar(&tcFlagTool, "tool", "", "Tool name (required)")
	testCallbackCmd.Flags().StringVar(&tcFlagInput, "input", "{}", `Tool input args as JSON object (default {})`)
	testCallbackCmd.Flags().StringVar(&tcFlagSecretEnv, "secret-env", "NOVA_CB_SECRET", "Env var name holding the HMAC secret (default NOVA_CB_SECRET)")
	testCallbackCmd.Flags().StringVar(&tcFlagToolUseID, "tool-use-id", "", "tool_use_id to send (default: random toolu_<hex>)")
	testCallbackCmd.Flags().StringVar(&tcFlagAgentID, "agent-id", "test-agent", "agent_id field on the payload")
	testCallbackCmd.Flags().StringVar(&tcFlagEmployee, "employee-id", "", "employee_id field on the payload")
	testCallbackCmd.Flags().IntVar(&tcFlagRepeat, "repeat", 1, "POST N times (use to test partner-side idempotency dedup)")
	testCallbackCmd.Flags().IntVar(&tcFlagTimeoutSec, "timeout", 30, "Per-request timeout in seconds")

	rootCmd.AddCommand(testCallbackCmd)
}

func randHex(n int) string {
	b := make([]byte, n)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "...[truncated]"
}
