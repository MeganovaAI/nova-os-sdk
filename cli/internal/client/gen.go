package client

// Pinned to the go.mod version (oapi-codegen v2.6.0) via `go run` so local
// `make codegen-go` is byte-identical to CI (which installs @v2.6.0) — a bare
// `oapi-codegen` on PATH could be any version and drift the generated client.
//go:generate go run github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen -config config.yaml ../../../openapi/nova-os-partner.v1.yaml
