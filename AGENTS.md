# Agents guide

Context for AI agents working in this repository.

## What this is

A personal Homebrew tap (`brew tap scallister/scallister`). Formulae live in `Formula/*.rb`. [README.md](README.md) is **public-facing** — install instructions and a tools list only. Maintainer and agent workflows belong here in AGENTS.md.

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
Script: [`.github/scripts/bump-formulae.py`](.github/scripts/bump-formulae.py)  
Tests: [`.github/scripts/test_bump_formulae.py`](.github/scripts/test_bump_formulae.py) (run via **Test Scripts** workflow or `python3 -m unittest discover -s .github/scripts -p "test_*.py"`)

- Formulae opt in with `# autobump: owner/repo` before the `class` line
- Workflow runs daily at 06:00 UTC and on `workflow_dispatch`
- Checks upstream GitHub repos for latest `v*` semver tag
- Updates **only** `version` and `tag:` — never `install`, `depends_on`, `desc`, etc.
- Commits and pushes bumps directly to `main`; no setup in tool repos

**Do not** manually bump `version` / `tag:` for autobump formulae unless fixing a mistake — let the workflow handle releases.

## Adding a new tool

1. Copy an existing formula from `Formula/`
2. Adapt metadata and `install` for the tool type
3. Add `# autobump: scallister/<repo>` if releases should auto-bump
4. Set `tag:` and `version` to the current release tag
5. **Update [README.md](README.md)** — add the tool to the Tools table with a brief public-facing description and link to the upstream repo
6. **Test the formula** — see [Testing formulae](#testing-formulae) below
7. PR and merge — no changes needed in the upstream tool repo

When a tool is removed, remove its formula and its README entry in the same PR.

## Testing formulae

Before opening a PR for a new or changed formula, verify it installs and runs. Do not rely on the Python autobump tests alone — they do not exercise `install` or upstream tags.

**Prerequisites**

- Homebrew installed (`brew --version` works)
- The upstream repo has the `tag:` referenced in the formula (check with `git ls-remote --tags https://github.com/owner/repo.git`)

**Local tap install (Linux / cloud agents)**

Clone the tap to a separate directory so `brew tap` does not hit git hardlink errors when the working copy is already a git repo:

```bash
git clone --no-hardlinks /path/to/homebrew-scallister /tmp/homebrew-scallister-tap
brew tap scallister/scallister /tmp/homebrew-scallister-tap
brew trust scallister/scallister
brew install <formula>
```

On macOS with a normal checkout, `brew tap scallister/scallister /path/to/homebrew-scallister` is usually enough.

**Verify the install**

```bash
brew test <formula>          # if the formula has a test do block
<installed-command> --help   # or another non-destructive smoke check
```

For tools that need a tmux session or other interactive setup, use the lightest check that confirms the binary is on `PATH` and executes (for example, a `help` subcommand).

**Optional checks**

```bash
brew audit --strict scallister/scallister/<formula>
python3 -m unittest discover -s .github/scripts -p "test_*.py"
```

`brew audit` may flag style differences this tap intentionally keeps (for example `version "v1.0.0"` with a leading `v`, or `:using => :git` hash syntax). Match existing formulae in `Formula/` rather than changing tap-wide conventions to satisfy audit.

## Releasing

Upstream repos push `v*` tags. This tap picks them up on the next daily run (or via manual workflow dispatch). Release tags must be kept — branch deletion is fine, tag deletion is not.

## When editing

- Preserve formula style (`:using => :git`, separate `version` line)
- Do not convert git-based formulae to tarballs
- Do not add cross-repo workflows or secrets to tool repos for bumping
- Keep autobump logic in this repo only
- Keep [README.md](README.md) in sync with `Formula/` — update the Tools table when adding or removing a formula; do not put maintainer instructions in README
