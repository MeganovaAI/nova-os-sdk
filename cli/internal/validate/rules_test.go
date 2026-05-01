package validate

import (
	"testing"
)

func TestRuleModelShape_AcceptsValid(t *testing.T) {
	doc := map[string]any{
		"model_config": map[string]any{
			"answer": map[string]any{"primary": "anthropic/claude-opus-4-7"},
		},
	}
	issues := RuleModelShape(doc, "x.md")
	if len(issues) != 0 {
		t.Fatalf("expected no issues, got %v", issues)
	}
}

func TestRuleModelShape_RejectsBareName(t *testing.T) {
	doc := map[string]any{
		"model_config": map[string]any{
			"answer": map[string]any{"primary": "claude-opus-4-7"},
		},
	}
	issues := RuleModelShape(doc, "x.md")
	if len(issues) != 1 {
		t.Fatalf("expected 1 issue, got %d: %v", len(issues), issues)
	}
	if issues[0].Field == "" {
		t.Fatal("issue field empty")
	}
}

func TestRuleVertexSchema_AcceptsArrayWithItems(t *testing.T) {
	doc := map[string]any{
		"custom_tools": []any{
			map[string]any{
				"name": "fetch_invoice",
				"input_schema": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"results": map[string]any{
							"type":  "array",
							"items": map[string]any{"type": "string"},
						},
					},
				},
			},
		},
	}
	issues := RuleVertexSchema(doc, "x.md")
	if len(issues) != 0 {
		t.Fatalf("expected no issues, got %v", issues)
	}
}

func TestRuleVertexSchema_RejectsArrayWithoutItems(t *testing.T) {
	doc := map[string]any{
		"custom_tools": []any{
			map[string]any{
				"name": "broken_tool",
				"input_schema": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"results": map[string]any{
							"type": "array",
							// items is MISSING — this is the deterministic bug
						},
					},
				},
			},
		},
	}
	issues := RuleVertexSchema(doc, "x.md")
	if len(issues) != 1 {
		t.Fatalf("expected 1 issue, got %d", len(issues))
	}
	if issues[0].Field == "" || issues[0].Message == "" {
		t.Fatalf("issue missing field or message: %+v", issues[0])
	}
}

func TestRuleVertexSchema_RejectsDeeplyNestedArrayWithoutItems(t *testing.T) {
	// Recursion depth 3 — array nested under multiple objects.
	doc := map[string]any{
		"custom_tools": []any{
			map[string]any{
				"name": "deeply_nested",
				"input_schema": map[string]any{
					"type": "object",
					"properties": map[string]any{
						"outer": map[string]any{
							"type": "object",
							"properties": map[string]any{
								"middle": map[string]any{
									"type": "object",
									"properties": map[string]any{
										"inner": map[string]any{
											"type": "array",
											// items missing
										},
									},
								},
							},
						},
					},
				},
			},
		},
	}
	issues := RuleVertexSchema(doc, "x.md")
	if len(issues) != 1 {
		t.Fatalf("expected 1 issue (recursive walk), got %d", len(issues))
	}
}

func TestRuleCallbackURL_AcceptsHTTPS(t *testing.T) {
	doc := map[string]any{
		"callback": map[string]any{"url": "https://partner.example.com/cb"},
	}
	issues := RuleCallbackURL(doc, "x.md")
	if len(issues) != 0 {
		t.Fatalf("expected no issues, got %v", issues)
	}
}

func TestRuleCallbackURL_AcceptsLocalhost(t *testing.T) {
	for _, u := range []string{"http://localhost:8080/cb", "http://127.0.0.1:8080/cb"} {
		doc := map[string]any{"callback": map[string]any{"url": u}}
		if issues := RuleCallbackURL(doc, "x.md"); len(issues) != 0 {
			t.Errorf("localhost %q should be allowed, got %v", u, issues)
		}
	}
}

func TestRuleCallbackURL_RejectsHTTP(t *testing.T) {
	doc := map[string]any{
		"callback": map[string]any{"url": "http://partner.example.com/cb"},
	}
	issues := RuleCallbackURL(doc, "x.md")
	if len(issues) != 1 {
		t.Fatalf("expected 1 issue, got %d", len(issues))
	}
}
