#!/usr/bin/env python3
"""
Fetch external documentation from configured repositories.

This script clones external repositories and syncs their documentation
to the local docs directory.

Usage:
    python scripts/fetch-external-docs.py [--dry-run] [--source NAME]
"""

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "sync-config.json"


@dataclass
class DocInfo:
    """Information about a documentation file."""
    source_path: Path
    source_dir: Path
    slug: str
    images_dir: Optional[Path]


@dataclass
class SourceConfig:
    """Configuration for a documentation source."""
    name: str
    repo: str
    branch: str
    source_dir: str
    target_dir: str
    sparse_checkout: bool
    temp_dir: str


def load_config() -> list[SourceConfig]:
    """Load configuration from sync-config.json."""
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)

    return [
        SourceConfig(
            name=item['name'],
            repo=item['repo'],
            branch=item.get('branch', 'main'),
            source_dir=item['sourceDir'],
            target_dir=item['targetDir'],
            sparse_checkout=item.get('sparseCheckout', True),
            temp_dir=item.get('tempDir', f'.{item["name"]}-temp'),
        )
        for item in data.get('sources', [])
    ]


def run_command(cmd: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result


def clone_repository(config: SourceConfig, dry_run: bool = False) -> Path:
    """Clone a repository using sparse checkout if configured."""
    temp_path = PROJECT_ROOT / config.temp_dir

    if dry_run:
        print(f"  [DRY RUN] Would clone {config.repo} to {temp_path}")
        return temp_path

    if config.sparse_checkout:
        run_command([
            "git", "clone", "--depth", "1", "--sparse",
            config.repo, "--branch", config.branch, str(temp_path)
        ], cwd=PROJECT_ROOT)
        run_command(["git", "sparse-checkout", "init"], cwd=temp_path)
        run_command(["git", "sparse-checkout", "add", config.source_dir], cwd=temp_path)
    else:
        run_command([
            "git", "clone", "--depth", "1",
            config.repo, "--branch", config.branch, str(temp_path)
        ], cwd=PROJECT_ROOT)

    return temp_path


def discover_docs(source_base: Path) -> list[DocInfo]:
    """Discover all documentation files in the source directory."""
    docs = []

    if not source_base.exists():
        return docs

    for md_file in sorted(source_base.rglob('*.md')):
        if md_file.is_file():
            rel_path = md_file.relative_to(source_base)
            docs.append(DocInfo(
                source_path=md_file,
                source_dir=source_base,
                slug=str(rel_path),
                images_dir=None
            ))

    return docs


def transform_image_paths(content: str, slug: str) -> str:
    """Transform relative image paths to namespaced paths."""
    return re.sub(
        rf'!\[([^\]]*)\]\(images/(?!{re.escape(slug)}/)([^)]+)\)',
        rf'![\1](images/{slug}/\2)',
        content
    )


def copy_doc_with_images(doc: DocInfo, dest_base: Path, dry_run: bool = False) -> Path:
    """Copy a documentation file and its images to the destination."""
    content = doc.source_path.read_text(encoding='utf-8')
    transformed = transform_image_paths(content, doc.slug)
    dest_md = dest_base / doc.slug

    if dry_run:
        print(f"  [DRY RUN] Would copy {doc.source_path} -> {dest_md}")
        return dest_md

    dest_md.parent.mkdir(parents=True, exist_ok=True)
    dest_md.write_text(transformed, encoding='utf-8')

    if doc.images_dir and doc.images_dir.exists():
        dest_images = dest_base / "images" / doc.slug
        dest_images.mkdir(parents=True, exist_ok=True)
        for img in doc.images_dir.iterdir():
            if img.is_file() and img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
                shutil.copy2(img, dest_images / img.name)

    return dest_md


def sync_source(config: SourceConfig, dry_run: bool = False) -> None:
    """Sync documentation from a single source."""
    print(f"Syncing: {config.name}")

    temp_path = None
    try:
        temp_path = clone_repository(config, dry_run)
        source_path = temp_path / config.source_dir
        target_path = PROJECT_ROOT / config.target_dir

        if not dry_run and not source_path.exists():
            print(f"  Error: Source path does not exist: {source_path}")
            return

        docs = [] if dry_run else discover_docs(source_path)

        if not dry_run:
            if target_path.exists():
                shutil.rmtree(target_path)
            target_path.mkdir(parents=True, exist_ok=True)

        for doc in docs:
            copy_doc_with_images(doc, target_path, dry_run)

        if not dry_run:
            print(f"  Synced {len(docs)} doc(s) to {config.target_dir}")

    finally:
        if temp_path and temp_path.exists() and not dry_run:
            shutil.rmtree(temp_path)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch external documentation from configured repositories"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--source", type=str, help="Only sync a specific source by name")
    args = parser.parse_args()

    if args.dry_run:
        print("*** DRY RUN MODE ***\n")

    sources = load_config()

    if args.source:
        sources = [s for s in sources if s.name == args.source]
        if not sources:
            print(f"Error: Source '{args.source}' not found")
            return 1

    for source in sources:
        sync_source(source, args.dry_run)

    print("\nDone!")
    return 0


if __name__ == "__main__":
    exit(main())
