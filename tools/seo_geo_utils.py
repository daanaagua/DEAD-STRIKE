#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Any


SITE_ORIGIN = "https://dead-strike.com"
PUBLISHER = {
    "@type": "Organization",
    "name": "DEAD STRIKE",
    "url": f"{SITE_ORIGIN}/",
}
CATEGORY_PRIORITY = ["zombie-games", "fps-games", "shooter-games"]


def title_case_label(value: str) -> str:
    return value.replace("-", " ").title()


def play_mode_for_categories(categories: list[str]) -> str:
    multiplayer_tokens = {"multiplayer", "io", "pvp", "co-op", "arena"}
    return "MultiPlayer" if any(category in multiplayer_tokens for category in categories) else "SinglePlayer"


def category_page_for_slug(library: dict[str, Any], slug: str) -> dict[str, Any] | None:
    category_pages = library.get("categoryPages", {})
    if not isinstance(category_pages, dict):
        return None

    for page_slug in CATEGORY_PRIORITY:
        page = category_pages.get(page_slug)
        if not isinstance(page, dict):
            continue
        slugs = page.get("slugs")
        if isinstance(slugs, list) and slug in slugs:
            return page
    return None


def build_detail_schema_objects(
    game: dict[str, Any],
    library: dict[str, Any],
    *,
    canonical_url: str,
    description: str,
    image_url: str,
) -> list[dict[str, Any]]:
    category_page = category_page_for_slug(library, game["slug"])
    breadcrumb_items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": f"{SITE_ORIGIN}/",
        },
        {
            "@type": "ListItem",
            "position": 2,
            "name": "Games",
            "item": f"{SITE_ORIGIN}/games/",
        },
    ]

    current_position = 3
    if category_page:
        breadcrumb_items.append(
            {
                "@type": "ListItem",
                "position": 3,
                "name": category_page["title"],
                "item": f"{SITE_ORIGIN}{category_page['href']}",
            }
        )
        current_position = 4

    breadcrumb_items.append(
        {
            "@type": "ListItem",
            "position": current_position,
            "name": game["title"],
            "item": canonical_url,
        }
    )

    categories = [category for category in game.get("categories", []) if isinstance(category, str)]
    video_game = {
        "@context": "https://schema.org",
        "@type": "VideoGame",
        "name": game["title"],
        "url": canonical_url,
        "image": image_url,
        "description": description,
        "genre": [title_case_label(category) for category in categories[:4]] or ["Shooter"],
        "gamePlatform": ["Web Browser"],
        "playMode": play_mode_for_categories(categories),
        "operatingSystem": "Any",
        "publisher": PUBLISHER,
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumb_items,
    }
    return [video_game, breadcrumb]


def render_json_ld_script(data: dict[str, Any]) -> str:
    payload = json.dumps(data, indent=2).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{payload}\n</script>'


def render_detail_schema_block(
    game: dict[str, Any],
    library: dict[str, Any],
    *,
    canonical_url: str,
    description: str,
    image_url: str,
) -> str:
    scripts = [
        render_json_ld_script(schema)
        for schema in build_detail_schema_objects(
            game,
            library,
            canonical_url=canonical_url,
            description=description,
            image_url=image_url,
        )
    ]
    return "\n".join(
        ["<!-- GEO_DETAIL_SCHEMA_START -->", *scripts, "<!-- GEO_DETAIL_SCHEMA_END -->"]
    )


def detail_page_path(repo_root: Path, slug: str) -> Path:
    return repo_root / slug / "index.html"
