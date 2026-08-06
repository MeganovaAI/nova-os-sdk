# Release-image workflow — one-time setup

The `release-image.yml` workflow in this repo publishes the LibraOS server as a public Docker image at `ghcr.io/libraos/libraos`. The Go source lives in the private `libraos/libraos` repo and is never copied here — the workflow checks it out at runtime via an SSH deploy key.

This page is the one-time bootstrap. Once it's done, releasing a new version is a single `gh workflow run` invocation (see "Cutting a release" at the bottom).

## Why the workflow lives here, not in nova-os

The published Docker package on GitHub auto-links to the **publisher** repo (the one whose workflow ran the push). Publishing from the private server repo links the package to it, which leaks the private repo's existence to anyone with read access who lands on the package page. Publishing from this public repo links the package here instead — no leak.

## Step 1 — Generate the deploy key

On any machine:

```bash
ssh-keygen -t ed25519 -C "libraos-sdk release-image deploy key" -f /tmp/nova-os-deploy-key -N ""
```

Two files are produced:

- `/tmp/nova-os-deploy-key` — private key (goes into a secret on this repo)
- `/tmp/nova-os-deploy-key.pub` — public key (goes onto the private server repo as a deploy key)

## Step 2 — Add the public key to libraos/libraos

1. Open <https://github.com/libraos/libraos/settings/keys>
2. Click **Add deploy key**
3. Title: `libraos-sdk release-image (read-only)`
4. Paste the contents of `/tmp/nova-os-deploy-key.pub`
5. **Leave "Allow write access" unchecked** — read is sufficient
6. **Add key**

## Step 3 — Add the private key as a secret on libraos/sdk

1. Open <https://github.com/libraos/sdk/settings/secrets/actions>
2. Click **New repository secret**
3. Name: `NOVA_OS_DEPLOY_KEY`
4. Value: paste the entire contents of `/tmp/nova-os-deploy-key` including the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines
5. **Add secret**

Then delete the local files:

```bash
shred -u /tmp/nova-os-deploy-key /tmp/nova-os-deploy-key.pub
```

## Step 4 — Package access

**The primary image needs no grant.** `ghcr.io/libraos/libraos` is in the same org as this
repo, so the workflow's `GITHUB_TOKEN` can push it directly with `permissions: packages: write`.
Nothing to configure.

This step used to describe adding `libraos/sdk` to an allowlist on the pre-rename
`meganovaai/nova-os` package. That is no longer required for a release to succeed.

### Optional — the deprecated legacy mirror

The workflow also copies each manifest to `ghcr.io/meganovaai/nova-os` so anything still pulling
the pre-rename path keeps working. That push is **cross-org**, so it does need a grant:

1. Open <https://github.com/orgs/MeganovaAI/packages/container/package/nova-os/settings>
2. Scroll to **Manage Actions access** → **Add repository** → `libraos/sdk` → Role **Write**

The mirror step is `continue-on-error`, so if that grant is absent or lapses the release still
succeeds and the job summary says the legacy path was not updated. Retire the mirror once pulls
of the old path have stopped.


## Step 5 — Cutting a release

Once steps 1-4 are done, every subsequent release is one command:

```bash
gh workflow run release-image.yml -R libraos/sdk -f tag=v0.1.7
```

Or via the UI: **Actions → Release Docker image → Run workflow → tag: `v0.1.7`**.

The workflow checks out `libraos/libraos@v0.1.7`, builds the multi-arch image, and pushes:

- `ghcr.io/libraos/libraos:v0.1.7`
- `ghcr.io/libraos/libraos:latest` (only for stable `vMAJOR.MINOR.PATCH` tags — RC / beta / alpha pre-releases skip the `:latest` move)

The build summary at the end of the run includes the source commit SHA pinned in the image's OCI labels and `nova-os version` output.

## Rotating the deploy key

The deploy key is read-only and scoped to a single private repo, so its blast radius is contained. Still, rotate annually (or sooner on suspected compromise):

1. Repeat Steps 1-3 with a new key pair
2. Delete the old key from <https://github.com/libraos/libraos/settings/keys>

The next workflow run picks up the new secret automatically.
