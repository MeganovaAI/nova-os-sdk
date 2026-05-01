package frontmatter

import (
	"strings"
	"testing"
)

func TestSplit_BasicFrontmatter(t *testing.T) {
	input := `---
id: frontdesk
display_name: Front Desk
---

Body text here.
`
	fm, body, err := Split([]byte(input))
	if err != nil {
		t.Fatalf("Split: %v", err)
	}
	if !strings.Contains(string(fm), "id: frontdesk") {
		t.Fatalf("frontmatter missing id: %q", string(fm))
	}
	if !strings.Contains(string(body), "Body text here.") {
		t.Fatalf("body missing: %q", string(body))
	}
}

func TestSplit_RejectsMissingFence(t *testing.T) {
	_, _, err := Split([]byte("no frontmatter here"))
	if err == nil {
		t.Fatal("expected error on missing opening fence")
	}
}

func TestSplit_RejectsUnclosedFence(t *testing.T) {
	_, _, err := Split([]byte("---\nid: x\nbody no closing"))
	if err == nil {
		t.Fatal("expected error on missing closing fence")
	}
}

func TestSplit_HandlesCRLF(t *testing.T) {
	input := "---\r\nid: x\r\n---\r\nbody\r\n"
	_, _, err := Split([]byte(input))
	if err != nil {
		t.Fatalf("Split with CRLF: %v", err)
	}
}
