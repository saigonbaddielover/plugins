from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NAME = "saigonbaddielover"
EXPECT_PUBLIC = True
EXPECTED_SOURCES = {"overseer": ("https://github.com/saigonbaddielover/overseer.git", "plugins/overseer", "plugin-release")}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path} must contain an object")
    return value


def plugins(value: dict, path: Path) -> dict[str, dict]:
    entries = value.get("plugins")
    if not isinstance(entries, list) or not entries:
        raise SystemExit(f"{path} must contain at least one plugin")
    result: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit(f"{path} contains an invalid plugin entry")
        name = entry.get("name")
        if not isinstance(name, str) or not name or name in result:
            raise SystemExit(f"{path} contains an invalid or duplicate plugin name")
        if "version" in entry:
            raise SystemExit(f"{path} must not duplicate plugin version metadata")
        result[name] = entry
    return result


def source(entry: dict, label: str) -> tuple[str, str, str]:
    value = entry.get("source")
    if not isinstance(value, dict) or value.get("source") != "git-subdir":
        raise SystemExit(f"{label} must use git-subdir")
    url = value.get("url")
    path = value.get("path")
    ref = value.get("ref")
    if not all(isinstance(item, str) and item for item in (url, path, ref)):
        raise SystemExit(f"{label} source is incomplete")
    if ref != "plugin-release":
        raise SystemExit(f"{label} must use plugin-release")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "github.com" or not parsed.path.endswith(".git"):
        raise SystemExit(f"{label} must use an HTTPS GitHub source")
    return url, path, ref


def repo_slug(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path.removeprefix("/").removesuffix(".git")


def anonymous_visibility(slug: str) -> bool:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{slug}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "saigonbaddielover-plugin-catalog-validator"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            value = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return False
        raise SystemExit(f"GitHub visibility probe failed for {slug}: HTTP {error.code}") from error
    return not bool(value.get("private"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true")
    args = parser.parse_args()
    claude_path = ROOT / ".claude-plugin" / "marketplace.json"
    codex_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    claude = load(claude_path)
    codex = load(codex_path)
    if claude.get("name") != EXPECTED_NAME or codex.get("name") != EXPECTED_NAME:
        raise SystemExit("marketplace identity mismatch")
    claude_plugins = plugins(claude, claude_path)
    codex_plugins = plugins(codex, codex_path)
    if set(claude_plugins) != set(codex_plugins):
        raise SystemExit("Claude and Codex plugin sets differ")
    if set(claude_plugins) != set(EXPECTED_SOURCES):
        raise SystemExit("catalog plugin set differs from policy")
    for name in sorted(claude_plugins):
        claude_source = source(claude_plugins[name], f"Claude plugin {name}")
        codex_source = source(codex_plugins[name], f"Codex plugin {name}")
        if claude_source != codex_source:
            raise SystemExit(f"plugin {name} source differs between catalogs")
        if claude_source != EXPECTED_SOURCES[name]:
            raise SystemExit(f"plugin {name} source differs from policy")
        if args.online and anonymous_visibility(repo_slug(claude_source[0])) != EXPECT_PUBLIC:
            raise SystemExit(f"plugin {name} source visibility violates catalog policy")
    print(f"validated {len(claude_plugins)} plugin(s) in {EXPECTED_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
