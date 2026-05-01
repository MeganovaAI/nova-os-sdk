package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"text/tabwriter"

	"github.com/spf13/cobra"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

var agentsCmd = &cobra.Command{
	Use:   "agents",
	Short: "Manage agents (/v1/managed/agents)",
}

var agentsOwnerEmployee string

var agentsListCmd = &cobra.Command{
	Use:   "list",
	Short: "List agents",
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		params := &gen.ListAgentsParams{}
		if agentsOwnerEmployee != "" {
			params.OwnerEmployee = &agentsOwnerEmployee
		}
		resp, err := c.ListAgentsWithResponse(ctx, params)
		if err != nil {
			return fmt.Errorf("list agents: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printAgentList(cmd, resp.JSON200)
	},
}

var agentsGetCmd = &cobra.Command{
	Use:   "get <id>",
	Short: "Get an agent by ID",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.GetAgentWithResponse(ctx, args[0])
		if err != nil {
			return fmt.Errorf("get agent: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printAgent(cmd, resp.JSON200)
	},
}

var agentsCreateFile string

var agentsCreateCmd = &cobra.Command{
	Use:   "create -f <file.json>",
	Short: "Create an agent from a JSON definition file",
	RunE: func(cmd *cobra.Command, args []string) error {
		if agentsCreateFile == "" {
			return fmt.Errorf("--file/-f is required")
		}
		data, err := os.ReadFile(agentsCreateFile)
		if err != nil {
			return fmt.Errorf("read file: %w", err)
		}
		var body gen.CreateAgentJSONRequestBody
		if err := json.Unmarshal(data, &body); err != nil {
			return fmt.Errorf("parse JSON: %w", err)
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.CreateAgentWithResponse(ctx, body)
		if err != nil {
			return fmt.Errorf("create agent: %w", err)
		}
		if resp.JSON201 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printAgent(cmd, resp.JSON201)
	},
}

var agentsUpdateFile string

var agentsUpdateCmd = &cobra.Command{
	Use:   "update <id> -f <file.json>",
	Short: "Update an agent from a JSON patch file",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		if agentsUpdateFile == "" {
			return fmt.Errorf("--file/-f is required")
		}
		data, err := os.ReadFile(agentsUpdateFile)
		if err != nil {
			return fmt.Errorf("read file: %w", err)
		}
		var body gen.UpdateAgentJSONRequestBody
		if err := json.Unmarshal(data, &body); err != nil {
			return fmt.Errorf("parse JSON: %w", err)
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.UpdateAgentWithResponse(ctx, args[0], body)
		if err != nil {
			return fmt.Errorf("update agent: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printAgent(cmd, resp.JSON200)
	},
}

var agentsDeleteCmd = &cobra.Command{
	Use:   "delete <id>",
	Short: "Delete an agent",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.DeleteAgentWithResponse(ctx, args[0])
		if err != nil {
			return fmt.Errorf("delete agent: %w", err)
		}
		if resp.StatusCode() >= 300 {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		cmd.Printf("deleted agent %s\n", args[0])
		return nil
	},
}

func init() {
	agentsListCmd.Flags().StringVar(&agentsOwnerEmployee, "owner-employee", "", "Filter to agents owned by this employee")
	agentsCreateCmd.Flags().StringVarP(&agentsCreateFile, "file", "f", "", "Path to JSON definition file")
	agentsUpdateCmd.Flags().StringVarP(&agentsUpdateFile, "file", "f", "", "Path to JSON patch file")

	agentsCmd.AddCommand(agentsListCmd)
	agentsCmd.AddCommand(agentsGetCmd)
	agentsCmd.AddCommand(agentsCreateCmd)
	agentsCmd.AddCommand(agentsUpdateCmd)
	agentsCmd.AddCommand(agentsDeleteCmd)
	rootCmd.AddCommand(agentsCmd)
}

func printAgentList(cmd *cobra.Command, list *gen.AgentList) error {
	if flagJSON {
		b, _ := json.MarshalIndent(list, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	tw := tabwriter.NewWriter(cmd.OutOrStdout(), 0, 0, 2, ' ', 0)
	defer tw.Flush()
	fmt.Fprintln(tw, "ID\tTYPE\tOWNER EMPLOYEE")
	for _, a := range list.Data {
		owner := ""
		if a.OwnerEmployee != nil {
			owner = *a.OwnerEmployee
		}
		fmt.Fprintf(tw, "%s\t%s\t%s\n", a.Id, string(a.Type), owner)
	}
	return nil
}

func printAgent(cmd *cobra.Command, a *gen.Agent) error {
	if flagJSON {
		b, _ := json.MarshalIndent(a, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	owner := ""
	if a.OwnerEmployee != nil {
		owner = *a.OwnerEmployee
	}
	cmd.Printf("ID:    %s\n", a.Id)
	cmd.Printf("Type:  %s\n", string(a.Type))
	cmd.Printf("Owner: %s\n", owner)
	return nil
}
