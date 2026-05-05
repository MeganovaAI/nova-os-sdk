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

var knowledgeCmd = &cobra.Command{
	Use:   "knowledge",
	Short: "Search + ingest knowledge collections (/v1/managed/knowledge)",
}

var (
	knowledgeSearchCollection string
	knowledgeSearchTopK       int
	knowledgeSearchThreshold  float32
)

var knowledgeSearchCmd = &cobra.Command{
	Use:   "search <query>",
	Short: "Hybrid search across the knowledge base",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		body := gen.SearchKnowledgeJSONRequestBody{Query: args[0]}
		if knowledgeSearchCollection != "" {
			body.Collection = &knowledgeSearchCollection
		}
		if knowledgeSearchTopK > 0 {
			body.TopK = &knowledgeSearchTopK
		}
		if knowledgeSearchThreshold > 0 {
			body.Threshold = &knowledgeSearchThreshold
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		resp, err := c.SearchKnowledgeWithResponse(context.Background(), body)
		if err != nil {
			return fmt.Errorf("search knowledge: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		return printKnowledgeChunks(cmd, resp.JSON200)
	},
}

var (
	knowledgeIngestFile       string
	knowledgeIngestTitle      string
	knowledgeIngestCollection string
)

var knowledgeIngestCmd = &cobra.Command{
	Use:   "ingest [content]",
	Short: "Ingest a document into a knowledge collection",
	Long: `Ingest a single document into a knowledge collection.

Content is read from the positional arg, or from --file/-f when the body
lives on disk. Exactly one of the two must be provided.`,
	Args: cobra.MaximumNArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		var content string
		switch {
		case len(args) == 1 && knowledgeIngestFile != "":
			return fmt.Errorf("pass content as either a positional arg OR --file, not both")
		case len(args) == 1:
			content = args[0]
		case knowledgeIngestFile != "":
			data, err := os.ReadFile(knowledgeIngestFile)
			if err != nil {
				return fmt.Errorf("read file: %w", err)
			}
			content = string(data)
		default:
			return fmt.Errorf("content required (positional arg or --file/-f)")
		}
		body := gen.IngestKnowledgeJSONRequestBody{Content: content}
		if knowledgeIngestTitle != "" {
			body.Title = &knowledgeIngestTitle
		}
		if knowledgeIngestCollection != "" {
			body.Collection = &knowledgeIngestCollection
		}
		c, err := newClient()
		if err != nil {
			return err
		}
		resp, err := c.IngestKnowledgeWithResponse(context.Background(), body)
		if err != nil {
			return fmt.Errorf("ingest knowledge: %w", err)
		}
		if resp.StatusCode() >= 300 {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		if flagJSON {
			cmd.Println(string(resp.Body))
		} else {
			cmd.Println("ingested")
		}
		return nil
	},
}

var knowledgeCollectionsCmd = &cobra.Command{
	Use:   "collections",
	Short: "List every knowledge collection",
	RunE: func(cmd *cobra.Command, args []string) error {
		c, err := newClient()
		if err != nil {
			return err
		}
		resp, err := c.ListKnowledgeCollectionsWithResponse(context.Background())
		if err != nil {
			return fmt.Errorf("list collections: %w", err)
		}
		if resp.JSON200 == nil {
			return fmt.Errorf("unexpected status %s", resp.Status())
		}
		if flagJSON {
			b, _ := json.MarshalIndent(resp.JSON200, "", "  ")
			cmd.Println(string(b))
			return nil
		}
		for _, name := range resp.JSON200.Data {
			cmd.Println(name)
		}
		return nil
	},
}

func init() {
	knowledgeSearchCmd.Flags().StringVar(&knowledgeSearchCollection, "collection", "", "Collection to search; empty = caller's own")
	knowledgeSearchCmd.Flags().IntVar(&knowledgeSearchTopK, "top-k", 5, "Maximum passages to return")
	knowledgeSearchCmd.Flags().Float32Var(&knowledgeSearchThreshold, "threshold", 0, "Minimum score to include (0 = no filter)")

	knowledgeIngestCmd.Flags().StringVarP(&knowledgeIngestFile, "file", "f", "", "Read content from a file instead of the positional arg")
	knowledgeIngestCmd.Flags().StringVar(&knowledgeIngestTitle, "title", "", "Document title")
	knowledgeIngestCmd.Flags().StringVar(&knowledgeIngestCollection, "collection", "", "Target collection; defaults to \"default\"")

	knowledgeCmd.AddCommand(knowledgeSearchCmd)
	knowledgeCmd.AddCommand(knowledgeIngestCmd)
	knowledgeCmd.AddCommand(knowledgeCollectionsCmd)
	rootCmd.AddCommand(knowledgeCmd)
}

func printKnowledgeChunks(cmd *cobra.Command, resp *gen.KnowledgeSearchResponse) error {
	if flagJSON {
		b, _ := json.MarshalIndent(resp, "", "  ")
		cmd.Println(string(b))
		return nil
	}
	tw := tabwriter.NewWriter(cmd.OutOrStdout(), 0, 0, 2, ' ', 0)
	defer tw.Flush()
	fmt.Fprintln(tw, "SCORE\tCOLLECTION\tDOCUMENT_ID\tCONTENT")
	for _, ch := range resp.Data {
		score := float32(0)
		if ch.Score != nil {
			score = *ch.Score
		}
		coll := ""
		if ch.Collection != nil {
			coll = *ch.Collection
		}
		docID := ""
		if ch.DocumentId != nil {
			docID = *ch.DocumentId
		}
		content := ch.Content
		if len(content) > 80 {
			content = content[:77] + "..."
		}
		fmt.Fprintf(tw, "%.3f\t%s\t%s\t%s\n", score, coll, docID, content)
	}
	return nil
}
