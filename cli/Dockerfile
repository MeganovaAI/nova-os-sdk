# Distroless static base — no shell, no package manager, ~2 MB.
# Image expects a pre-built linux/amd64 or linux/arm64 binary copied in
# by goreleaser. Multi-arch manifest is assembled by goreleaser.
FROM gcr.io/distroless/static:nonroot

LABEL org.opencontainers.image.source="https://github.com/libraos/sdk"
LABEL org.opencontainers.image.description="LibraOS partner CLI"
LABEL org.opencontainers.image.licenses="MIT"

# goreleaser drops the binary at the build context root.
COPY libraos-cli /usr/local/bin/libraos-cli

USER nonroot
ENTRYPOINT ["/usr/local/bin/libraos-cli"]
