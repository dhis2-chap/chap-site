#!/usr/bin/env python3
"""
Fetch external documentation from configured repositories.

This script clones external repositories and syncs their documentation
to the local docs directory. It also merges nav items from external
mkdocs.yml files into the main mkdocs.yml.

Usage:
    python scripts/fetch-external-docs.py [--dry-run] [--source NAME]
"""

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any

from ruamel.yaml import YAML

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
    mkdocs_yml: Optional[str] = None
    nav_placeholder: Optional[str] = None


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
            mkdocs_yml=item.get('mkdocsYml'),
            nav_placeholder=item.get('navPlaceholder'),
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

    if temp_path.exists():
        shutil.rmtree(temp_path)

    if config.sparse_checkout:
        run_command([
            "git", "clone", "--depth", "1", "--sparse",
            config.repo, "--branch", config.branch, str(temp_path)
        ], cwd=PROJECT_ROOT)
        run_command(["git", "sparse-checkout", "init"], cwd=temp_path)
        run_command(["git", "sparse-checkout", "add", config.source_dir], cwd=temp_path)
        # Also checkout mkdocs.yml if configured
        if config.mkdocs_yml:
            run_command(["git", "sparse-checkout", "add", config.mkdocs_yml], cwd=temp_path)
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

    # Find all markdown files recursively
    for md_file in sorted(source_base.rglob('*.md')):
        if md_file.is_file():
            # Calculate relative path from source_base
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
    # Preserve directory structure using slug (which is now relative path)
    dest_md = dest_base / doc.slug

    if dry_run:
        print(f"  [DRY RUN] Would copy {doc.source_path} -> {dest_md}")
        return dest_md

    # Create parent directories if needed
    dest_md.parent.mkdir(parents=True, exist_ok=True)
    dest_md.write_text(transformed, encoding='utf-8')

    if doc.images_dir and doc.images_dir.exists():
        dest_images = dest_base / "images" / doc.slug
        dest_images.mkdir(parents=True, exist_ok=True)
        for img in doc.images_dir.iterdir():
            if img.is_file() and img.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'):
                shutil.copy2(img, dest_images / img.name)

    return dest_md


def transform_nav_paths(nav: Any, prefix: str) -> Any:
    """Recursively transform nav paths by adding a prefix."""
    if isinstance(nav, list):
        return [transform_nav_paths(item, prefix) for item in nav]
    elif isinstance(nav, dict):
        result = {}
        for key, value in nav.items():
            if isinstance(value, str):
                # This is a path - add prefix
                result[key] = f"{prefix}/{value}"
            else:
                # This is a nested structure
                result[key] = transform_nav_paths(value, prefix)
        return result
    elif isinstance(nav, str):
        return f"{prefix}/{nav}"
    return nav


def inject_nav_into_mkdocs(config: SourceConfig, temp_path: Path, dry_run: bool = False) -> None:
    """Read nav from external mkdocs.yml and inject into main mkdocs.yml."""
    if not config.mkdocs_yml:
        return

    external_mkdocs_path = temp_path / config.mkdocs_yml
    if not external_mkdocs_path.exists():
        print(f"  Warning: External mkdocs.yml not found at {external_mkdocs_path}")
        return

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=2, offset=2)
    yaml.width = float('inf')

    # Read external mkdocs.yml
    with open(external_mkdocs_path, 'r') as f:
        external_config = yaml.load(f)

    external_nav = external_config.get('nav', [])
    if not external_nav:
        print(f"  Warning: No nav found in external mkdocs.yml")
        return

    # Transform paths to include target directory prefix
    # Remove 'docs/' prefix from target_dir for nav paths
    nav_prefix = config.target_dir.replace('docs/', '')
    transformed_nav = transform_nav_paths(external_nav, nav_prefix)

    # Always generate sub-nav HTML for main.html template
    inject_subnav_into_template(external_nav, nav_prefix, dry_run)

    # Only inject into mkdocs.yml if placeholder is configured
    if not config.nav_placeholder:
        return

    if dry_run:
        print(f"  [DRY RUN] Would inject {len(external_nav)} nav items into mkdocs.yml")
        return

    # Read main mkdocs.yml as text to find placeholder indentation
    with open(MKDOCS_FILE, 'r') as f:
        mkdocs_content = f.read()

    # Find the placeholder line and its indentation
    placeholder_line = None
    base_indent = ""
    for line in mkdocs_content.split('\n'):
        if config.nav_placeholder in line:
            placeholder_line = line
            # Get indentation of the placeholder (the comment itself)
            base_indent = line[:len(line) - len(line.lstrip())]
            break

    if not placeholder_line:
        print(f"  Note: Placeholder '{config.nav_placeholder}' not found in mkdocs.yml (nav may already be hardcoded)")
        return

    # Generate YAML for each nav item separately to control indentation
    from io import StringIO
    nav_lines = []
    for item in transformed_nav:
        stream = StringIO()
        yaml.dump([item], stream)
        item_yaml = stream.getvalue().strip()
        # Add proper indentation to each line (same as placeholder)
        for line in item_yaml.split('\n'):
            nav_lines.append(base_indent + line)

    # Replace placeholder with nav items
    new_content = mkdocs_content.replace(placeholder_line, '\n'.join(nav_lines))

    with open(MKDOCS_FILE, 'w') as f:
        f.write(new_content)

    print(f"  Injected {len(external_nav)} nav items into mkdocs.yml")


