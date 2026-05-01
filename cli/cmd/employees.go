package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"text/tabwriter"

	"github.com/spf13/cobra"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

var employeesCmd = &cobra.Command{
	Use:   "employees",
	Short: "Manage employees (/v1/managed/employees)",
}

var employeesListCmd = &cobra.Command{
	Use:   "list",
	Short: "List employees",
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.ListEmployeesWithResponse(ctx, &gen.ListEmployeesParams{})
		if err != nil {
			return fmt.Errorf("list employees: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printEmployeeList(cmd, resp.JSON200)
	},
}

var employeesGetCmd = &cobra.Command{
	Use:   "get <id>",
	Short: "Get an employee by ID",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.GetEmployeeWithResponse(ctx, args[0])
		if err != nil {
			return fmt.Errorf("get employee: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printEmployee(cmd, resp.JSON200)
	},
}

var employeesCreateFile string

var employeesCreateCmd = &cobra.Command{
	Use:   "create -f <file.json>",
	Short: "Create an employee from a JSON definition file",
	RunE: func(cmd *cobra.Command, args []string) error {
		if employeesCreateFile == "" {
			return fmt.Errorf("--file/-f is required")
		}
		data, err := os.ReadFile(employeesCreateFile)
		if err != nil {
			return fmt.Errorf("read file: %w", err)
		}
		var body gen.CreateEmployeeJSONRequestBody
		if err := json.Unmarshal(data, &body); err != nil {
			return fmt.Errorf("parse JSON: %w", err)
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.CreateEmployeeWithResponse(ctx, body)
		if err != nil {
			return fmt.Errorf("create employee: %w", err)
		}
		if resp.JSON201 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printEmployee(cmd, resp.JSON201)
	},
}

var employeesUpdateFile string

var employeesUpdateCmd = &cobra.Command{
	Use:   "update <id> -f <file.json>",
	Short: "Update an employee from a JSON patch file",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		if employeesUpdateFile == "" {
			return fmt.Errorf("--file/-f is required")
		}
		data, err := os.ReadFile(employeesUpdateFile)
		if err != nil {
			return fmt.Errorf("read file: %w", err)
		}
		var body gen.UpdateEmployeeJSONRequestBody
		if err := json.Unmarshal(data, &body); err != nil {
			return fmt.Errorf("parse JSON: %w", err)
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.UpdateEmployeeWithResponse(ctx, args[0], body)
		if err != nil {
			return fmt.Errorf("update employee: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printEmployee(cmd, resp.JSON200)
	},
}

var employeesDeleteCmd = &cobra.Command{
	Use:   "delete <id>",
	Short: "Delete an employee",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.DeleteEmployeeWithResponse(ctx, args[0])
		if err != nil {
			return fmt.Errorf("delete employee: %w", err)
		}
		if resp.StatusCode() >= 300 {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		cmd.Printf("deleted employee %s\n", args[0])
		return nil
	},
}

func init() {
	employeesCreateCmd.Flags().StringVarP(&employeesCreateFile, "file", "f", "", "Path to JSON definition file")
	employeesUpdateCmd.Flags().StringVarP(&employeesUpdateFile, "file", "f", "", "Path to JSON patch file")

	employeesCmd.AddCommand(employeesListCmd)
	employeesCmd.AddCommand(employeesGetCmd)
	employeesCmd.AddCommand(employeesCreateCmd)
	employeesCmd.AddCommand(employeesUpdateCmd)
	employeesCmd.AddCommand(employeesDeleteCmd)
	rootCmd.AddCommand(employeesCmd)
}

// newClient returns a ClientWithResponses configured with the global auth settings.
func newClient() (*gen.ClientWithResponses, error) {
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

func printEmployeeList(cmd *cobra.Command, list *gen.EmployeeList) error {
	if flagJSON {
		b, _ := json.MarshalIndent(list, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	tw := tabwriter.NewWriter(cmd.OutOrStdout(), 0, 0, 2, ' ', 0)
	defer tw.Flush()
	fmt.Fprintln(tw, "ID\tDISPLAY NAME\tAGENTS")
	for _, e := range list.Data {
		name := ""
		if e.DisplayName != nil {
			name = *e.DisplayName
		}
		agentCount := 0
		if e.Agents != nil {
			agentCount = len(*e.Agents)
		}
		fmt.Fprintf(tw, "%s\t%s\t%d\n", e.Id, name, agentCount)
	}
	return nil
}

func printEmployee(cmd *cobra.Command, e *gen.Employee) error {
	if flagJSON {
		b, _ := json.MarshalIndent(e, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	name := ""
	if e.DisplayName != nil {
		name = *e.DisplayName
	}
	desc := ""
	if e.Description != nil {
		desc = *e.Description
	}
	cmd.Printf("ID:          %s\n", e.Id)
	cmd.Printf("Name:        %s\n", name)
	cmd.Printf("Description: %s\n", desc)
	return nil
}
