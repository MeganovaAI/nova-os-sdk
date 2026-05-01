package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/fsnotify/fsnotify"
	"github.com/spf13/cobra"
	"gopkg.in/yaml.v3"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
	"github.com/MeganovaAI/nova-os-sdk/cli/internal/frontmatter"
)

var (
	syncFlagWatch bool
	syncFlagDry   bool
)

var syncCmd = &cobra.Command{
	Use:   "sync <dir>",
	Short: "Diff folder against server, push changes (one-shot or --watch)",
	Long: `Walks <dir>/employees/*.md and <dir>/agents/*.md, computes a sync plan
(creates/updates), and executes it against the configured server.

By default this is forward-only — server-side resources missing from the
folder are NOT deleted. Add a --prune flag (when implemented) for destructive
sync.`,
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		dir := args[0]
		c, err := newSyncClient()
		if err != nil {
			return err
		}
		if syncFlagWatch {
			return runWatch(cmd, c, dir)
		}
		_, err = runOnce(cmd, c, dir)
		return err
	},
}

func init() {
	syncCmd.Flags().BoolVar(&syncFlagWatch, "watch", false, "Re-run sync on filesystem changes (300ms debounce)")
	syncCmd.Flags().BoolVar(&syncFlagDry, "dry-run", false, "Print the plan without executing")
	rootCmd.AddCommand(syncCmd)
}

// SyncResult tallies what happened in one run.
type SyncResult struct {
	EmployeesCreated int
	EmployeesUpdated int
	AgentsCreated    int
	AgentsUpdated    int
	NoOps            int
	Errors           []string
}

func runOnce(cmd *cobra.Command, c *gen.ClientWithResponses, dir string) (SyncResult, error) {
	ctx := context.Background()
	res := SyncResult{}

	empDir := filepath.Join(dir, "employees")
	if entries, err := os.ReadDir(empDir); err == nil {
		for _, e := range entries {
			if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
				continue
			}
			path := filepath.Join(empDir, e.Name())
			if err := syncEmployee(ctx, cmd, c, path, &res); err != nil {
				res.Errors = append(res.Errors, fmt.Sprintf("%s: %v", path, err))
			}
		}
	}

	agentDir := filepath.Join(dir, "agents")
	if entries, err := os.ReadDir(agentDir); err == nil {
		for _, e := range entries {
			if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
				continue
			}
			path := filepath.Join(agentDir, e.Name())
			if err := syncAgent(ctx, cmd, c, path, &res); err != nil {
				res.Errors = append(res.Errors, fmt.Sprintf("%s: %v", path, err))
			}
		}
	}

	cmd.Printf("sync: employees +%d ~%d  agents +%d ~%d  no-op %d  errors %d\n",
		res.EmployeesCreated, res.EmployeesUpdated,
		res.AgentsCreated, res.AgentsUpdated,
		res.NoOps, len(res.Errors))
	for _, e := range res.Errors {
		cmd.PrintErrln("  ERR " + e)
	}
	if len(res.Errors) > 0 {
		return res, fmt.Errorf("%d sync error(s)", len(res.Errors))
	}
	return res, nil
}

func syncEmployee(ctx context.Context, cmd *cobra.Command, c *gen.ClientWithResponses, path string, res *SyncResult) error {
	fm, err := loadFrontmatter(path)
	if err != nil {
		return err
	}
	id, _ := fm["id"].(string)
	if id == "" {
		return fmt.Errorf("missing id")
	}

	// GET — does it exist?
	getResp, err := c.GetEmployeeWithResponse(ctx, id)
	if err != nil {
		return err
	}

	if getResp.StatusCode() == http.StatusNotFound {
		if syncFlagDry {
			cmd.Printf("  [dry-run] CREATE employee %s\n", id)
			res.NoOps++
			return nil
		}
		body, err := buildEmployeeCreateBody(fm)
		if err != nil {
			return err
		}
		createResp, err := c.CreateEmployeeWithResponse(ctx, body)
		if err != nil {
			return err
		}
		if createResp.StatusCode() >= 300 {
			return fmt.Errorf("create returned %d", createResp.StatusCode())
		}
		cmd.Printf("  CREATED employee %s\n", id)
		res.EmployeesCreated++
		return nil
	}

	// Exists — diff and PUT if changed.
	if getResp.JSON200 == nil {
		return fmt.Errorf("get returned %d (no JSON200)", getResp.StatusCode())
	}
	if equivalent(fm, getResp.JSON200) {
		res.NoOps++
		return nil
	}
	if syncFlagDry {
		cmd.Printf("  [dry-run] UPDATE employee %s\n", id)
		res.NoOps++
		return nil
	}
	body, err := buildEmployeeUpdateBody(fm)
	if err != nil {
		return err
	}
	putResp, err := c.UpdateEmployeeWithResponse(ctx, id, body)
	if err != nil {
		return err
	}
	if putResp.StatusCode() >= 300 {
		return fmt.Errorf("update returned %d", putResp.StatusCode())
	}
	cmd.Printf("  UPDATED employee %s\n", id)
	res.EmployeesUpdated++
	return nil
}

