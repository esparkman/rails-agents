#!/usr/bin/env python3
"""Native Codex file-edit guards and advisory lifecycle checks."""
import json
import os
from pathlib import Path
import subprocess
import sys


def git(directory, *args):
    result = subprocess.run(["git", "-C", str(directory), *args],
                            capture_output=True, text=True, check=False)
    return result.stdout.rstrip("\n") if result.returncode == 0 else None


def repository(path):
    directory = path if path.is_dir() else path.parent
    while not directory.exists() and directory != directory.parent:
        directory = directory.parent
    root = git(directory, "rev-parse", "--show-toplevel")
    return Path(root) if root is not None else None


def edit_paths(payload, cwd):
    tool = payload.get("tool_input")
    if not isinstance(tool, dict):
        raise ValueError("Missing file-edit tool input")
    if "command" in tool:
        patch = tool["command"]
        if not isinstance(patch, str):
            raise ValueError("Patch command must be a string")
        lines = patch.splitlines()
        if len(lines) < 3 or lines[0] != "*** Begin Patch" or lines[-1] != "*** End Patch":
            raise ValueError("Malformed native patch envelope")
        names = []
        for line in lines[1:-1]:
            prefixes = ("*** Add File: ", "*** Update File: ",
                        "*** Delete File: ", "*** Move to: ")
            prefix = next((p for p in prefixes if line.startswith(p)), None)
            if prefix is not None:
                names.append(line[len(prefix):])
            elif line.startswith("*** ") and line != "*** End of File":
                raise ValueError("Unrecognized patch file directive")
    else:
        names = [tool.get("file_path", tool.get("notebook_path"))]
    if not names or any(not isinstance(p, str) or p.strip() == "" or "\0" in p for p in names):
        raise ValueError("File-edit payload has no valid target paths")
    paths = []
    for name in names:
        path = Path(name).expanduser()
        if not path.is_absolute():
            path = cwd / path
        # Check both the directory entry and its destination when symlinks cross repos.
        paths.extend([Path(os.path.abspath(path)), path.resolve()])
    return paths


def pretool(payload, cwd):
    warnings = []
    for path in edit_paths(payload, cwd):
        root = repository(path)
        if root is None:
            continue
        branch = git(root, "symbolic-ref", "--short", "HEAD")
        default = git(root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        defaults = {"main", "master"}
        if default is not None and default.startswith("origin/"):
            defaults.add(default.removeprefix("origin/"))
        if branch in defaults:
            return decision("deny", f"Blocked edit to {path}: repository is on {branch}. Create a feature branch first.")
        if not ((root / "Gemfile").exists() or (root / ".ruby-version").exists()):
            continue
        relative = path.relative_to(root).parts
        implementation = relative[:1] in [("app",), ("lib",)] or relative[:2] == ("db", "migrate")
        if not implementation:
            continue
        markers = root / ".codex"
        if (markers / ".small-fix").is_file():
            warnings.append("SMALL-FIX BYPASS active; remove .codex/.small-fix after this independent fix.")
            continue
        story = markers / ".current-story"
        if story.is_file() and any(line.lower().split() == ["dor:", "passed"] for line in story.read_text().splitlines()):
            continue
        message = "Pipeline gate: no DoR: PASSED story in .codex/.current-story. Route through story-writer and product-manager, or declare an independent .codex/.small-fix."
        if (markers / ".pipeline-block").is_file():
            return decision("deny", message)
        warnings.append("PIPELINE WARN: " + message)
    if warnings:
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "\n".join(dict.fromkeys(warnings))}}
    return {}


def decision(value, reason):
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                  "permissionDecision": value, "permissionDecisionReason": reason}}


def session(cwd):
    root = repository(cwd) or cwd
    home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    agents = list((root / ".codex/agents").glob("*.toml"))
    broken = sum(not p.exists() for p in agents)
    text = (f"HARNESS CHECK: global instructions {home / 'AGENTS.md'} "
            f"({'present' if (home / 'AGENTS.md').is_file() else 'MISSING'}); "
            f"project native agent files: {len(agents)}, broken links: {broken}. "
            "This is an on-disk roster, not proof that roles are callable in this session.")
    return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}


def stop(payload, cwd):
    if payload.get("stop_hook_active") is True:
        return {}
    root = repository(cwd)
    if root is None:
        return {}
    status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if status is None or status == "":
        return {}
    paths = []
    entries = iter(status.split("\0"))
    for entry in entries:
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if "R" in entry[:2] or "C" in entry[:2]:
            original = next(entries, "")
            if original != "":
                paths.append(original)
    code = [p for p in paths if p.endswith((".rb", ".rake", ".erb", ".js", ".jsx", ".ts", ".tsx", ".svelte"))]
    if not code:
        return {}
    warnings = ["Verification advisory: changed code requires fresh suite/linter results and independent reviewer evidence. This hook cannot attest that tests or review ran; .last-review HEAD markers are not accepted as evidence."]
    if any(p.startswith(("app/views/", "app/controllers/")) for p in code):
        if not any(p.startswith(("test/system/", "spec/system/", "spec/features/")) for p in paths):
            warnings.append("No changed operator-journey test detected. Verify the real workflow using the configured Minitest or RSpec system suite; file presence alone never proves execution.")
    return {"systemMessage": "\n".join(warnings)}


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "PreToolUse"
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("Hook payload must be an object")
        cwd = Path(payload.get("cwd", os.getcwd())).resolve()
        if event == "PreToolUse":
            result = pretool(payload, cwd)
        elif event == "SessionStart":
            result = session(cwd)
        elif event == "Stop":
            result = stop(payload, cwd)
        else:
            raise ValueError("Unknown hook event")
    except (ValueError, TypeError, OSError, RuntimeError) as error:
        result = decision("deny", f"Cannot validate file edit: {error}") if event == "PreToolUse" else {"systemMessage": f"Harness advisory unavailable: {error}"}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
