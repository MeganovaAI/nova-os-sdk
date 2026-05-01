package main

import (
	"fmt"
	"os"

	"github.com/MeganovaAI/nova-os-sdk/cli/internal/client"
)

const (
	cliVersion  = "0.1.0-alpha.1"
	specVersion = "1.0.0-alpha.1"
)

func main() {
	args := os.Args[1:]
	if len(args) >= 1 && args[0] == "version" {
		fmt.Printf("nova-os-cli %s (spec %s)\n", cliVersion, specVersion)
		// Reference the generated package so the build fails if codegen is broken.
		_ = (*client.Client)(nil)
		return
	}
	fmt.Fprintln(os.Stderr, "usage: nova-os-cli version")
	os.Exit(2)
}
