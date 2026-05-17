package cmd

import (
	"strings"
	"testing"
)

func TestListTemplates_ReturnsSortedSet(t *testing.T) {
	got := listTemplates()
	if len(got) == 0 {
		t.Fatalf("expected at least one builtin template")
	}
	// Spot-check the four slice-3 starter personas are present.
	want := []string{"customer-support", "data-analyst", "dev-assistant", "legal-assistant"}
	if strings.Join(got, ",") != strings.Join(want, ",") {
		t.Errorf("got %v, want %v (must be sorted)", got, want)
	}
}

func TestLoadTemplate_AllBuiltinsParseCleanly(t *testing.T) {
	// Every shipped template must parse — frontmatter delimiters present,
	// YAML valid, body separated. Catches a typo at compile/test time
	// rather than at runtime against an operator.
	for _, name := range listTemplates() {
		tmpl, err := loadTemplate(name)
		if err != nil {
			t.Errorf("template %q failed to load: %v", name, err)
			continue
		}
		if tmpl.frontmatter["name"] != name {
			t.Errorf("template %q frontmatter name=%v should match template id", name, tmpl.frontmatter["name"])
		}
		if tmpl.systemPrompt == "" {
			t.Errorf("template %q has empty system_prompt body", name)
		}
	}
}

func TestLoadTemplate_UnknownReturnsHelpfulError(t *testing.T) {
	_, err := loadTemplate("nonexistent")
	if err == nil {
		t.Fatalf("expected error for unknown template")
	}
	if !strings.Contains(err.Error(), "available:") {
		t.Errorf("error should list available templates; got: %v", err)
	}
	// And should mention at least one real template name.
	if !strings.Contains(err.Error(), "customer-support") {
		t.Errorf("error should include real template names; got: %v", err)
	}
}

func TestParseTemplate_RejectsMissingOpenDelimiter(t *testing.T) {
	_, err := parseTemplate("name: foo\n---\nbody")
	if err == nil || !strings.Contains(err.Error(), "leading frontmatter") {
		t.Errorf("expected leading-delimiter error, got: %v", err)
	}
}

func TestParseTemplate_RejectsMissingCloseDelimiter(t *testing.T) {
	_, err := parseTemplate("---\nname: foo\nbody-with-no-delim")
	if err == nil || !strings.Contains(err.Error(), "closing frontmatter") {
		t.Errorf("expected closing-delimiter error, got: %v", err)
	}
}

func TestApplyTemplate_SeedsBodyWithoutOverridingExisting(t *testing.T) {
	tmpl, err := loadTemplate("customer-support")
	if err != nil {
		t.Fatalf("loadTemplate: %v", err)
	}
	body := map[string]any{
		"name":  "my-custom-name", // pre-existing, must survive
		"model": "anthropic/claude-opus-4-7", // pre-existing override of template's gemini default
	}
	applyTemplate(tmpl, body)

	if body["name"] != "my-custom-name" {
		t.Errorf("pre-existing name was overridden; body=%v", body["name"])
	}
	if body["model"] != "anthropic/claude-opus-4-7" {
		t.Errorf("pre-existing model was overridden by template; body=%v", body["model"])
	}
	// Template fields not in seed should fill in.
	if body["agent_type"] != "persona" {
		t.Errorf("template agent_type not applied; body=%+v", body)
	}
	// system_prompt should come from the template body.
	if body["system_prompt"] == nil {
		t.Errorf("system_prompt should be populated from template body")
	}
}

func TestApplyTemplate_DoesNotOverrideExistingSystemPrompt(t *testing.T) {
	tmpl, err := loadTemplate("legal-assistant")
	if err != nil {
		t.Fatalf("loadTemplate: %v", err)
	}
	body := map[string]any{"system_prompt": "my own custom prompt"}
	applyTemplate(tmpl, body)
	if body["system_prompt"] != "my own custom prompt" {
		t.Errorf("template overrode existing system_prompt; got: %v", body["system_prompt"])
	}
}
