#!/usr/bin/env python3
"""
Fetch external documentation from configured repositories.

This script clones external repositories and syncs their documentation
to the local docs directory, similar to how the DHIS2 developer-portal
handles multi-repo documentation.

Usage:
    python scripts/fetch-external-docs.py [--dry-run] [--source NAME]

Examples:
    # Fetch all configured sources
    python scripts/fetch-external-docs.py

    # Preview what will be done
    python scripts/fetch-external-docs.py --dry-run

    # Fetch only a specific source
    python scripts/fetch-external-docs.py --source modeling-app
"""

import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

# Script directory for resolving relative paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "sync-config.json"
MKDOCS_FILE = PROJECT_ROOT / "mkdocs.yml"


@dataclass
class DocInfo:
    """Information about a documentation file."""
    source_path: Path
    source_dir: Path
    slug: str
    title: str
    order: int
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
    nav_section: str
    preserve_nav_entries: list[str]


def load_config() -> list[SourceConfig]:
    """Load configuration from sync-config.json."""
    with open(CONFIG_FILE, 'r') as f:
        data = json.load(f)

    sources = []
    for item in data.get('sources', []):
        sources.append(SourceConfig(
            name=item['name'],
            repo=item['repo'],
            branch=item.get('branch', 'main'),
            source_dir=item['sourceDir'],
            target_dir=item['targetDir'],
            sparse_checkout=item.get('sparseCheckout', True),
            temp_dir=item.get('tempDir', f'.{item["name"]}-temp'),
            nav_section=item.get('navSection', item['name']),
            preserve_nav_entries=item.get('preserveNavEntries', [])
        ))

    return sources


