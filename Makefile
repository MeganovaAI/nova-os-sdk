.PHONY: spec-validate spec-lint spec-hash spec-check codegen-go codegen-python smoke

SPEC := openapi/nova-os-partner.v1.yaml
HASH_FILE := openapi/openapi-hash.txt

spec-validate:
	openapi-spec-validator $(SPEC)

spec-lint:
	spectral lint --ruleset openapi/.spectral.yaml $(SPEC)

spec-hash:
	@sha256sum $(SPEC) | cut -c1-12

spec-check: spec-validate spec-lint
	@echo "Comparing canonical hash..."
	@actual=$$(sha256sum $(SPEC) | cut -c1-12); \
	committed=$$(cat $(HASH_FILE)); \
	if [ "$$actual" != "$$committed" ]; then \
	  echo "FAIL: spec hash drift. Committed=$$committed Actual=$$actual"; \
	  echo "Run 'make spec-hash > $(HASH_FILE) && git commit'."; \
	  exit 1; \
	fi
	@echo "OK: spec hash matches ($$committed)."

codegen-go:
	cd cli && go generate ./...

codegen-python:
	cd python && openapi-python-client generate --path ../$(SPEC) --overwrite \
	  --config openapi-python-client.toml

smoke:
	$(MAKE) spec-check
	$(MAKE) codegen-go
	$(MAKE) codegen-python
	cd cli && go build ./...
	cd python && python -c "import nova_os; print('import ok')"
