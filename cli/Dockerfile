# Distroless static base — no shell, no package manager, ~2 MB.
# Image expects a pre-built linux/amd64 or linux/arm64 binary copied in
# by goreleaser. Multi-arch manifest is assembled by goreleaser.
FROM gcr.io/distroless/static:nonroot

LABEL org.opencontainers.image.source="https://github.com/MeganovaAI/nova-os-sdk"
LABEL org.opencontainers.image.description="Nova OS partner CLI"
LABEL org.opencontainers.image.licenses="MIT"

# goreleaser drops the binary at the build context root.
COPY nova-os-cli /usr/local/bin/nova-os-cli

USER nonroot
ENTRYPOINT ["/usr/local/bin/nova-os-cli"]