def run_command(cmd: str, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"  $ {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        print(f"    Error: {result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result


def clone_repository(config: SourceConfig, dry_run: bool = False) -> Path:
    """Clone a repository using sparse checkout if configured."""
    temp_path = PROJECT_ROOT / config.temp_dir

    if dry_run:
        print(f"  [DRY RUN] Would clone {config.repo} to {temp_path}")
        return temp_path

    # Remove any previous temp directory
    if temp_path.exists():
        shutil.rmtree(temp_path)

    # Clone with sparse checkout
    if config.sparse_checkout:
        clone_cmd = f"git clone --depth 1 --sparse {config.repo} --branch {config.branch} {temp_path}"
        run_command(clone_cmd, cwd=PROJECT_ROOT)

        # Set up sparse checkout for the docs directory
        run_command("git sparse-checkout init", cwd=temp_path)
        run_command(f"git sparse-checkout add {config.source_dir}", cwd=temp_path)
    else:
        clone_cmd = f"git clone --depth 1 {config.repo} --branch {config.branch} {temp_path}"
        run_command(clone_cmd, cwd=PROJECT_ROOT)

    return temp_path


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        import yaml
        try:
            fm = yaml.safe_load(match.group(1))
            body = match.group(2)
            return fm or {}, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def discover_docs(source_base: Path) -> list[DocInfo]:
    """
    Discover all documentation files in the source directory.

    Looks for index.md or index.mdx files in subdirectories.
    """
    docs = []

    if not source_base.exists():
        return docs

    for subdir in sorted(source_base.iterdir()):
        if not subdir.is_dir():
            continue

        # Look for index.md or index.mdx
        index_path = None
        for ext in ['.md', '.mdx']:
            candidate = subdir / f"index{ext}"
            if candidate.exists():
                index_path = candidate
                break

        if not index_path:
            continue

        content = index_path.read_text(encoding='utf-8')
        fm, _ = parse_frontmatter(content)

        # Get title from frontmatter or derive from directory name
        title = fm.get('title', subdir.name.replace('-', ' ').title())
        order = fm.get('order', 999)

        images_dir = subdir / "images"

        docs.append(DocInfo(
            source_path=index_path,
            source_dir=subdir,
            slug=subdir.name,
            title=title,
            order=order,
            images_dir=images_dir if images_dir.exists() else None
        ))

    # Sort by order, then alphabetically by slug
    return sorted(docs, key=lambda d: (d.order, d.slug))


def transform_image_paths(content: str, slug: str) -> str:
    """
    Transform relative image paths to namespaced paths.

    Converts:
        ![alt](./images/foo.png) -> ![alt](images/{slug}/foo.png)
        ![alt](images/foo.png) -> ![alt](images/{slug}/foo.png)
    """
    # Pattern with leading ./
    content = re.sub(
        r'!\[([^\]]*)\]\(\./images/([^)]+)\)',
        rf'![\1](images/{slug}/\2)',
        content
    )

    # Pattern without leading ./ (but not already namespaced with slug)
    content = re.sub(
        rf'!\[([^\]]*)\]\(images/(?!{re.escape(slug)}/)([^)]+)\)',
        rf'![\1](images/{slug}/\2)',
        content
    )

    return content


def copy_doc_with_images(doc: DocInfo, dest_base: Path, dry_run: bool = False) -> Path:
    """
    Copy a documentation file and its images to the destination.

    Returns:
        Path to the copied markdown file
    """
    # Read and transform content
    content = doc.source_path.read_text(encoding='utf-8')
    _, body = parse_frontmatter(content)

    # Transform image paths in body
    transformed_body = transform_image_paths(body, doc.slug)

    # Destination path
    dest_md = dest_base / f"{doc.slug}.md"

    if dry_run:
        print(f"    [DRY RUN] Would copy {doc.source_path} -> {dest_md}")
        return dest_md

    # Write markdown file (body only, frontmatter stripped for MkDocs)
    dest_md.write_text(transformed_body, encoding='utf-8')

    # Copy images if they exist
    if doc.images_dir and doc.images_dir.exists():
        dest_images = dest_base / "images" / doc.slug
        dest_images.mkdir(parents=True, exist_ok=True)

        for img in doc.images_dir.iterdir():
            if img.is_file() and img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
                shutil.copy2(img, dest_images / img.name)

    return dest_md


def update_mkdocs_nav(
    mkdocs_path: Path,
    nav_section: str,
    synced_docs: list[DocInfo],
    target_dir: str,
    preserve_entries: list[str],
    dry_run: bool = False
) -> None:
    """
    Update a navigation section in mkdocs.yml.

    Uses text-based replacement to preserve exact YAML formatting.
    """
    content = mkdocs_path.read_text(encoding='utf-8')

    # Find the section header and detect its indentation
    header_pattern = rf'^(\s*)- {re.escape(nav_section)}:\n'
    header_match = re.search(header_pattern, content, re.MULTILINE)

    if not header_match:
        print(f"  Warning: Could not find '{nav_section}' section in mkdocs.yml nav")
        return

    header_indent = header_match.group(1)
    header_end = header_match.end()

    # Items under the section should have 2 more spaces than the header
    item_indent = header_indent + '  '

    # Find all items under this section
    lines = content[header_end:].split('\n')
    section_lines = []
    for line in lines:
        if line.startswith(item_indent + '- '):
            section_lines.append(line)
        elif line.strip() == '':
            continue
        elif line.startswith(header_indent + '- ') or (line.strip() and not line.startswith(item_indent)):
            break

    # Calculate end position of the section
    if section_lines:
        section_end = header_end + content[header_end:].find(section_lines[-1]) + len(section_lines[-1]) + 1
    else:
        section_end = header_end

    # Build new entries
    new_lines = []

    # First, find and preserve entries that should be kept
    for line in section_lines:
        entry_match = re.match(rf'^{re.escape(item_indent)}-\s+([^:]+):\s*(.+)$', line)
        if entry_match:
            path = entry_match.group(2).strip()
            filename = Path(path).name
            if filename in preserve_entries:
                new_lines.append(line)

    # Add synced docs
    # Remove 'docs/' prefix from target_dir for MkDocs navigation (paths are relative to docs/)
    mkdocs_nav_path = target_dir.replace('docs/', '', 1) if target_dir.startswith('docs/') else target_dir
    for doc in synced_docs:
        nav_path = f"{mkdocs_nav_path}/{doc.slug}.md"
        new_lines.append(f"{item_indent}- {doc.title}: {nav_path}")

    # Build replacement
    new_section = header_match.group(0) + '\n'.join(new_lines) + '\n'

    # Replace in content
    new_content = content[:header_match.start()] + new_section + content[section_end:]

    if dry_run:
        print(f"  [DRY RUN] Would update navigation in {mkdocs_path}")
        return

    mkdocs_path.write_text(new_content, encoding='utf-8')


def sync_source(config: SourceConfig, dry_run: bool = False) -> None:
    """Sync documentation from a single source."""
    print(f"\n{'='*60}")
    print(f"Syncing: {config.name}")
    print(f"  Repo: {config.repo}")
    print(f"  Branch: {config.branch}")
    print(f"  Source: {config.source_dir}")
    print(f"  Target: {config.target_dir}")
    print(f"{'='*60}")

    temp_path = None
    try:
        # Clone the repository
        print("\n1. Cloning repository...")
        temp_path = clone_repository(config, dry_run)

        # Source path within the cloned repo
        source_path = temp_path / config.source_dir
        target_path = PROJECT_ROOT / config.target_dir

        if not dry_run and not source_path.exists():
            print(f"  Error: Source path does not exist: {source_path}")
            return

        # Discover documentation
        print("\n2. Discovering documentation...")
        if dry_run:
            print("  [DRY RUN] Would scan for documentation")
            docs = []
        else:
            docs = discover_docs(source_path)
            print(f"  Found {len(docs)} document(s):")
            for doc in docs:
                print(f"    - {doc.slug} (order: {doc.order}, title: \"{doc.title}\")")
                if doc.images_dir:
                    image_count = len([f for f in doc.images_dir.iterdir() if f.is_file()])
                    print(f"      └── {image_count} image(s)")

        # Ensure target directory exists
        if not dry_run:
            target_path.mkdir(parents=True, exist_ok=True)

        # Copy docs and images
        print("\n3. Copying documentation...")
        for doc in docs:
            dest_path = copy_doc_with_images(doc, target_path, dry_run)
            if not dry_run:
                print(f"  Synced: {dest_path.name}")
                if doc.images_dir:
                    image_count = len([f for f in doc.images_dir.iterdir() if f.is_file()])
                    print(f"    └── {image_count} image(s) copied")

        # Update navigation
        print("\n4. Updating navigation...")
        update_mkdocs_nav(
            MKDOCS_FILE,
            config.nav_section,
            docs,
            config.target_dir,
            config.preserve_nav_entries,
            dry_run
        )
        if not dry_run:
            print("  Navigation updated successfully")

    finally:
        # Clean up temp directory
        if temp_path and temp_path.exists() and not dry_run:
            print("\n5. Cleaning up...")
            shutil.rmtree(temp_path)
            print(f"  Removed {temp_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch external documentation from configured repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Only sync a specific source by name"
    )
    args = parser.parse_args()

    print("Fetch External Documentation")
    print(f"Config: {CONFIG_FILE}")
    print(f"MkDocs: {MKDOCS_FILE}")

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***")

    # Load configuration
    sources = load_config()
    print(f"\nConfigured sources: {len(sources)}")
    for src in sources:
        print(f"  - {src.name}: {src.repo}")

    # Filter sources if specified
    if args.source:
        sources = [s for s in sources if s.name == args.source]
        if not sources:
            print(f"\nError: Source '{args.source}' not found in configuration")
            return 1

    # Sync each source
    for source in sources:
        sync_source(source, args.dry_run)

    print("\n" + "="*60)
    print("Sync complete!")
    print("="*60)
    return 0


if __name__ == "__main__":
    exit(main())