// agentID extracts the agent identifier from the frontmatter, checking
// agent_id → id → name in that order. Agent markdown files can declare
// their ID under any of these keys depending on author convention.
func agentID(fm map[string]any) string {
	for _, key := range []string{"agent_id", "id", "name"} {
		if v, ok := fm[key].(string); ok && v != "" {
			return v
		}
	}
	return ""
}

func syncAgent(ctx context.Context, cmd *cobra.Command, c *gen.ClientWithResponses, path string, res *SyncResult) error {
	fm, err := loadFrontmatter(path)
	if err != nil {
		return err
	}
	id := agentID(fm)
	if id == "" {
		return fmt.Errorf("missing agent id (no agent_id, id, or name field)")
	}

	// GET — does it exist?
	getResp, err := c.GetAgentWithResponse(ctx, id)
	if err != nil {
		return err
	}

	if getResp.StatusCode() == http.StatusNotFound {
		if syncFlagDry {
			cmd.Printf("  [dry-run] CREATE agent %s\n", id)
			res.NoOps++
			return nil
		}
		body, err := buildAgentCreateBody(fm)
		if err != nil {
			return err
		}
		createResp, err := c.CreateAgentWithResponse(ctx, body)
		if err != nil {
			return err
		}
		if createResp.StatusCode() >= 300 {
			return fmt.Errorf("create returned %d", createResp.StatusCode())
		}
		cmd.Printf("  CREATED agent %s\n", id)
		res.AgentsCreated++
		return nil
	}

	// Exists — diff and PUT if changed.
	if getResp.JSON200 == nil {
		return fmt.Errorf("get returned %d (no JSON200)", getResp.StatusCode())
	}
	if equivalent(fm, getResp.JSON200) {
		res.NoOps++
		return nil
	}
	if syncFlagDry {
		cmd.Printf("  [dry-run] UPDATE agent %s\n", id)
		res.NoOps++
		return nil
	}
	body, err := buildAgentUpdateBody(fm)
	if err != nil {
		return err
	}
	putResp, err := c.UpdateAgentWithResponse(ctx, id, body)
	if err != nil {
		return err
	}
	if putResp.StatusCode() >= 300 {
		return fmt.Errorf("update returned %d", putResp.StatusCode())
	}
	cmd.Printf("  UPDATED agent %s\n", id)
	res.AgentsUpdated++
	return nil
}

// loadFrontmatter reads and parses a markdown file's YAML frontmatter.
func loadFrontmatter(path string) (map[string]any, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	fm, _, err := frontmatter.Split(data)
	if err != nil {
		return nil, err
	}
	var doc map[string]any
	if err := yaml.Unmarshal(fm, &doc); err != nil {
		return nil, err
	}
	return doc, nil
}

func buildEmployeeCreateBody(fm map[string]any) (gen.CreateEmployeeJSONRequestBody, error) {
	jsonBytes, err := json.Marshal(fm)
	if err != nil {
		return gen.CreateEmployeeJSONRequestBody{}, err
	}
	var body gen.CreateEmployeeJSONRequestBody
	if err := json.Unmarshal(jsonBytes, &body); err != nil {
		return gen.CreateEmployeeJSONRequestBody{}, fmt.Errorf("frontmatter doesn't fit the API schema: %w", err)
	}
	return body, nil
}

func buildEmployeeUpdateBody(fm map[string]any) (gen.UpdateEmployeeJSONRequestBody, error) {
	jsonBytes, err := json.Marshal(fm)
	if err != nil {
		return gen.UpdateEmployeeJSONRequestBody{}, err
	}
	var body gen.UpdateEmployeeJSONRequestBody
	if err := json.Unmarshal(jsonBytes, &body); err != nil {
		return gen.UpdateEmployeeJSONRequestBody{}, err
	}
	return body, nil
}

