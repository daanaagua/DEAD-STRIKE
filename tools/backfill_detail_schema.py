#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import load_library
from seo_geo_utils import detail_page_path, render_detail_schema_block

DETAIL_SCHEMA_PATTERN = re.compile(
    r"\n?<!-- GEO_DETAIL_SCHEMA_START -->.*?<!-- GEO_DETAIL_SCHEMA_END -->\n?",
    re.S,
)
TAG_PATTERN = re.compile(r"<(meta|link)\b[^>]*>", re.I)
ATTR_PATTERN = re.compile(r'([:\w-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.I)


def parse_tag_attributes(tag: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for match in ATTR_PATTERN.finditer(tag):
        key = match.group(1).lower()
        value = next(group for group in match.groups()[1:] if group is not None)
        attributes[key] = value.strip()
    return attributes


def require_tag_attr(
    html: str,
    tag_name: str,
    attr_name: str,
    attr_value: str,
    return_attr: str,
    label: str,
    slug: str,
) -> str:
    attr_name = attr_name.lower()
    attr_value = attr_value.lower()
    return_attr = return_attr.lower()

    for match in TAG_PATTERN.finditer(html):
        if match.group(1).lower() != tag_name.lower():
            continue
        attributes = parse_tag_attributes(match.group(0))
        if attributes.get(attr_name, "").lower() != attr_value:
            continue
        value = attributes.get(return_attr)
        if value:
            return value.strip()

    raise ValueError(f"{slug}: missing {label}")


def require_robots_content(html: str, slug: str) -> str:
    for match in TAG_PATTERN.finditer(html):
        if match.group(1).lower() != "meta":
            continue
        attributes = parse_tag_attributes(match.group(0))
        if attributes.get("name", "").lower() == "robots":
            content = attributes.get("content")
            if content:
                return content.strip()
            break

    raise ValueError(f"{slug}: missing robots meta")


def is_noindex_page(html: str, slug: str) -> bool:
    try:
        robots = require_robots_content(html, slug)
    except ValueError:
        return False
    return "noindex" in robots.lower()


def upsert_detail_schema(html: str, schema_block: str) -> str:
    if DETAIL_SCHEMA_PATTERN.search(html):
        return DETAIL_SCHEMA_PATTERN.sub("\n" + schema_block + "\n", html, count=1)
    if "</head>" not in html:
        raise ValueError("missing </head> tag")
    return html.replace("</head>", f"\n{schema_block}\n</head>", 1)


def main() -> int:
    library = load_library(ROOT / "game-library.js")
    updated = 0

    for game in library.get("games", []):
        if not isinstance(game, dict):
            continue

        slug = game.get("slug")
        href = game.get("href")
        canonical_slug = game.get("canonicalSlug")
        if not isinstance(slug, str) or not isinstance(href, str):
            continue
        if href == "/" or (isinstance(canonical_slug, str) and canonical_slug and canonical_slug != slug):
            continue

        page_path = detail_page_path(ROOT, slug)
        if not page_path.exists():
            continue

        html = page_path.read_text(encoding="utf-8")
        if is_noindex_page(html, slug):
            continue

        canonical_url = require_tag_attr(
            html,
            "link",
            "rel",
            "canonical",
            "href",
            "canonical link",
            slug,
        )
        description = require_tag_attr(
            html,
            "meta",
            "name",
            "description",
            "content",
            "meta description",
            slug,
        )
        image_url = require_tag_attr(
            html,
            "meta",
            "property",
            "og:image",
            "content",
            "og:image",
            slug,
        )

        schema_block = render_detail_schema_block(
            game,
            library,
            canonical_url=canonical_url,
            description=description,
            image_url=image_url,
        )
        updated_html = upsert_detail_schema(html, schema_block)
        if updated_html != html:
            page_path.write_text(updated_html, encoding="utf-8")
            updated += 1

    print(f"DETAIL_SCHEMA_BACKFILLED: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
