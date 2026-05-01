// Package validate runs offline checks against the YAML frontmatter
// of agent + employee markdown files. Each rule is a pure function:
// given the parsed doc + the file path, return zero or more Issues.
// Rule chain runs all rules on every file — we want the full report,
// not first-failure.
package validate

import (
	"fmt"
	"net/url"
	"regexp"
)

// Issue is one validation finding. Path is the file path; Field is
// a JSON-pointer-ish locator within the doc; Message is the human-
// readable explanation.
type Issue struct {
	Path    string `json:"path"`
	Field   string `json:"field"`
	Message string `json:"message"`
}

func (i Issue) String() string {
	if i.Field != "" {
		return fmt.Sprintf("%s [%s]: %s", i.Path, i.Field, i.Message)
	}
	return fmt.Sprintf("%s: %s", i.Path, i.Message)
}

// modelShapeRE matches "<vendor>/<model>" — same regex shape as the
// validateModelShape gate in nova-os.
var modelShapeRE = regexp.MustCompile(`^[a-z0-9_.-]+/[A-Za-z0-9_.:-]+$`)

// RuleModelShape verifies model_config.{answer,planner,skill}.primary
// fields use <vendor>/<model> form. Empty fields are skipped — empty
// is "fall through to higher-cascade tier", which is fine.
func RuleModelShape(doc map[string]any, path string) []Issue {
	cfg, ok := doc["model_config"].(map[string]any)
	if !ok {
		return nil
	}
	var issues []Issue
	for _, slot := range []string{"answer", "planner", "skill"} {
		s, ok := cfg[slot].(map[string]any)
		if !ok {
			continue
		}
		primary, ok := s["primary"].(string)
		if !ok || primary == "" {
			continue
		}
		if !modelShapeRE.MatchString(primary) {
			issues = append(issues, Issue{
				Path:    path,
				Field:   fmt.Sprintf("model_config.%s.primary", slot),
				Message: fmt.Sprintf("model %q must be <vendor>/<model> shape (e.g. anthropic/claude-opus-4-7)", primary),
			})
		}
	}
	return issues
}

// RuleVertexSchema walks every custom_tools[].input_schema looking for
// `type: array` without `items` — the deterministic class of bugs that
// surfaces as a misleading 400 when Gemini routes through Vertex AI.
func RuleVertexSchema(doc map[string]any, path string) []Issue {
	tools, ok := doc["custom_tools"].([]any)
	if !ok {
		return nil
	}
	var issues []Issue
	for i, raw := range tools {
		tool, ok := raw.(map[string]any)
		if !ok {
			continue
		}
		schema, ok := tool["input_schema"].(map[string]any)
		if !ok {
			continue
		}
		name, _ := tool["name"].(string)
		basePath := fmt.Sprintf("custom_tools[%d:%s].input_schema", i, name)
		issues = append(issues, walkSchema(schema, basePath, path)...)
	}
	return issues
}

// walkSchema recurses through a JSON Schema-like map and reports any
// `type: array` node missing `items`.
func walkSchema(schema map[string]any, fieldPath, filePath string) []Issue {
	var issues []Issue

	if t, ok := schema["type"].(string); ok && t == "array" {
		if _, hasItems := schema["items"]; !hasItems {
			issues = append(issues, Issue{
				Path:    filePath,
				Field:   fieldPath,
				Message: "type:array requires `items` schema (Vertex AI strictly enforces this — missing items causes a misleading 400 Connection error in production)",
			})
		}
	}

	// Recurse into properties (object schemas).
	if props, ok := schema["properties"].(map[string]any); ok {
		for key, val := range props {
			if sub, ok := val.(map[string]any); ok {
				issues = append(issues, walkSchema(sub, fmt.Sprintf("%s.properties.%s", fieldPath, key), filePath)...)
			}
		}
	}

	// Recurse into items (when present and itself an object schema).
	if items, ok := schema["items"].(map[string]any); ok {
		issues = append(issues, walkSchema(items, fieldPath+".items", filePath)...)
	}

	// Recurse into oneOf/anyOf/allOf composition.
	for _, key := range []string{"oneOf", "anyOf", "allOf"} {
		if arr, ok := schema[key].([]any); ok {
			for i, val := range arr {
				if sub, ok := val.(map[string]any); ok {
					issues = append(issues, walkSchema(sub, fmt.Sprintf("%s.%s[%d]", fieldPath, key, i), filePath)...)
				}
			}
		}
	}

	return issues
}

// RuleCallbackURL — agent.callback.url and any custom_tools[].callback.url
// must be HTTPS, except for localhost (dev convenience).
func RuleCallbackURL(doc map[string]any, path string) []Issue {
	var issues []Issue

	check := func(u, fieldPath string) {
		parsed, err := url.Parse(u)
		if err != nil {
			issues = append(issues, Issue{Path: path, Field: fieldPath, Message: fmt.Sprintf("invalid URL: %v", err)})
			return
		}
		host := parsed.Hostname()
		if parsed.Scheme == "https" {
			return
		}
		if parsed.Scheme == "http" && (host == "localhost" || host == "127.0.0.1" || host == "::1") {
			return
		}
		issues = append(issues, Issue{
			Path:    path,
			Field:   fieldPath,
			Message: fmt.Sprintf("callback URL must be HTTPS (got %q); only localhost is allowed over HTTP for dev", u),
		})
	}

	if cb, ok := doc["callback"].(map[string]any); ok {
		if u, ok := cb["url"].(string); ok && u != "" {
			check(u, "callback.url")
		}
	}
	if tools, ok := doc["custom_tools"].([]any); ok {
		for i, raw := range tools {
			tool, ok := raw.(map[string]any)
			if !ok {
				continue
			}
			cb, ok := tool["callback"].(map[string]any)
			if !ok {
				continue
			}
			if u, ok := cb["url"].(string); ok && u != "" {
				name, _ := tool["name"].(string)
				check(u, fmt.Sprintf("custom_tools[%d:%s].callback.url", i, name))
			}
		}
	}
	return issues
}

// RuleOwnerEmployeeRef — when an agent declares `owner_employee: <id>`,
// the validator can only check refs WITHIN the folder being validated.
// Server-side employees aren't visible offline. Pass empty `employees`
// to skip; pass a populated set to validate.
func RuleOwnerEmployeeRef(doc map[string]any, path string, employees map[string]bool) []Issue {
	if len(employees) == 0 {
		return nil
	}
	owner, ok := doc["owner_employee"].(string)
	if !ok || owner == "" {
		return nil
	}
	if !employees[owner] {
		return []Issue{{
			Path:    path,
			Field:   "owner_employee",
			Message: fmt.Sprintf("references unknown employee %q (not present in the validated folder)", owner),
		}}
	}
	return nil
}

// AllRules is the chain `validate` runs on every agent doc. Employee
// docs use a subset (no owner_employee, no custom_tools — though we
// run the full chain because the rules return zero issues on missing
// fields).
var AllRules = []func(map[string]any, string) []Issue{
	RuleModelShape,
	RuleVertexSchema,
	RuleCallbackURL,
}
