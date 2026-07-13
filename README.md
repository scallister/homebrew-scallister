# homebrew-scallister

Personal Homebrew tap for scallister tools.

## Install

```bash
brew tap scallister/scallister
brew install gitpath
```

## Add a new tool

1. Copy an existing formula from [Formula/](Formula/) as a starting point.
2. Adapt `desc`, `homepage`, and `install` for the tool (Go, bash, etc.).
3. Add an autobump marker before the class line:

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
    # tool-specific install steps
  end
end
```

4. Open a PR in this repo and merge.

Formulae use git tags (not tarballs). The `version` line stays separate from `url`.

## Release a new version

In the tool repo, push a semver tag:

```bash
git tag v1.2.3
git push origin v1.2.3
```

A daily GitHub Action checks formulae with `# autobump:` markers and opens a PR here when a newer `v*` tag exists. Use **Actions → Bump Formulae → Run workflow** for an immediate check.

No setup is required in tool repos.

## Autobump

Only formulae with a top-of-file marker are checked:

```ruby
# autobump: owner/repo
```

The workflow updates `version` and `tag:` in the `url` block. It does not change `install`, `depends_on`, or other formula logic.
