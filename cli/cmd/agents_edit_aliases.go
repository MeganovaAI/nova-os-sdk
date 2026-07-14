// Legacy-alias mapping + once-per-run deprecation warnings for
// `nova-os-cli agents edit` (slice 3 of libraos-sdk#18).
//
// The AgentDef schema declares `x-legacy-aliases` (a legacy → canonical
// field-name map) and `x-deprecation-target` (the version the legacy
// names go away). When an operator's --set / --set-list key matches a
// legacy alias, we auto-map to the canonical field AND emit a warning
// once per run so they update their scripts before the deprecation
// target ships.
//
// Interactive mode doesn't need alias mapping — schema walks expose
// canonical names directly. Aliases only matter for scriptable input
// (--set-list skills=... mapping to tools, --set id=... mapping to
// name, etc.).

package cmd

import (
	"fmt"
	"io"
	"sort"
	"sync"
)

// legacyAliases extracts the schema's x-legacy-aliases extension as a
// canonical (key=legacy, value=canonical) map. Returns nil if the
// extension is absent or malformed — alias handling becomes a no-op,
// not an error.
func legacyAliases(schema map[string]any) map[string]string {
	raw, ok := schema["x-legacy-aliases"]
	if !ok {
		return nil
	}
	m, ok := raw.(map[string]any)
	if !ok {
		// JSON unmarshal lands aliases here; older schemas might have
		// already-typed map[string]string but JSON path produces
		// map[string]any so handle that.
		return nil
	}
	out := make(map[string]string, len(m))
	for k, v := range m {
		if s, ok := v.(string); ok {
			out[k] = s
		}
	}
	if len(out) == 0 {
		return nil
	}
	return out
}

// deprecationTarget extracts x-deprecation-target as a string, or ""
// when absent. Used only to phrase the warning message; doesn't gate
// behavior.
func deprecationTarget(schema map[string]any) string {
	if s, ok := schema["x-deprecation-target"].(string); ok {
		return s
	}
	return ""
}

// aliasWarner emits a once-per-key deprecation warning when a legacy
// alias gets auto-mapped. Same key won't warn twice in the same run.
// The writer is configurable so tests can capture output; production
// callers point it at the cobra command's ErrOrStderr().
type aliasWarner struct {
	out               io.Writer
	deprecationTarget string
	once              sync.Map // map[string]bool
}

func newAliasWarner(out io.Writer, target string) *aliasWarner {
	return &aliasWarner{out: out, deprecationTarget: target}
}

func (w *aliasWarner) warn(legacy, canonical string) {
	if w == nil || w.out == nil {
		return
	}
	if _, seen := w.once.LoadOrStore(legacy, true); seen {
		return
	}
	target := w.deprecationTarget
	if target == "" {
		target = "a future version"
	}
	fmt.Fprintf(w.out,
		"⚠ deprecated field %q auto-mapped to %q; remove before %s.\n",
		legacy, canonical, target,
	)
}

// mapAlias returns (canonical, wasLegacy). If key is already a canonical
// schema field, returns (key, false). If key is a legacy alias, returns
// (canonical, true). If key is neither (typo / unknown), returns
// (key, false) — caller's validateField will reject.
func mapAlias(key string, aliases map[string]string) (string, bool) {
	if aliases == nil {
		return key, false
	}
	if canonical, ok := aliases[key]; ok {
		return canonical, true
	}
	return key, false
}

// listAliases returns the sorted list of legacy alias keys — used
// for --help output and the warning message's "available legacy
// aliases" hint, not for behavior.
func listAliases(aliases map[string]string) []string {
	if aliases == nil {
		return nil
	}
	out := make([]string, 0, len(aliases))
	for k := range aliases {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}
