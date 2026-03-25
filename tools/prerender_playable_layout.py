#!/usr/bin/env python3
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import game_page_paths, load_library


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = load_library(ROOT / "game-library.js")
GAMES = {game["slug"]: game for game in LIBRARY.get("games", []) if isinstance(game, dict) and isinstance(game.get("slug"), str)}


def canonical_slug(game):
    return game.get("canonicalSlug") or game["slug"]


def renderable_game(slug):
    game = GAMES.get(slug)
    if not game:
        return None
    return GAMES.get(canonical_slug(game), game)


def is_live(game):
    return bool(game and game.get("isLive"))


def get_pool(pool_name):
    value = LIBRARY.get("pools", {})
    for part in pool_name.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return value if isinstance(value, list) else []


def dedupe_games(slugs, exclude_slugs, limit):
    exclude = set(exclude_slugs)
    seen = set()
    results = []
    for slug in slugs:
        if len(results) >= limit or slug in exclude:
            continue
        game = GAMES.get(slug)
        if not is_live(game):
            continue
        game = renderable_game(slug)
        if not is_live(game):
            continue
        key = canonical_slug(game)
        if key in exclude or key in seen:
            continue
        seen.add(key)
        results.append(game)
    return results


def get_pool_games(pool_name, exclude_slugs, limit=12):
    combined = list(get_pool(pool_name))
    fill = LIBRARY.get("renderRules", {}).get("homePoolFillOrder", {}).get(pool_name, [])
    for fallback in fill:
        combined.extend(get_pool(fallback))
    return dedupe_games(combined, exclude_slugs, limit)


def get_related_games(slug, limit=12):
    current = GAMES.get(slug)
    if not current:
        return []

    current_renderable = renderable_game(slug)
    exclude = [canonical_slug(current_renderable)] if current_renderable else [slug]
    combined = list(current.get("related", []))
    categories = set(current.get("categories", []))
    rules = LIBRARY.get("renderRules", {})
    for rule in rules.get("categoryFallbackPriority", []):
        if rule.get("category") in categories and rule.get("pool"):
            combined.extend(get_pool(rule["pool"]))
    for pool_name in rules.get("terminalFallbackPools", []):
        combined.extend(get_pool(pool_name))
    return dedupe_games(combined, exclude, limit)


def player_strip_html(games):
    cards = []
    for game in games:
        cards.append(
            f'<a class="player-strip-card" href="{game["href"]}" aria-label="{game["title"]}">'
            f'<img src="{game["thumb"]}" alt="{game["title"]}" loading="lazy" decoding="async" />'
            f'<span class="sr-only">{game["title"]}</span>'
            f'</a>'
        )
    return '<div class="player-strip-grid">' + "".join(cards) + "</div>"


def sidebar_html(games):
    cards = []
    for game in games:
        cards.append(
            f'<a class="sidebar-icon-card" href="{game["href"]}" aria-label="{game["title"]}">'
            f'<img src="{game["thumb"]}" alt="{game["title"]}" loading="lazy" decoding="async" />'
            f'<span class="sr-only">{game["title"]}</span>'
            f'</a>'
        )
    return '<div class="sidebar-icon-grid">' + "".join(cards) + "</div>"


def build_compat_note(game):
    iframe_url = game.get("iframeUrl", game.get("href", "/"))
    title = game["title"]
    category_text = ", ".join(game.get("categories", [])[:2]).upper() or "SHOOTER"
    return (
        '<div class="compat-note">'
        '<div>'
        '<p class="compat-note-kicker">Mission briefing</p>'
        '<h2>Best in fullscreen or a dedicated tab.</h2>'
        f'<p>{title} runs best when you keep the play area wide and switch to the source tab if you want the cleanest loading path. Stay in the {category_text} lane, then jump sideways into more missions from the icon walls.</p>'
        '</div>'
        '<div class="compat-note-actions">'
        f'<a class="button button-primary" href="{iframe_url}" target="_blank" rel="noreferrer">Open Full Game</a>'
        '<a class="button button-ghost" href="/games/">Browse All Games</a>'
        '</div>'
        '</div>'
    )


def build_sidebar_sections(current_slug):
    popular = get_pool_games("popular", {current_slug})
    fresh = get_pool_games("fresh", {current_slug})
    return (
        '<section class="sidebar-icon-panel sidebar-icon-panel-flat">'
        '<div class="sidebar-panel-title"><h2>Popular Games</h2><span>🔥</span></div>'
        f'<div data-home-popular aria-label="Popular Games icon wall">{sidebar_html(popular)}</div>'
        '</section>'
        '<section class="sidebar-icon-panel sidebar-icon-panel-flat">'
        '<div class="sidebar-panel-title"><h2>New Games</h2><span>✨</span></div>'
        f'<div data-home-fresh aria-label="New Games icon wall">{sidebar_html(fresh)}</div>'
        '</section>'
    )


def update_home():
    path = ROOT / "index.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    current_slug = "dead-strike"
    strip = soup.select_one("[data-player-strip]")
    if strip:
        strip.clear()
        strip.append(BeautifulSoup(player_strip_html(get_pool_games("playerStrip", {current_slug})), "html.parser"))

    for selector, pool_name in (("[data-home-popular]", "popular"), ("[data-home-fresh]", "fresh")):
        node = soup.select_one(selector)
        if node:
            node.clear()
            node.append(BeautifulSoup(sidebar_html(get_pool_games(pool_name, {current_slug})), "html.parser"))

    for panel in soup.select("section.sidebar-icon-panel"):
        classes = set(panel.get("class", []))
        classes.add("sidebar-icon-panel-flat")
        panel["class"] = list(classes)

    path.write_text(str(soup), encoding="utf-8")


def update_detail_page(path):
    slug = path.parent.name
    game = GAMES[slug]
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")

    strip = soup.select_one("[data-player-strip]")
    if strip:
        strip.clear()
        strip.append(BeautifulSoup(player_strip_html(get_related_games(slug)), "html.parser"))

    titlebar = soup.select_one(".arcade-titlebar")
    if titlebar:
        compat = titlebar.find_next_sibling(class_="compat-note")
        if compat is None:
            titlebar.insert_after(BeautifulSoup(build_compat_note(game), "html.parser"))

    aside = soup.select_one("aside.arcade-sidebar")
    if aside:
        aside.clear()
        aside.append(BeautifulSoup(build_sidebar_sections(slug), "html.parser"))

    path.write_text(str(soup), encoding="utf-8")


def main():
    update_home()
    for path in game_page_paths(ROOT, LIBRARY, live_only=True, include_home=False):
        update_detail_page(path)


if __name__ == "__main__":
    main()
