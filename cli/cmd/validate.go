package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
	"gopkg.in/yaml.v3"

	"github.com/MeganovaAI/nova-os-sdk/cli/internal/frontmatter"
	"github.com/MeganovaAI/nova-os-sdk/cli/internal/validate"
)

var validateCmd = &cobra.Command{
	Use:   "validate <dir>",
	Short: "Offline validation of agent + employee markdown frontmatter",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		dir := args[0]

		empDocs, err := loadDocs(filepath.Join(dir, "employees"))
		if err != nil {
			return err
		}
		agentDocs, err := loadDocs(filepath.Join(dir, "agents"))
		if err != nil {
			return err
		}

		// Build employee-id set for cross-ref checking on agents.
		empIDs := map[string]bool{}
		for _, doc := range empDocs {
			if id, ok := doc["id"].(string); ok && id != "" {
				empIDs[id] = true
			}
		}

		var allIssues []validate.Issue
		for path, doc := range empDocs {
			for _, rule := range validate.AllRules {
				allIssues = append(allIssues, rule(doc, path)...)
			}
		}
		for path, doc := range agentDocs {
			for _, rule := range validate.AllRules {
				allIssues = append(allIssues, rule(doc, path)...)
			}
			allIssues = append(allIssues, validate.RuleOwnerEmployeeRef(doc, path, empIDs)...)
		}

		if flagJSON {
			b, _ := json.MarshalIndent(map[string]any{
				"issues":         allIssues,
				"employee_count": len(empDocs),
				"agent_count":    len(agentDocs),
			}, "", "  ")
			cmd.Println(string(b))
		} else {
			cmd.Printf("validated %d employee(s), %d agent(s)\n", len(empDocs), len(agentDocs))
			if len(allIssues) == 0 {
				cmd.Println("OK — no issues")
			} else {
				cmd.Printf("FOUND %d issue(s):\n", len(allIssues))
				for _, iss := range allIssues {
					cmd.Println("  " + iss.String())
				}
			}
		}
		if len(allIssues) > 0 {
			return fmt.Errorf("validation failed: %d issue(s)", len(allIssues))
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(validateCmd)
}

// loadDocs reads every *.md under dir, splits frontmatter, parses as
// generic map[string]any. Missing dir is OK (returns empty map). Per-
// file parse errors are returned as a wrapped error WITH any successful
// loads still in the map; caller decides whether partial success matters.
func loadDocs(dir string) (map[string]map[string]any, error) {
	out := map[string]map[string]any{}
	entries, err := os.ReadDir(dir)
	if err != nil {
		if os.IsNotExist(err) {
			return out, nil
		}
		return out, fmt.Errorf("read %s: %w", dir, err)
	}
	var errs []string
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
			continue
		}
		path := filepath.Join(dir, e.Name())
		data, err := os.ReadFile(path)
		if err != nil {
			errs = append(errs, fmt.Sprintf("%s: %v", path, err))
			continue
		}
		fm, _, err := frontmatter.Split(data)
		if err != nil {
			errs = append(errs, fmt.Sprintf("%s: %v", path, err))
			continue
		}
		var doc map[string]any
		if err := yaml.Unmarshal(fm, &doc); err != nil {
			errs = append(errs, fmt.Sprintf("%s: yaml: %v", path, err))
			continue
		}
		out[path] = doc
	}
	if len(errs) > 0 {
		return out, fmt.Errorf("%d parse error(s): %s", len(errs), strings.Join(errs, "; "))
	}
	return out, nil
}
