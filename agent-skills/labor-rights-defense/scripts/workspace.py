from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


def resolve_git_username() -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    username = result.stdout.strip()
    return username or None


def normalize_workspace_username(raw_name: str | None) -> str:
    if raw_name and raw_name.strip():
        return raw_name.strip().replace(" ", "-")
    return "default-zoom"


def get_repo_root(skill_dir: Path) -> Path:
    return skill_dir.resolve().parent.parent


def get_workspace_root(skill_dir: Path) -> Path:
    return get_repo_root(skill_dir) / "labor-rights-defense-workspace"


def get_user_workspace(skill_dir: Path, username: str | None = None) -> Path:
    raw_username = username if username is not None else resolve_git_username()
    workspace_user = normalize_workspace_username(raw_username)
    return get_workspace_root(skill_dir) / workspace_user


def get_workspace_paths(skill_dir: Path, username: str | None = None) -> dict[str, Path]:
    root = get_user_workspace(skill_dir, username=username)
    profile_dir = root / "profile"
    cases_dir = root / "cases"
    cache_dir = root / "cache"
    cache_law_dir = cache_dir / "law"
    cache_procedure_dir = cache_dir / "procedure"
    return {
        "workspace_root": root,
        "profile_dir": profile_dir,
        "cases_dir": cases_dir,
        "cache_dir": cache_dir,
        "cache_law_dir": cache_law_dir,
        "cache_procedure_dir": cache_procedure_dir,
        "profile_file": profile_dir / "profile.json",
    }


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def ensure_workspace(skill_dir: Path, username: str | None = None) -> dict:
    source_git_username = username if username is not None else resolve_git_username()
    workspace_user = normalize_workspace_username(source_git_username)
    paths = get_workspace_paths(skill_dir, username=username)

    created_dirs: list[str] = []
    created_files: list[str] = []
    for key in [
        "workspace_root",
        "profile_dir",
        "cases_dir",
        "cache_dir",
        "cache_law_dir",
        "cache_procedure_dir",
    ]:
        directory = paths[key]
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        if not existed:
            created_dirs.append(str(directory))

    profile_path = paths["profile_file"]
    if not profile_path.exists():
        profile_path.write_text(
            json.dumps(
                {
                    "workspace_user": workspace_user,
                    "source_git_username": source_git_username,
                    "created_at": _timestamp(),
                    "updated_at": _timestamp(),
                    "region": {"province": None, "city": None},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        created_files.append(str(profile_path))

    return {
        "source_git_username": source_git_username,
        "workspace_user": workspace_user,
        "workspace_root": str(paths["workspace_root"]),
        "created": bool(created_dirs or created_files),
        "created_dirs": created_dirs,
        "created_files": created_files,
    }

