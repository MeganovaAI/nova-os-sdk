package cmd

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"

	"github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

// CLIVersion is the published nova-os-cli version.
// SpecVersion stays in lockstep with the OpenAPI version pinned in the spec file.
// CLIVersion, commit, and buildDate are overridable via -ldflags from goreleaser.
var (
	CLIVersion  = "0.1.0-alpha.1" // overridable via -ldflags from goreleaser
	SpecVersion = "1.0.0-alpha.1"
	commit      = "dev"
	buildDate   = "unknown"
)

var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print CLI + OpenAPI spec versions",
	RunE: func(cmd *cobra.Command, args []string) error {
		hash := readSpecHash()

		// Pin the generated-client type so a broken codegen breaks at
		// compile time, not runtime.
		_ = (*client.Client)(nil)

		if flagJSON {
			out := map[string]string{
				"cli_version":  CLIVersion,
				"spec_version": SpecVersion,
				"spec_hash":    hash,
				"commit":       commit,
				"build_date":   buildDate,
			}
			b, _ := json.Marshal(out)
			cmd.Println(string(b))
			return nil
		}
		cmd.Printf("nova-os-cli %s (commit %s, built %s)\n", CLIVersion, commit, buildDate)
		cmd.Printf("openapi spec %s (hash %s)\n", SpecVersion, hash)
		return nil
	},
}

func init() {
	rootCmd.AddCommand(versionCmd)
}

// readSpecHash returns the canonical OpenAPI spec hash. We try a few
// locations in order so the binary works whether run from the repo root,
// from cli/, or as a packaged binary that ships the hash file alongside.
// Returns "unknown" on miss — version still prints cleanly.
func readSpecHash() string {
	candidates := []string{
		"openapi/openapi-hash.txt",
		"../openapi/openapi-hash.txt",
		"../../openapi/openapi-hash.txt",
	}
	for _, p := range candidates {
		if data, err := os.ReadFile(p); err == nil {
			return strings.TrimSpace(string(data))
		}
	}
	exe, err := os.Executable()
	if err == nil {
		near := filepath.Join(filepath.Dir(exe), "openapi-hash.txt")
		if data, err := os.ReadFile(near); err == nil {
			return strings.TrimSpace(string(data))
		}
	}
	return "unknown"
}
