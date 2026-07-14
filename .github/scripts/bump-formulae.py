#!/usr/bin/env python3
"""Bump Homebrew formulae from upstream GitHub release tags.

Scans Formula/*.rb for a top-of-file autobump marker:

    # autobump: owner/repo

When a newer v* tag exists on GitHub, updates the formula version line and
git tag ref in the url block. Network access is only used to list tags.

Usage:
    python3 bump-formulae.py
    python3 bump-formulae.py --dry-run
    python3 -m unittest discover -s .github/scripts -p "test_*.py"
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

FORMULA_DIR = Path(__file__).resolve().parents[2] / "Formula"
AUTOBUMP_PATTERN = re.compile(r"#\s*autobump:\s*([^\s#]+)", re.IGNORECASE)
VERSION_PATTERN = re.compile(r'^([ \t]*)version[ \t]+"([^"]+)"', re.MULTILINE)
TAG_PATTERN = re.compile(r'^([ \t]*)tag:[ \t]*"[^"]+",?', re.MULTILINE)
BRANCH_PATTERN = re.compile(r'^([ \t]*)branch:[ \t]*"[^"]+",?', re.MULTILINE)
RELEASE_TAG_PATTERN = re.compile(r"^v\d", re.IGNORECASE)


def github_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN")


def github_get(path: str) -> list | dict:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "homebrew-scallister-bump-formulae",
            **(
                {"Authorization": f"Bearer {github_token()}"}
                if github_token()
                else {}
            ),
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        body = error.read().decode()
        raise SystemExit(f"GitHub API error for {path}: {error.code} {body}") from error


def parse_version(tag: str) -> tuple[int, ...] | None:
    clean = re.sub(r"^v", "", tag, flags=re.IGNORECASE)
    match = re.match(r"^(\d+(?:\.\d+)*)", clean)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def fetch_release_tags(owner: str, repo: str) -> list[str]:
    tags: list[str] = []
    page = 1

    while True:
        batch = github_get(f"/repos/{owner}/{repo}/tags?per_page=100&page={page}")
        if not batch:
            break

        tags.extend(tag["name"] for tag in batch if RELEASE_TAG_PATTERN.match(tag["name"]))
        if len(batch) < 100:
            break
        page += 1

    return tags


def latest_release_tag(tags: list[str]) -> str | None:
    tagged_versions: list[tuple[tuple[int, ...], str]] = []
    for tag in tags:
        version = parse_version(tag)
        if version is not None:
            tagged_versions.append((version, tag))

    if not tagged_versions:
        return None

    return max(tagged_versions, key=lambda item: item[0])[1]


def parse_autobump_repo(contents: str) -> tuple[str, str] | None:
    match = AUTOBUMP_PATTERN.search(contents)
    if not match:
        return None

    repo = match.group(1)
    if "/" not in repo:
        raise SystemExit(f"Invalid autobump repo {repo!r}")

    owner, name = repo.split("/", 1)
    return owner, name


def current_version(contents: str) -> str | None:
    match = VERSION_PATTERN.search(contents)
    return match.group(2) if match else None


def version_outdated(current: str, latest: str) -> bool:
    current_version = parse_version(current)
    latest_version = parse_version(latest)
    if current_version is None or latest_version is None:
        return True
    return latest_version > current_version


def bump_formula_contents(contents: str, new_tag: str) -> str:
    updated = VERSION_PATTERN.sub(rf'\1version "{new_tag}"', contents, count=1)

    if TAG_PATTERN.search(updated):
        updated = TAG_PATTERN.sub(rf'\1tag: "{new_tag}",', updated, count=1)
    elif BRANCH_PATTERN.search(updated):
        updated = BRANCH_PATTERN.sub(rf'\1tag: "{new_tag}",', updated, count=1)
    else:
        raise SystemExit("Formula is missing tag: or branch: in url block")

    return updated


def process_formula(path: Path, dry_run: bool) -> str:
    contents = path.read_text()
    repo_parts = parse_autobump_repo(contents)
    if repo_parts is None:
        return "skipped"

    owner, repo = repo_parts
    formula_version = current_version(contents)
    if formula_version is None:
        raise SystemExit(f"{path}: missing version line")

    latest_tag = latest_release_tag(fetch_release_tags(owner, repo))
    if latest_tag is None:
        print(f"{path}: no v* release tags found for {owner}/{repo}", file=sys.stderr)
        return "skipped"

    if formula_version == latest_tag:
        print(f"{path}: up to date ({latest_tag})")
        return "current"

    if not version_outdated(formula_version, latest_tag):
        print(
            f"{path}: formula version {formula_version} is newer than "
            f"latest tag {latest_tag}, skipping"
        )
        return "skipped"

    print(f"{path}: {formula_version} -> {latest_tag}")
    if not dry_run:
        path.write_text(bump_formula_contents(contents, latest_tag))

    return "bumped"


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    checked = bumped = current = skipped = 0

    for path in sorted(FORMULA_DIR.glob("*.rb")):
        if not path.is_file():
            continue

        checked += 1
        result = process_formula(path, dry_run)
        if result == "bumped":
            bumped += 1
        elif result == "current":
            current += 1
        elif result == "skipped":
            skipped += 1

    print(f"Checked {checked} formulae: bumped {bumped}, current {current}, skipped {skipped}")

    if checked == 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
