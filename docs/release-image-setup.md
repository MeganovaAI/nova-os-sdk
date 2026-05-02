# Release-image workflow — one-time setup

The `release-image.yml` workflow in this repo publishes the Nova OS server as a public Docker image at `ghcr.io/meganovaai/nova-os`. The Go source lives in the private `MeganovaAI/nova-os` repo and is never copied here — the workflow checks it out at runtime via an SSH deploy key.

This page is the one-time bootstrap. Once it's done, releasing a new version is a single `gh workflow run` invocation (see "Cutting a release" at the bottom).

## Why the workflow lives here, not in nova-os

The published Docker package on GitHub auto-links to the **publisher** repo (the one whose workflow ran the push). Publishing from the private nova-os repo links the package to nova-os, which leaks the private repo's existence to anyone with read access who lands on the package page. Publishing from this public repo links the package here instead — no leak.

## Step 1 — Generate the deploy key

On any machine:

```bash
ssh-keygen -t ed25519 -C "nova-os-sdk release-image deploy key" -f /tmp/nova-os-deploy-key -N ""
```

Two files are produced:

- `/tmp/nova-os-deploy-key` — private key (goes into a secret on this repo)
- `/tmp/nova-os-deploy-key.pub` — public key (goes onto the nova-os repo as a deploy key)

## Step 2 — Add the public key to MeganovaAI/nova-os

1. Open <https://github.com/MeganovaAI/nova-os/settings/keys>
2. Click **Add deploy key**
3. Title: `nova-os-sdk release-image (read-only)`
4. Paste the contents of `/tmp/nova-os-deploy-key.pub`
5. **Leave "Allow write access" unchecked** — read is sufficient
6. **Add key**

## Step 3 — Add the private key as a secret on MeganovaAI/nova-os-sdk

1. Open <https://github.com/MeganovaAI/nova-os-sdk/settings/secrets/actions>
2. Click **New repository secret**
3. Name: `NOVA_OS_DEPLOY_KEY`
4. Value: paste the entire contents of `/tmp/nova-os-deploy-key` including the `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----` lines
5. **Add secret**

Then delete the local files:

```bash
shred -u /tmp/nova-os-deploy-key /tmp/nova-os-deploy-key.pub
```

## Step 4 — Authorize this repo to push to the package

The package `ghcr.io/meganovaai/nova-os` is currently linked to the private nova-os repo. Before this repo's workflow can push, it needs to be added to the package's allowlist:

1. Open <https://github.com/orgs/MeganovaAI/packages/container/package/nova-os/settings>
2. Scroll to **Manage Actions access**
3. Click **Add repository**
4. Select `MeganovaAI/nova-os-sdk`
5. Role: **Write**
6. **Add**

After the first successful push from this repo, GitHub will re-link the package's "source repository" to `MeganovaAI/nova-os-sdk` automatically — at which point the private nova-os repo can be removed from the package's Manage Actions access list (and its old release-image workflow can be archived).

## Step 5 — Cutting a release

Once steps 1-4 are done, every subsequent release is one command:

```bash
gh workflow run release-image.yml -R MeganovaAI/nova-os-sdk -f tag=v0.1.5
```

Or via the UI: **Actions → Release Docker image → Run workflow → tag: `v0.1.5`**.

The workflow checks out `MeganovaAI/nova-os@v0.1.5`, builds the multi-arch image, and pushes:

- `ghcr.io/meganovaai/nova-os:v0.1.5`
- `ghcr.io/meganovaai/nova-os:latest` (only for stable `vMAJOR.MINOR.PATCH` tags — RC / beta / alpha pre-releases skip the `:latest` move)

The build summary at the end of the run includes the source commit SHA pinned in the image's OCI labels and `nova-os version` output.

## Rotating the deploy key

The deploy key is read-only and scoped to a single private repo, so its blast radius is contained. Still, rotate annually (or sooner on suspected compromise):

1. Repeat Steps 1-3 with a new key pair
2. Delete the old key from <https://github.com/MeganovaAI/nova-os/settings/keys>

The next workflow run picks up the new secret automatically.