def inject_subnav_into_template(nav: list, prefix: str, dry_run: bool = False) -> None:
    """Generate horizontal sub-nav HTML and inject into main.html template."""
    template_path = PROJECT_ROOT / "docs" / "overrides" / "main.html"

    if not template_path.exists():
        print(f"  Warning: Template not found at {template_path}")
        return

    # Extract top-level nav items for sub-nav
    subnav_items = []
    for item in nav:
        if isinstance(item, dict):
            for label, value in item.items():
                if isinstance(value, str):
                    # Simple item: "Home: index.md"
                    url = f"{prefix}/{value}"
                    url_check = value.replace('.md', '').replace('index', '')
                    subnav_items.append((label, url, url_check))
                elif isinstance(value, list):
                    # Nested item: get the first child's URL
                    first_child = value[0] if value else None
                    if first_child:
                        if isinstance(first_child, dict):
                            for _, child_value in first_child.items():
                                if isinstance(child_value, str):
                                    url = f"{prefix}/{child_value}"
                                    # Use folder name for URL check
                                    folder = child_value.split('/')[0] if '/' in child_value else child_value
                                    subnav_items.append((label, url, folder))
                                    break
                        elif isinstance(first_child, str):
                            url = f"{prefix}/{first_child}"
                            folder = first_child.split('/')[0] if '/' in first_child else first_child
                            subnav_items.append((label, url, folder))

    if dry_run:
        print(f"  [DRY RUN] Would inject {len(subnav_items)} sub-nav items into main.html")
        return

    # Generate HTML for sub-nav using same structure as root tabs
    html_lines = []
    for i, (label, url, url_check) in enumerate(subnav_items):
        # Remove .md extension and index for cleaner URLs
        clean_url = url.replace('.md', '').replace('/index', '/')
        if not clean_url.endswith('/'):
            clean_url += '/'

        # For active state: use exact match for Home, folder match for others
        if i == 0:  # Home item
            active_check = f'page.url == "{prefix}/" or page.url == "{prefix}/index.html"'
        else:
            # Check if URL starts with this section but not other sections
            active_check = f'"{prefix}/{url_check}" in page.url and page.url != "{prefix}/"'

        html_lines.append(
            f'      <li class="doc-subnav__item"><a href="{{{{ \'{clean_url}\' | url }}}}" '
            f'{{% if {active_check} %}}class="active"{{% endif %}}>{label}</a></li>'
        )

    subnav_html = '\n'.join(html_lines)

    # Read and update template
    with open(template_path, 'r') as f:
        template_content = f.read()

    placeholder = "<!-- DOC_SUBNAV_PLACEHOLDER -->"
    path_placeholder = "DOC_SUBNAV_PATH_PLACEHOLDER"

    if placeholder not in template_content:
        print(f"  Warning: Sub-nav placeholder not found in main.html")
        return

    # Replace both placeholders
    new_content = template_content.replace(placeholder, subnav_html)
    new_content = new_content.replace(path_placeholder, prefix)

    with open(template_path, 'w') as f:
        f.write(new_content)

    print(f"  Injected {len(subnav_items)} sub-nav items into main.html")


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

        # Inject nav if configured
        inject_nav_into_mkdocs(config, temp_path, dry_run)

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
