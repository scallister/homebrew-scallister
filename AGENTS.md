# Agents guide

Context for AI agents working in this repository.

## What this is

A personal Homebrew tap (`brew tap scallister/scallister`). Formulae live in `Formula/*.rb`. User-facing docs are in [README.md](README.md).

## Formula conventions

Follow existing formulae in `Formula/`. Key rules:

- **Git URLs only** — no tarballs, no `sha256`
- **`version` on its own line**, separate from `url`
- **Pin source with `tag:`** in the `url` block (not `branch:`)
- **Multi-line `url`** with `:using => :git`
- Tools can be anything (Go, bash, etc.) — only `install` / `depends_on` / `test` differ

```ruby
# autobump: scallister/myrepo
class Mytool < Formula
  desc "..."
  homepage "https://github.com/scallister/myrepo"
  url "https://github.com/scallister/myrepo.git",
    tag: "v1.0.0",
    :using => :git

  version "v1.0.0"

  def install
    # tool-specific
  end
end
```

## Autobump

Daily workflow: [`.github/workflows/bump-formulae.yml`](.github/workflows/bump-formulae.yml)  
Script: [`.github/scripts/bump-formulae.rb`](.github/scripts/bump-formulae.rb)

- Formulae opt in with `# autobump: owner/repo` before the `class` line
- Workflow runs daily at 06:00 UTC and on `workflow_dispatch`
- Checks upstream GitHub repos for latest `v*` semver tag
- Updates **only** `version` and `tag:` — never `install`, `depends_on`, `desc`, etc.
- Opens a PR when changes are needed; no setup in tool repos

**Do not** manually bump `version` / `tag:` for autobump formulae unless fixing a mistake — let the workflow handle releases.

## Adding a new tool

1. Copy an existing formula from `Formula/`
2. Adapt metadata and `install` for the tool type
3. Add `# autobump: scallister/<repo>` if releases should auto-bump
4. Set `tag:` and `version` to the current release tag
5. PR and merge — no changes needed in the upstream tool repo

## Releasing

Upstream repos push `v*` tags. This tap picks them up on the next daily run (or via manual workflow dispatch). Release tags must be kept — branch deletion is fine, tag deletion is not.

## When editing

- Preserve formula style (`:using => :git`, separate `version` line)
- Do not convert git-based formulae to tarballs
- Do not add cross-repo workflows or secrets to tool repos for bumping
- Keep autobump logic in this repo only
