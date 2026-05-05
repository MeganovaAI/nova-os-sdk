// cli/cmd/messages_test.go
//
// Surface tests for `messages send` + `messages stream` — exercise
// flag parsing + body construction; the wire is stubbed via
// httptest.Server so no live server is required.
package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestMessagesSend_PostsJSONBodyAndPrintsResponse(t *testing.T) {
	captured := struct {
		method    string
		path      string
		body      []byte
		auth      string
		endUser   string
	}{}

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		captured.method = r.Method
		captured.path = r.URL.Path
		captured.auth = r.Header.Get("Authorization")
		captured.endUser = r.Header.Get("X-End-User")
		captured.body, _ = io.ReadAll(r.Body)

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		fmt.Fprint(w, `{"id":"msg_1","model":"anthropic/claude-opus-4-7","stop_reason":"end_turn","role":"assistant","content":[{"type":"text","text":"hi"}]}`)
	}))
	defer srv.Close()

	t.Setenv("NOVA_OS_URL", srv.URL)
	t.Setenv("NOVA_OS_API_KEY", "test-key")
	flagURL = ""
	flagAPIKey = ""
	msgEndUser = "tenant-42-user-7"
	msgMetadata = ""
	msgModel = ""
	msgMaxTokens = 0
	msgSystem = ""
	msgTimeoutSec = 5

	out := &strings.Builder{}
	messagesSendCmd.SetOut(out)
	messagesSendCmd.SetErr(out)
	messagesSendCmd.SetArgs([]string{"intake-specialist", "hello"})

	if err := messagesSendCmd.RunE(messagesSendCmd, []string{"intake-specialist", "hello"}); err != nil {
		t.Fatalf("RunE: %v", err)
	}

	if captured.method != "POST" {
		t.Errorf("method = %q, want POST", captured.method)
	}
	if captured.path != "/v1/managed/agents/intake-specialist/messages" {
		t.Errorf("path = %q", captured.path)
	}
	if captured.auth != "Bearer test-key" {
		t.Errorf("auth = %q", captured.auth)
	}
	if captured.endUser != "tenant-42-user-7" {
		t.Errorf("X-End-User = %q", captured.endUser)
	}

	var body map[string]any
	if err := json.Unmarshal(captured.body, &body); err != nil {
		t.Fatalf("body json: %v", err)
	}
	msgs, _ := body["messages"].([]any)
	if len(msgs) != 1 {
		t.Fatalf("messages len = %d", len(msgs))
	}
	first := msgs[0].(map[string]any)
	if first["role"] != "user" {
		t.Errorf("role = %v", first["role"])
	}
	if first["content"] != "hello" {
		t.Errorf("content = %v", first["content"])
	}
	if body["stream"] != false {
		t.Errorf("stream = %v, want false on send", body["stream"])
	}

	got := out.String()
	if !strings.Contains(got, `"id": "msg_1"`) {
		t.Errorf("output missing id: %s", got)
	}
}

func TestMessagesStream_ReadsSSEFramesAndPrintsDataLines(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/event-stream")
		w.WriteHeader(http.StatusOK)
		// Three frames: text_delta, text_delta, done. SSE frames are
		// `data: {json}\n\n`. Our scanner ignores anything not starting
		// with `data:`.
		flusher := w.(http.Flusher)
		fmt.Fprintf(w, "data: {\"type\":\"text\",\"content\":\"hello \"}\n\n")
		flusher.Flush()
		fmt.Fprintf(w, "data: {\"type\":\"text\",\"content\":\"world\"}\n\n")
		flusher.Flush()
		fmt.Fprintf(w, "data: {\"type\":\"done\",\"status\":\"completed\",\"message_id\":\"msg_1\"}\n\n")
		flusher.Flush()
	}))
	defer srv.Close()

	t.Setenv("NOVA_OS_URL", srv.URL)
	t.Setenv("NOVA_OS_API_KEY", "test-key")
	flagURL = ""
	flagAPIKey = ""
	msgEndUser = ""
	msgMetadata = ""
	msgModel = ""

	out := &strings.Builder{}
	messagesStreamCmd.SetOut(out)
	messagesStreamCmd.SetErr(out)

	if err := messagesStreamCmd.RunE(messagesStreamCmd, []string{"intake-specialist", "hi"}); err != nil {
		t.Fatalf("RunE: %v", err)
	}

	got := out.String()
	wantSubstrings := []string{
		`"type":"text","content":"hello "`,
		`"type":"text","content":"world"`,
		`"type":"done"`,
	}
	for _, w := range wantSubstrings {
		if !strings.Contains(got, w) {
			t.Errorf("output missing %q\nfull:\n%s", w, got)
		}
	}
}

func TestMessagesSend_RejectsBadMetadataJSON(t *testing.T) {
	t.Setenv("NOVA_OS_URL", "http://test.example")
	t.Setenv("NOVA_OS_API_KEY", "k")
	flagURL = ""
	flagAPIKey = ""
	msgEndUser = ""
	msgMetadata = "not-valid-json"
	msgModel = ""

	err := messagesSendCmd.RunE(messagesSendCmd, []string{"a", "b"})
	if err == nil || !strings.Contains(err.Error(), "metadata") {
		t.Fatalf("expected metadata error, got %v", err)
	}
}
