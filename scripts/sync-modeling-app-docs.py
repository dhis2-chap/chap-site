#!/usr/bin/env python3
"""
Sync documentation from chap-frontend modeling app to chap-site.

This script copies markdown documentation from the modeling app's user-guides
folder to the chap-site documentation, transforming file paths and automatically
updating the mkdocs.yml navigation.

Usage:
    python scripts/sync-modeling-app-docs.py [--dry-run] [--source PATH] [--dest PATH]

Examples:
    # Preview what will be synced
    python scripts/sync-modeling-app-docs.py --dry-run

    # Run the sync
    python scripts/sync-modeling-app-docs.py
"""

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

# Default configuration - adjust these paths as needed
DEFAULT_SOURCE = Path(__file__).parent.parent.parent / "chap-frontend/apps/modeling-app/docs/user-guides"
DEFAULT_DEST = Path(__file__).parent.parent / "docs/guides/using-the-modeling-app"
DEFAULT_MKDOCS = Path(__file__).parent.parent / "mkdocs.yml"

# Navigation entries to preserve (won't be removed during sync)
PRESERVE_NAV_ENTRIES = ["getting-started.md"]


@dataclass
class DocInfo:
    """Information about a documentation file."""
    source_path: Path
    source_dir: Path
    slug: str
    title: str
    order: int
    images_dir: Optional[Path]


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


def discover_source_docs(source_base: Path) -> list[DocInfo]:
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
    # Use negative lookahead to avoid matching already-transformed paths
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
    fm, body = parse_frontmatter(content)

    # Transform image paths in body
    transformed_body = transform_image_paths(body, doc.slug)

    # Destination path
    dest_md = dest_base / f"{doc.slug}.md"

    if not dry_run:
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


def update_mkdocs_nav(mkdocs_path: Path, synced_docs: list[DocInfo], preserve_entries: list[str], dry_run: bool = False) -> None:
    """
    Update the 'Using the modeling app' section in mkdocs.yml navigation.

    Uses text-based replacement to preserve exact YAML formatting.
    """
    content = mkdocs_path.read_text(encoding='utf-8')

    # Find the "Using the modeling app:" section header and detect its indentation
    header_pattern = r'^(\s*)- Using the modeling app:\n'
    header_match = re.search(header_pattern, content, re.MULTILINE)

    if not header_match:
        raise ValueError("Could not find 'Using the modeling app' section in mkdocs.yml nav")

    header_indent = header_match.group(1)
    header_end = header_match.end()

    # Items under "Using the modeling app" should have 2 more spaces than the header
    item_indent = header_indent + '  '

    # Find all items under this section (lines starting with item_indent + '- ')
    # Stop when we hit a line with less or equal indentation to the header
    lines = content[header_end:].split('\n')
    section_lines = []
    for line in lines:
        # Check if line is an item at our expected indentation
        if line.startswith(item_indent + '- '):
            section_lines.append(line)
        elif line.strip() == '':
            # Empty lines might be between items, continue
            continue
        elif line.startswith(header_indent + '- ') or (line.strip() and not line.startswith(item_indent)):
            # Hit next sibling section or different indentation, stop
            break

    # Calculate end position of the section we're replacing
    section_text = '\n'.join(section_lines) + '\n'
    section_end = header_end + content[header_end:].find(section_lines[-1]) + len(section_lines[-1]) + 1 if section_lines else header_end

    # Build new entries
    new_lines = []

    # First, find and preserve entries that should be kept
    for line in section_lines:
        entry_match = re.match(rf'^{re.escape(item_indent)}-\s+([^:]+):\s*(.+)$', line)
        if entry_match:
            title = entry_match.group(1).strip()
            path = entry_match.group(2).strip()
            filename = Path(path).name
            if filename in preserve_entries:
                new_lines.append(f"{item_indent}- {title}: {path}")

    # Add synced docs
    for doc in synced_docs:
        nav_path = f"guides/using-the-modeling-app/{doc.slug}.md"
        new_lines.append(f"{item_indent}- {doc.title}: {nav_path}")

    # Build replacement
    new_section = header_match.group(0) + '\n'.join(new_lines) + '\n'

    # Replace in content
    new_content = content[:header_match.start()] + new_section + content[section_end:]

    if not dry_run:
        mkdocs_path.write_text(new_content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Sync modeling app documentation to chap-site",
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
        type=Path,
        default=DEFAULT_SOURCE,
        help=f"Source directory (default: {DEFAULT_SOURCE})"
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help=f"Destination directory (default: {DEFAULT_DEST})"
    )
    parser.add_argument(
        "--mkdocs",
        type=Path,
        default=DEFAULT_MKDOCS,
        help=f"Path to mkdocs.yml (default: {DEFAULT_MKDOCS})"
    )
    args = parser.parse_args()

    # Resolve paths
    source = args.source.resolve()
    dest = args.dest.resolve()
    mkdocs_path = args.mkdocs.resolve()

    print(f"Source:      {source}")
    print(f"Destination: {dest}")
    print(f"mkdocs.yml:  {mkdocs_path}")
    print()

    # Validate paths
    if not source.exists():
        print(f"Error: Source directory does not exist: {source}")
        return 1

    if not mkdocs_path.exists():
        print(f"Error: mkdocs.yml not found: {mkdocs_path}")
        return 1

    # Discover source docs
    print("Scanning source directory...")
    docs = discover_source_docs(source)

    if not docs:
        print("No documentation found to sync")
        return 0

    print(f"Found {len(docs)} document(s):")
    for doc in docs:
        print(f"  - {doc.slug} (order: {doc.order}, title: \"{doc.title}\")")
        if doc.images_dir:
            image_count = len([f for f in doc.images_dir.iterdir() if f.is_file()])
            print(f"    └── {image_count} image(s)")
    print()

    if args.dry_run:
        print("[DRY RUN] Would perform the following actions:")
        print()
        for doc in docs:
            print(f"  Copy: {doc.source_path}")
            print(f"    -> {dest / f'{doc.slug}.md'}")
            if doc.images_dir:
                print(f"  Copy images: {doc.images_dir}")
                print(f"    -> {dest / 'images' / doc.slug}")
        print()
        print(f"  Update navigation in: {mkdocs_path}")
        print()
        return 0

    # Ensure destination exists
    dest.mkdir(parents=True, exist_ok=True)

    # Copy docs and images
    print("Syncing documentation...")
    for doc in docs:
        dest_path = copy_doc_with_images(doc, dest, dry_run=args.dry_run)
        print(f"  Synced: {dest_path.name}")
        if doc.images_dir:
            image_count = len([f for f in doc.images_dir.iterdir() if f.is_file()])
            print(f"    └── {image_count} image(s) copied")
    print()

    # Update navigation
    print(f"Updating navigation in {mkdocs_path}...")
    update_mkdocs_nav(mkdocs_path, docs, PRESERVE_NAV_ENTRIES, dry_run=args.dry_run)
    print("Navigation updated successfully")
    print()

    print("Sync complete!")
    return 0


if __name__ == "__main__":
    exit(main())
