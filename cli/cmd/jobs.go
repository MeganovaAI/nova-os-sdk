package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"text/tabwriter"
	"time"

	"github.com/spf13/cobra"

	gen "github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

var jobsCmd = &cobra.Command{
	Use:   "jobs",
	Short: "Manage async jobs (/v1/managed/jobs)",
}

var jobsStatusFilter string
var jobsAgentFilter string

var jobsListCmd = &cobra.Command{
	Use:   "list",
	Short: "List jobs",
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		params := &gen.ListJobsParams{}
		if jobsStatusFilter != "" {
			s := gen.JobStatus(jobsStatusFilter)
			params.Status = &s
		}
		if jobsAgentFilter != "" {
			params.AgentId = &jobsAgentFilter
		}
		resp, err := c.ListJobsWithResponse(ctx, params)
		if err != nil {
			return fmt.Errorf("list jobs: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printJobList(cmd, resp.JSON200)
	},
}

var jobsGetCmd = &cobra.Command{
	Use:   "get <job-id>",
	Short: "Get a job by ID",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.GetJobWithResponse(ctx, args[0])
		if err != nil {
			return fmt.Errorf("get job: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printJob(cmd, resp.JSON200)
	},
}

var jobsCreateFile string

var jobsCreateCmd = &cobra.Command{
	Use:   "create -f <file.json>",
	Short: "Submit a new async job from a JSON definition file",
	RunE: func(cmd *cobra.Command, args []string) error {
		if jobsCreateFile == "" {
			return fmt.Errorf("--file/-f is required")
		}
		data, err := os.ReadFile(jobsCreateFile)
		if err != nil {
			return fmt.Errorf("read file: %w", err)
		}
		var body gen.CreateJobJSONRequestBody
		if err := json.Unmarshal(data, &body); err != nil {
			return fmt.Errorf("parse JSON: %w", err)
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.CreateJobWithResponse(ctx, body)
		if err != nil {
			return fmt.Errorf("create job: %w", err)
		}
		if resp.JSON202 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printJob(cmd, resp.JSON202)
	},
}

var jobsCancelCmd = &cobra.Command{
	Use:   "cancel <job-id>",
	Short: "Cancel a running or queued job",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		ctx := context.Background()
		resp, err := c.CancelJobWithResponse(ctx, args[0])
		if err != nil {
			return fmt.Errorf("cancel job: %w", err)
		}
		if resp.StatusCode() >= 300 {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		cmd.Printf("cancelled job %s\n", args[0])
		return nil
	},
}

func init() {
	jobsListCmd.Flags().StringVar(&jobsStatusFilter, "status", "", "Filter by status (queued, running, completed, failed, cancelled)")
	jobsListCmd.Flags().StringVar(&jobsAgentFilter, "agent-id", "", "Filter by agent ID")
	jobsCreateCmd.Flags().StringVarP(&jobsCreateFile, "file", "f", "", "Path to JSON definition file")

	jobsCmd.AddCommand(jobsListCmd)
	jobsCmd.AddCommand(jobsGetCmd)
	jobsCmd.AddCommand(jobsCreateCmd)
	jobsCmd.AddCommand(jobsCancelCmd)
	rootCmd.AddCommand(jobsCmd)
}

func printJobList(cmd *cobra.Command, list *gen.JobList) error {
	if flagJSON {
		b, _ := json.MarshalIndent(list, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	tw := tabwriter.NewWriter(cmd.OutOrStdout(), 0, 0, 2, ' ', 0)
	defer tw.Flush()
	fmt.Fprintln(tw, "JOB ID\tAGENT\tSTATUS\tCREATED")
	for _, j := range list.Data {
		fmt.Fprintf(tw, "%s\t%s\t%s\t%s\n",
			j.JobId,
			j.AgentId,
			string(j.Status),
			j.CreatedAt.Format(time.RFC3339),
		)
	}
	return nil
}

func printJob(cmd *cobra.Command, j *gen.Job) error {
	if flagJSON {
		b, _ := json.MarshalIndent(j, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	cmd.Printf("Job ID:  %s\n", j.JobId)
	cmd.Printf("Agent:   %s\n", j.AgentId)
	cmd.Printf("Status:  %s\n", string(j.Status))
	cmd.Printf("Created: %s\n", j.CreatedAt.Format(time.RFC3339))
	return nil
}