func buildAgentCreateBody(fm map[string]any) (gen.CreateAgentJSONRequestBody, error) {
	jsonBytes, err := json.Marshal(fm)
	if err != nil {
		return gen.CreateAgentJSONRequestBody{}, err
	}
	var body gen.CreateAgentJSONRequestBody
	if err := json.Unmarshal(jsonBytes, &body); err != nil {
		return gen.CreateAgentJSONRequestBody{}, fmt.Errorf("frontmatter doesn't fit the API schema: %w", err)
	}
	return body, nil
}

func buildAgentUpdateBody(fm map[string]any) (gen.UpdateAgentJSONRequestBody, error) {
	jsonBytes, err := json.Marshal(fm)
	if err != nil {
		return gen.UpdateAgentJSONRequestBody{}, err
	}
	var body gen.UpdateAgentJSONRequestBody
	if err := json.Unmarshal(jsonBytes, &body); err != nil {
		return gen.UpdateAgentJSONRequestBody{}, err
	}
	return body, nil
}

// equivalent compares the local frontmatter against the server-side
// resource by round-tripping both through JSON and string-comparing.
// Read-only fields (created_at, updated_at, source_path, storage_path,
// agents, skills, loaded_at) are stripped before compare so they don't
// falsely trigger an update.
func equivalent(local map[string]any, remote any) bool {
	a, _ := json.Marshal(stripReadOnly(local))

	rj, _ := json.Marshal(remote)
	var rmap map[string]any
	_ = json.Unmarshal(rj, &rmap)
	b, _ := json.Marshal(stripReadOnly(rmap))

	return string(a) == string(b)
}

// stripReadOnly returns a copy of doc with server-controlled fields removed.
func stripReadOnly(doc map[string]any) map[string]any {
	out := map[string]any{}
	for k, v := range doc {
		switch k {
		case "created_at", "updated_at", "source_path", "storage_path",
			"agents", "skills", "loaded_at":
			continue
		}
		out[k] = v
	}
	return out
}

// newSyncClient is a thin wrapper around the generated NewClientWithResponses.
func newSyncClient() (*gen.ClientWithResponses, error) {
	url, apiKey, err := globalConfig()
	if err != nil {
		return nil, err
	}
	return gen.NewClientWithResponses(url, gen.WithRequestEditorFn(
		func(_ context.Context, req *http.Request) error {
			req.Header.Set("Authorization", "Bearer "+apiKey)
			return nil
		},
	))
}

// watchDebounce is the quiescence window before a batch of filesystem
// events triggers a sync run.
const watchDebounce = 300 * time.Millisecond

func runWatch(cmd *cobra.Command, c *gen.ClientWithResponses, dir string) error {
	cmd.Printf("watching %s — Ctrl-C to stop\n", dir)

	// Initial sync.
	if _, err := runOnce(cmd, c, dir); err != nil {
		cmd.PrintErrln("  initial sync had errors; continuing to watch")
	}

	w, err := fsnotify.NewWatcher()
	if err != nil {
		return fmt.Errorf("fsnotify: %w", err)
	}
	defer w.Close()

	// Watch both subdirs (tolerate missing — empty trees are fine).
	for _, sub := range []string{"employees", "agents"} {
		path := filepath.Join(dir, sub)
		if _, err := os.Stat(path); err == nil {
			if err := w.Add(path); err != nil {
				return fmt.Errorf("watch %s: %w", path, err)
			}
		}
	}

	debounceTimer := time.NewTimer(time.Hour) // start with a long no-op
	debounceTimer.Stop()
	pending := false

	for {
		select {
		case ev, ok := <-w.Events:
			if !ok {
				return nil
			}
			// Filter to .md files — avoids editor swap files (.swp, ~, etc.)
			if !strings.HasSuffix(ev.Name, ".md") {
				continue
			}
			pending = true
			debounceTimer.Reset(watchDebounce)
		case err, ok := <-w.Errors:
			if !ok {
				return nil
			}
			cmd.PrintErrf("  watch error: %v\n", err)
		case <-debounceTimer.C:
			if !pending {
				continue
			}
			pending = false
			if _, err := runOnce(cmd, c, dir); err != nil {
				cmd.PrintErrf("  sync had errors: %v\n", err)
			}
		}
	}
}
