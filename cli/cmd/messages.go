// cli/cmd/messages.go
//
// `nova-os-cli messages send` + `nova-os-cli messages stream` — partner
// smoke-test path matching the shape of `test-callback` (see #13). One
// short HTTP round-trip from the same auth/profile resolution as the
// rest of the CLI.
package cmd

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/spf13/cobra"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

var messagesCmd = &cobra.Command{
	Use:   "messages",
	Short: "Send a message to an agent (smoke-test path)",
}

// Shared flags for both send + stream subcommands.
var (
	msgEndUser    string
	msgMetadata   string
	msgModel      string
	msgMaxTokens  int
	msgSystem     string
	msgTimeoutSec int
)

var messagesSendCmd = &cobra.Command{
	Use:   "send <agent_id> <prompt>",
	Short: "POST one-shot message; print the JSON response.",
	Args:  cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		agentID, prompt := args[0], args[1]
		c, err := newClient()
		if err != nil {
			return err
		}
		body, err := buildMessageRequest(prompt, false)
		if err != nil {
			return err
		}
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(msgTimeoutSec)*time.Second)
		defer cancel()

		resp, err := c.CreateMessageWithResponse(ctx, agentID, body, withEndUserHeader(msgEndUser))
		if err != nil {
			return fmt.Errorf("send message: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s\n%s", resp.Status(), string(resp.Body))
		}
		out, err := json.MarshalIndent(resp.JSON200, "", "  ")
		if err != nil {
			return err
		}
		fmt.Fprintln(cmd.OutOrStdout(), string(out))
		return nil
	},
}

var messagesStreamCmd = &cobra.Command{
	Use:   "stream <agent_id> <prompt>",
	Short: "Open a streaming SSE connection; print events as they arrive.",
	Args:  cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		agentID, prompt := args[0], args[1]

		// Build the same request shape, but with stream=true and a
		// raw HTTP path so we can read SSE events line-by-line. The
		// generated CreateMessageWithResponse swallows the body into
		// JSON200; for streaming we need the raw http.Response.
		body, err := buildMessageRequest(prompt, true)
		if err != nil {
			return err
		}
		url, apiKey, err := globalConfig()
		if err != nil {
			return err
		}
		bodyJSON, err := json.Marshal(body)
		if err != nil {
			return err
		}
		req, err := http.NewRequest("POST",
			strings.TrimRight(url, "/")+"/v1/managed/agents/"+agentID+"/messages",
			bytes.NewReader(bodyJSON))
		if err != nil {
			return err
		}
		req.Header.Set("Authorization", "Bearer "+apiKey)
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Accept", "text/event-stream")
		if msgEndUser != "" {
			req.Header.Set("X-End-User", msgEndUser)
		}

		// Long timeout for streams — partners use this for live tailing.
		// Ctrl+C on the calling shell kills the request cleanly.
		client := &http.Client{Timeout: 0}
		resp, err := client.Do(req)
		if err != nil {
			return fmt.Errorf("open stream: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode >= 300 {
			b, _ := io.ReadAll(resp.Body)
			return fmt.Errorf("stream open failed: HTTP %d\n%s", resp.StatusCode, string(b))
		}

		// SSE frame parser — lines until empty line; "data:" lines
		// hold the JSON event. We print one event per line so partners
		// can `| jq` the output.
		scanner := bufio.NewScanner(resp.Body)
		// Default buffer (64 KB) is fine for typical SSE; bump just in
		// case a streamed structured_options payload is large.
		scanner.Buffer(make([]byte, 0, 64*1024), 1024*1024)
		for scanner.Scan() {
			line := scanner.Text()
			if !strings.HasPrefix(line, "data:") {
				continue
			}
			payload := strings.TrimSpace(strings.TrimPrefix(line, "data:"))
			if payload == "" {
				continue
			}
			fmt.Fprintln(cmd.OutOrStdout(), payload)
		}
		return scanner.Err()
	},
}

// buildMessageRequest constructs the MessageRequest body from the CLI
// flag set. Shared by send + stream. Sets stream= per the caller.
func buildMessageRequest(prompt string, stream bool) (gen.CreateMessageJSONRequestBody, error) {
	var msg gen.Message
	msg.Role = gen.RoleUser
	if err := msg.Content.FromMessageContent0(prompt); err != nil {
		return gen.CreateMessageJSONRequestBody{}, fmt.Errorf("set message content: %w", err)
	}

	body := gen.CreateMessageJSONRequestBody{
		Messages: []gen.Message{msg},
		Stream:   &stream,
	}
	if msgModel != "" {
		body.Model = &msgModel
	}
	if msgMaxTokens > 0 {
		body.MaxTokens = &msgMaxTokens
	}
	if msgSystem != "" {
		body.System = &msgSystem
	}
	if msgMetadata != "" {
		var meta gen.MessageRequest_Metadata
		if err := json.Unmarshal([]byte(msgMetadata), &meta); err != nil {
			return body, fmt.Errorf("--metadata is not valid JSON: %w", err)
		}
		body.Metadata = &meta
	}
	return body, nil
}

// withEndUserHeader injects X-End-User on the outbound request when the
// flag is set. No-op otherwise. Used as a generated-client RequestEditor.
func withEndUserHeader(endUser string) gen.RequestEditorFn {
	return func(_ context.Context, req *http.Request) error {
		if endUser != "" {
			req.Header.Set("X-End-User", endUser)
		}
		return nil
	}
}

func init() {
	for _, c := range []*cobra.Command{messagesSendCmd, messagesStreamCmd} {
		c.Flags().StringVar(&msgEndUser, "end-user", "", "X-End-User identity for per-end-user memory scoping")
		c.Flags().StringVar(&msgMetadata, "metadata", "", "JSON object passed as MessageRequest.metadata")
		c.Flags().StringVar(&msgModel, "model", "", "Per-call model override (e.g. anthropic/claude-opus-4-7)")
	}
	messagesSendCmd.Flags().IntVar(&msgMaxTokens, "max-tokens", 0, "max_tokens cap (0 = server default)")
	messagesSendCmd.Flags().StringVar(&msgSystem, "system", "", "Per-call system prompt override")
	messagesSendCmd.Flags().IntVar(&msgTimeoutSec, "timeout", 60, "HTTP timeout in seconds (send only; stream has no timeout)")

	messagesCmd.AddCommand(messagesSendCmd)
	messagesCmd.AddCommand(messagesStreamCmd)
	rootCmd.AddCommand(messagesCmd)
}
