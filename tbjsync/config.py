"""Load brand.toml + repos.toml and build the per-repo context the checks run against."""
from __future__ import annotations

import os
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent


def load_toml(path: Path) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


@dataclass
class Brand:
    raw: dict
    root: Path = KIT_ROOT

    @classmethod
    def load(cls, root: Path | None = None) -> "Brand":
        root = root or KIT_ROOT
        return cls(load_toml(root / "brand.toml"), root)

    @property
    def version(self) -> str:
        return self.raw["standards"]["version"]

    @property
    def enforce(self) -> str:
        return self.raw["standards"].get("enforce", "warn")

    @property
    def identity(self) -> dict:
        return self.raw["identity"]

    @property
    def palette(self) -> str:
        return self.raw["palette"]["active"]

    @property
    def badge_hex(self) -> str:
        return self.raw["palette"]["badge"][self.palette]

    def tier(self, name: str) -> dict:
        return self.raw["tiers"][name]

    def venture(self, name: str) -> dict:
        return self.raw["ventures"][name]

    def fmt(self, text: str) -> str:
        """Fill {github} {handle} {site} {domain} placeholders from [identity]."""
        return text.format(**self.identity)

    def tokens_path(self) -> Path:
        return self.root / "tokens" / f"{self.palette}.json"


@dataclass
class RepoEntry:
    name: str
    tier: str = "tool"
    venture: str = "tbj"
    license: str | None = None          # None → brand default
    relicense: bool = False             # explicit consent to replace a different LICENSE
    description: str = ""
    homepage: str = ""
    successor: str = ""                 # archive tier: where to point people
    wave: int = 2                       # rollout wave: 0 canary, 1 early, 2 everyone
    skip: list[str] = field(default_factory=list)  # check ids to skip for this repo
    notes: str = ""
    host: str = ""                      # target platform, one of [infra].hosts ("" = not decided yet)
    data: str = ""                      # target data store, one of [infra].data ("" = not decided yet)


def load_manifest(root: Path | None = None) -> dict[str, RepoEntry]:
    root = root or KIT_ROOT
    path = root / "repos.toml"
    if not path.exists():
        return {}
    data = load_toml(path).get("repo", {})
    out = {}
    for name, cfg in data.items():
        known = {k: v for k, v in cfg.items() if k in RepoEntry.__dataclass_fields__}
        out[name] = RepoEntry(name=name, **known)
    return out


# ── Stack detection ──────────────────────────────────────────────────────────
def walk_files(path: Path, limit: int = 4000) -> list[Path]:
    skip_dirs = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".godot", ".next"}
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for f in filenames:
            found.append(Path(dirpath) / f)
            if len(found) >= limit:
                return found
    return found


def detect_stack(files: list[Path], root: Path) -> list[str]:
    names = {p.name for p in files}
    exts = {p.suffix.lower() for p in files}
    stack = []
    if names & {"pyproject.toml", "requirements.txt", "setup.py"} or ".py" in exts:
        stack.append("python")
    if "package.json" in names:
        stack.append("node")
    if "project.godot" in names or ".gd" in exts:
        stack.append("godot")
    if ".ps1" in exts:
        stack.append("powershell")
    if ".cs" in exts or ".ahk" in exts:
        stack.append("windows")
    if ".kt" in exts or "build.gradle" in names or "build.gradle.kts" in names:
        stack.append("android")
    if exts & {".html", ".css", ".jsx", ".tsx"}:
        stack.append("web")
    return stack


def git(path: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return ""


@dataclass
class RepoContext:
    path: Path
    entry: RepoEntry
    brand: Brand
    files: list[Path]
    stack: list[str]
    default_branch: str
    has_dev: bool
    is_fork: bool = False

    @property
    def name(self) -> str:
        return self.entry.name

    @property
    def license_policy(self) -> str:
        return self.entry.license or self.brand.raw["license"]["default"]

    @property
    def readme_path(self) -> Path | None:
        for p in self.path.iterdir():
            if p.is_file() and p.name.lower() == "readme.md":
                return p
        return None

    def rel(self, p: Path) -> str:
        return str(p.relative_to(self.path))


def build_context(path: Path, brand: Brand, manifest: dict[str, RepoEntry],
                  default_branch: str | None = None, has_dev: bool | None = None) -> RepoContext:
    path = path.resolve()
    name = path.name
    entry = manifest.get(name) or RepoEntry(name=name)
    files = walk_files(path)
    if default_branch is None:
        default_branch = os.environ.get("TBJ_DEFAULT_BRANCH") or None
    if default_branch is None:
        head = git(path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        default_branch = head.split("/", 1)[1] if "/" in head else (git(path, "rev-parse", "--abbrev-ref", "HEAD") or "main")
    if has_dev is None:
        heads = git(path, "ls-remote", "--heads", "origin", "dev")
        has_dev = "refs/heads/dev" in heads
    return RepoContext(path=path, entry=entry, brand=brand, files=files,
                       stack=detect_stack(files, path), default_branch=default_branch,
                       has_dev=has_dev, is_fork=entry.tier == "external")
