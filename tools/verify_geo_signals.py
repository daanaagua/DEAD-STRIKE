#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import load_library
from seo_geo_utils import detail_page_path

HOME = ROOT / "index.html"
LLMS = ROOT / "llms.txt"

REQUIRED_LLMS_SECTIONS = [
    "## Core Pages",
    "## Category Hubs",
    "## Specialized Hubs",
    "## Round-Two Tactical FPS",
    "## Round-Two Multiplayer Arena",
    "## Round-Two Sniper",
    "## Round-Two Zombie Defense",
    "## Trust Pages",
    "## Answer Pages",
    "## Key Facts",
]
STATIC_PAGE_EXPECTATIONS = [
    {
        "path": ROOT / "about" / "index.html",
        "canonical": "https://dead-strike.com/about/",
        "types": {"AboutPage", "Organization", "BreadcrumbList"},
    },
    {
        "path": ROOT / "contact" / "index.html",
        "canonical": "https://dead-strike.com/contact/",
        "types": {"ContactPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "privacy-policy" / "index.html",
        "canonical": "https://dead-strike.com/privacy-policy/",
        "types": {"WebPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "terms" / "index.html",
        "canonical": "https://dead-strike.com/terms/",
        "types": {"WebPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "editorial-policy" / "index.html",
        "canonical": "https://dead-strike.com/editorial-policy/",
        "types": {"WebPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "games" / "sniper-games" / "index.html",
        "canonical": "https://dead-strike.com/games/sniper-games/",
        "types": {"CollectionPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "games" / "zombie-defense-games" / "index.html",
        "canonical": "https://dead-strike.com/games/zombie-defense-games/",
        "types": {"CollectionPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "games" / "multiplayer-shooter-games" / "index.html",
        "canonical": "https://dead-strike.com/games/multiplayer-shooter-games/",
        "types": {"CollectionPage", "BreadcrumbList"},
    },
    {
        "path": ROOT / "dead-strike-controls-guide" / "index.html",
        "canonical": "https://dead-strike.com/dead-strike-controls-guide/",
        "types": {"Article", "BreadcrumbList", "FAQPage"},
    },
    {
        "path": ROOT / "dead-strike-tips" / "index.html",
        "canonical": "https://dead-strike.com/dead-strike-tips/",
        "types": {"Article", "BreadcrumbList"},
    },
    {
        "path": ROOT / "best-browser-zombie-fps-games" / "index.html",
        "canonical": "https://dead-strike.com/best-browser-zombie-fps-games/",
        "types": {"Article", "BreadcrumbList"},
    },
    {
        "path": ROOT / "best-sniper-browser-games" / "index.html",
        "canonical": "https://dead-strike.com/best-sniper-browser-games/",
        "types": {"Article", "BreadcrumbList"},
    },
    {
        "path": ROOT / "dead-strike-vs-other-browser-zombie-games" / "index.html",
        "canonical": "https://dead-strike.com/dead-strike-vs-other-browser-zombie-games/",
        "types": {"Article", "BreadcrumbList"},
    },
]
TAG_PATTERN = re.compile(r"<(meta|link)\b[^>]*>", re.I)
ATTR_PATTERN = re.compile(r'([:\w-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.I)
JSON_LD_PATTERN = re.compile(
    r'<script[^>]*type=(?:"application/ld\+json"|\'application/ld\+json\')[^>]*>(.*?)</script>',
    re.I | re.S,
)


def parse_tag_attributes(tag: str) -> dict[str, str]:
    attributes: dict[str, str] = {}
    for match in ATTR_PATTERN.finditer(tag):
        key = match.group(1).lower()
        value = next(group for group in match.groups()[1:] if group is not None)
        attributes[key] = value.strip()
    return attributes


def parse_json_ld(html: str) -> list[dict]:
    payloads: list[dict] = []
    for match in JSON_LD_PATTERN.finditer(html):
        raw = match.group(1).strip()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            payloads.extend(item for item in payload if isinstance(item, dict))
        elif isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def find_tag_attr(
    html: str,
    tag_name: str,
    attr_name: str,
    attr_value: str,
    return_attr: str,
) -> str | None:
    attr_name = attr_name.lower()
    attr_value = attr_value.lower()
    return_attr = return_attr.lower()

    for match in TAG_PATTERN.finditer(html):
        if match.group(1).lower() != tag_name.lower():
            continue
        attributes = parse_tag_attributes(match.group(0))
        if attributes.get(attr_name, "").lower() != attr_value:
            continue
        return attributes.get(return_attr)
    return None


def has_noindex(html: str) -> bool:
    robots = find_tag_attr(html, "meta", "name", "robots", "content")
    return isinstance(robots, str) and "noindex" in robots.lower()


def fail(errors: list[str]) -> int:
    print("GEO_SIGNAL_VERIFICATION_FAILED")
    for error in errors:
        print(f"- {error}")
    return 1


def verify_static_pages(errors: list[str]) -> None:
    for page in STATIC_PAGE_EXPECTATIONS:
        path = page["path"]
        if not path.exists():
            errors.append(f"missing static GEO page '{path}'")
            continue

        html = path.read_text(encoding="utf-8")
        canonical_href = find_tag_attr(html, "link", "rel", "canonical", "href")
        if canonical_href != page["canonical"]:
            errors.append(f"{path}: canonical must be {page['canonical']}")

        description = find_tag_attr(html, "meta", "name", "description", "content")
        if not description:
            errors.append(f"{path}: missing meta description")

        payloads = parse_json_ld(html)
        types = {payload.get("@type") for payload in payloads}
        for needed_type in page["types"]:
            if needed_type not in types:
                errors.append(f"{path}: missing {needed_type} structured data")

        breadcrumb = next((payload for payload in payloads if payload.get("@type") == "BreadcrumbList"), None)
        if breadcrumb is None:
            continue
        items = breadcrumb.get("itemListElement", [])
        if not isinstance(items, list) or len(items) < 2:
            errors.append(f"{path}: breadcrumb must contain at least Home and current page")
        elif items[-1].get("item") != page["canonical"]:
            errors.append(f"{path}: breadcrumb last item must match canonical")


def main() -> int:
    errors: list[str] = []
    library = load_library(ROOT / "game-library.js")

    home_html = HOME.read_text(encoding="utf-8")
    home_payloads = parse_json_ld(home_html)
    home_types = {payload.get("@type") for payload in home_payloads}
    for needed in ("WebSite", "VideoGame", "FAQPage", "Organization"):
        if needed not in home_types:
            errors.append(f"index.html missing {needed} structured data")

    llms_text = LLMS.read_text(encoding="utf-8")
    for section in REQUIRED_LLMS_SECTIONS:
        if section not in llms_text:
            errors.append(f"llms.txt missing section '{section}'")

    verify_static_pages(errors)

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
            errors.append(f"missing detail page file for slug '{slug}'")
            continue

        html = page_path.read_text(encoding="utf-8")
        if has_noindex(html):
            continue

        payloads = parse_json_ld(html)
        by_type = {payload.get("@type"): payload for payload in payloads}
        video_game = by_type.get("VideoGame")
        breadcrumb = by_type.get("BreadcrumbList")
        if video_game is None:
            errors.append(f"{page_path}: missing VideoGame structured data")
            continue
        if breadcrumb is None:
            errors.append(f"{page_path}: missing BreadcrumbList structured data")
            continue

        canonical_href = find_tag_attr(html, "link", "rel", "canonical", "href")
        if video_game.get("url") != canonical_href:
            errors.append(f"{page_path}: VideoGame.url must match canonical")
        if video_game.get("name") != game.get("title"):
            errors.append(f"{page_path}: VideoGame.name must match library title")
        if not video_game.get("description"):
            errors.append(f"{page_path}: VideoGame.description missing")
        if not video_game.get("image"):
            errors.append(f"{page_path}: VideoGame.image missing")
        publisher = video_game.get("publisher", {})
        if publisher.get("name") != "DEAD STRIKE":
            errors.append(f"{page_path}: VideoGame.publisher.name must be DEAD STRIKE")

        items = breadcrumb.get("itemListElement", [])
        if not isinstance(items, list) or len(items) < 3:
            errors.append(f"{page_path}: breadcrumb must contain at least Home, Games, and current page")
        elif items[-1].get("item") != canonical_href:
            errors.append(f"{page_path}: breadcrumb last item must match canonical")

    if errors:
        return fail(errors)

    print("GEO_SIGNAL_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
