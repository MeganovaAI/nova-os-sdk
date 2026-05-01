package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
	"gopkg.in/yaml.v3"
)

// configFile holds the full structure of ~/.nova-os/config.yaml.
type configFile struct {
	Default  string             `yaml:"default,omitempty"`
	Profiles map[string]Profile `yaml:"profiles,omitempty"`
}

var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Manage profiles in ~/.nova-os/config.yaml",
}

var configListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all profiles",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := readConfigFile()
		if err != nil {
			return err
		}
		if len(cfg.Profiles) == 0 {
			cmd.Println("no profiles configured")
			return nil
		}
		for name, p := range cfg.Profiles {
			marker := ""
			if name == cfg.Default {
				marker = " (default)"
			}
			cmd.Printf("  %s%s\n", name, marker)
			cmd.Printf("    url:         %s\n", p.URL)
			cmd.Printf("    api_key_env: %s\n", p.APIKeyEnv)
			if p.CallbackURL != "" {
				cmd.Printf("    callback_url: %s\n", p.CallbackURL)
			}
		}
		return nil
	},
}

var configGetCmd = &cobra.Command{
	Use:   "get <profile>",
	Short: "Show a single profile",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := readConfigFile()
		if err != nil {
			return err
		}
		p, ok := cfg.Profiles[args[0]]
		if !ok {
			return fmt.Errorf("profile %q not found", args[0])
		}
		cmd.Printf("url:         %s\n", p.URL)
		cmd.Printf("api_key_env: %s\n", p.APIKeyEnv)
		if p.CallbackURL != "" {
			cmd.Printf("callback_url: %s\n", p.CallbackURL)
		}
		return nil
	},
}

var (
	configSetURL         string
	configSetAPIKeyEnv   string
	configSetCallbackURL string
)

var configSetCmd = &cobra.Command{
	Use:   "set <profile>",
	Short: "Create or update a profile",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]
		cfg, err := readConfigFileOrEmpty()
		if err != nil {
			return err
		}
		if cfg.Profiles == nil {
			cfg.Profiles = make(map[string]Profile)
		}
		existing := cfg.Profiles[name]
		if configSetURL != "" {
			existing.URL = configSetURL
		}
		if configSetAPIKeyEnv != "" {
			existing.APIKeyEnv = configSetAPIKeyEnv
		}
		if configSetCallbackURL != "" {
			existing.CallbackURL = configSetCallbackURL
		}
		cfg.Profiles[name] = existing
		// Set as default if it's the only profile or no default is set yet.
		if cfg.Default == "" {
			cfg.Default = name
		}
		if err := writeConfigFile(cfg); err != nil {
			return err
		}
		cmd.Printf("profile %q saved\n", name)
		return nil
	},
}

var configDefaultCmd = &cobra.Command{
	Use:   "default <profile>",
	Short: "Set the default profile",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]
		cfg, err := readConfigFileOrEmpty()
		if err != nil {
			return err
		}
		if _, ok := cfg.Profiles[name]; !ok {
			return fmt.Errorf("profile %q not found; create it first with 'config set'", name)
		}
		cfg.Default = name
		if err := writeConfigFile(cfg); err != nil {
			return err
		}
		cmd.Printf("default profile set to %q\n", name)
		return nil
	},
}

var configDeleteCmd = &cobra.Command{
	Use:   "delete <profile>",
	Short: "Delete a profile",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]
		cfg, err := readConfigFile()
		if err != nil {
			return err
		}
		if _, ok := cfg.Profiles[name]; !ok {
			return fmt.Errorf("profile %q not found", name)
		}
		delete(cfg.Profiles, name)
		if cfg.Default == name {
			cfg.Default = ""
		}
		if err := writeConfigFile(cfg); err != nil {
			return err
		}
		cmd.Printf("profile %q deleted\n", name)
		return nil
	},
}

func init() {
	configSetCmd.Flags().StringVar(&configSetURL, "url", "", "Nova OS server URL")
	configSetCmd.Flags().StringVar(&configSetAPIKeyEnv, "api-key-env", "", "Env var name holding the bearer token")
	configSetCmd.Flags().StringVar(&configSetCallbackURL, "callback-url", "", "Callback URL for partner webhooks")

	configCmd.AddCommand(configListCmd)
	configCmd.AddCommand(configGetCmd)
	configCmd.AddCommand(configSetCmd)
	configCmd.AddCommand(configDefaultCmd)
	configCmd.AddCommand(configDeleteCmd)
	rootCmd.AddCommand(configCmd)
}

// configFilePath returns the path to ~/.nova-os/config.yaml.
func configFilePath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("resolve home dir: %w", err)
	}
	return filepath.Join(home, ".nova-os", "config.yaml"), nil
}

// readConfigFile reads the config file; returns an error if it doesn't exist.
func readConfigFile() (configFile, error) {
	path, err := configFilePath()
	if err != nil {
		return configFile{}, err
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return configFile{}, fmt.Errorf("read config: %w (run 'config set' to create one)", err)
	}
	var cfg configFile
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return configFile{}, fmt.Errorf("parse config: %w", err)
	}
	return cfg, nil
}

// readConfigFileOrEmpty reads the config file; returns an empty configFile if
// it doesn't exist yet (so 'config set' can bootstrap the file).
func readConfigFileOrEmpty() (configFile, error) {
	path, err := configFilePath()
	if err != nil {
		return configFile{}, err
	}
	data, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return configFile{}, nil
	}
	if err != nil {
		return configFile{}, fmt.Errorf("read config: %w", err)
	}
	var cfg configFile
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return configFile{}, fmt.Errorf("parse config: %w", err)
	}
	return cfg, nil
}

// writeConfigFile atomically writes cfg to ~/.nova-os/config.yaml via
// temp-file + rename so partial writes never corrupt the config.
func writeConfigFile(cfg configFile) error {
	path, err := configFilePath()
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return fmt.Errorf("create config dir: %w", err)
	}
	data, err := yaml.Marshal(cfg)
	if err != nil {
		return fmt.Errorf("marshal config: %w", err)
	}
	tmp := path + ".tmp"
	if err := os.WriteFile(tmp, data, 0o600); err != nil {
		return fmt.Errorf("write config: %w", err)
	}
	if err := os.Rename(tmp, path); err != nil {
		return fmt.Errorf("rename config: %w", err)
	}
	return nil
}
