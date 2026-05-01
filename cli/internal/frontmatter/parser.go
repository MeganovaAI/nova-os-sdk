// Package frontmatter splits Claude-Agent-SDK-style markdown into
// a YAML frontmatter region and a body region. Mirrors the Go-side
// implementation that ships in the nova-os corporate package, so the
// frontmatter the CLI parses is bit-for-bit what the server parses.
package frontmatter

import (
	"bytes"
	"fmt"
)

const fence = "---"

// Split returns (frontmatter, body, err). Frontmatter is the YAML
// content between the two `---` lines (no fences). Body is the
// trailing markdown content. Both empty if file isn't fenced; error
// is returned in that case.
func Split(data []byte) (fm, body []byte, err error) {
	// Accept LF and CRLF openers.
	openLF := []byte(fence + "\n")
	openCRLF := []byte(fence + "\r\n")

	if !bytes.HasPrefix(data, openLF) && !bytes.HasPrefix(data, openCRLF) {
		return nil, nil, fmt.Errorf("file does not start with %q", fence)
	}
	rest := data[len(fence):]
	for len(rest) > 0 && (rest[0] == '\n' || rest[0] == '\r') {
		rest = rest[1:]
	}
	closer := []byte("\n" + fence)
	idx := bytes.Index(rest, closer)
	if idx < 0 {
		return nil, nil, fmt.Errorf("missing closing %q", fence)
	}
	fm = rest[:idx]
	body = rest[idx+len(closer):]
	for len(body) > 0 && (body[0] == '\n' || body[0] == '\r') {
		body = body[1:]
	}
	return fm, body, nil
}
