#!/usr/bin/env python3
import re
import sys
from html import escape, unescape
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import game_page_paths, load_library


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = load_library(ROOT / "game-library.js")
GAMES = {
    game["slug"]: game
    for game in LIBRARY.get("games", [])
    if isinstance(game, dict) and isinstance(game.get("slug"), str)
}

HOME_CONFIG = {
    "title": "DEAD STRIKE",
    "iframe_url": "https://dead-strike.1games.io/",
    "poster_src": "/dead-strike-thumb.webp",
    "heading": "Load DEAD STRIKE when you are ready to fight.",
    "copy": "Keep the homepage lighter while you browse the guides, then launch the live build in place or open the full game in a separate tab.",
}

FEATURED_PAGE_PATHS = [
    Path("games/zombie-games/index.html"),
    Path("games/fps-games/index.html"),
    Path("games/shooter-games/index.html"),
    Path("games/sniper-games/index.html"),
    Path("games/zombie-defense-games/index.html"),
    Path("games/multiplayer-shooter-games/index.html"),
]

PLAYER_SHELL_PATTERN = re.compile(
    r'<div(?=[^>]*\bplayer-shell\b)(?=[^>]*\bid="playerShell")[^>]*>',
    re.I,
)
IFRAME_SRC_PATTERN = re.compile(r'<iframe[^>]+(?:data-iframe-src|src)="([^"]+)"', re.I)
H1_PATTERN = re.compile(r"<h1[^>]*>(.*?)</h1>", re.I | re.S)
TAG_PATTERN = re.compile(r"<[^>]+>")


def render_player_shell(title: str, iframe_url: str, poster_src: str, heading: str, copy: str) -> str:
    safe_title = escape(title)
    safe_iframe_url = escape(iframe_url, quote=True)
    safe_poster_src = escape(poster_src, quote=True)
    safe_heading = escape(heading)
    safe_copy = escape(copy)
    return (
        '<div class="player-shell arcade-player-shell player-shell-deferred" data-player-loaded="false" data-player-shell="" id="playerShell">'
        f'<iframe allow="fullscreen *; gamepad *" class="player-frame arcade-player-frame" data-iframe-src="{safe_iframe_url}" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" src="about:blank" title="{escape(title, quote=True)}"></iframe>'
        '<div class="player-poster" data-player-poster="">'
        '<div class="player-poster-content">'
        '<div class="player-poster-copy-wrap">'
        '<p class="player-poster-kicker">Fast first load</p>'
        f'<h2 class="player-poster-title">{safe_heading}</h2>'
        f'<p class="player-poster-copy">{safe_copy}</p>'
        '<div class="player-poster-actions">'
        '<button class="button button-primary" data-load-player="#playerShell" data-load-player-default="Play in Page" data-load-player-loading="Loading..." type="button">Play in Page</button>'
        f'<a class="button button-ghost" href="{safe_iframe_url}" rel="noreferrer" target="_blank">Open Full Game</a>'
        "</div>"
        "</div>"
        '<div class="player-poster-thumb">'
        f'<img alt="{escape(title, quote=True)} preview" class="player-poster-media" decoding="async" loading="eager" src="{safe_poster_src}"/>'
        "</div>"
        "</div>"
        "</div>"
        "</div>"
    )


def replace_player_shell(html: str, replacement: str) -> str:
    match = PLAYER_SHELL_PATTERN.search(html)
    if not match:
        return html

    cursor = match.end()
    depth = 1

    while depth > 0:
        next_open = html.find("<div", cursor)
        next_close = html.find("</div>", cursor)
        if next_close == -1:
            raise ValueError("Could not find closing </div> for playerShell")

        if next_open != -1 and next_open < next_close:
            depth += 1
            cursor = next_open + 4
            continue

        depth -= 1
        cursor = next_close + len("</div>")

    return html[: match.start()] + replacement + html[cursor:]


def defer_player(path: Path, *, title: str, iframe_url: str, poster_src: str, heading: str, copy: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = replace_player_shell(
        text,
        render_player_shell(
            title=title,
            iframe_url=iframe_url,
            poster_src=poster_src,
            heading=heading,
            copy=copy,
        ),
    )
    path.write_text(updated, encoding="utf-8")


def extract_iframe_url(text: str) -> str:
    match = IFRAME_SRC_PATTERN.search(text)
    if not match:
        raise ValueError("Could not find iframe src for featured page")
    return unescape(match.group(1))


def extract_h1_text(text: str) -> str:
    match = H1_PATTERN.search(text)
    if not match:
        return "featured game"
    return unescape(TAG_PATTERN.sub("", match.group(1))).strip() or "featured game"


def game_for_iframe(iframe_url: str) -> dict | None:
    for game in GAMES.values():
        if game.get("iframeUrl") == iframe_url:
            return game
    return None


def update_home_copy(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = {
        "Fast-paced zombie FPS with weapon unlocks, wave survival, and instant browser play.": "Fast-paced zombie FPS with weapon unlocks, wave survival, and click-to-load browser play.",
        "The current Dead Strike build is a heavy Unity FPS. It runs in the homepage iframe, but phones usually get a smaller play area and slower first load, so opening the full game tab is the safer mobile path.": "The current Dead Strike build is a heavy Unity FPS. The homepage now keeps the iframe unloaded until you choose to play, which trims first-load cost while preserving an in-page launch option. Phones still get a smaller play area, so opening the full game tab remains the safer mobile path.",
        "Dead Strike drops you into compact combat spaces where zombies keep pushing forward until you break the wave. The homepage is not just a trailer or a landing screen: it is the live play surface, so players can load the game instantly, test the pacing, and decide whether they want to stay in the embedded frame or jump into fullscreen.": "Dead Strike drops you into compact combat spaces where zombies keep pushing forward until you break the wave. The homepage is still a playable launch surface, but it now waits for your click before loading the live build, giving the page a faster first view while keeping in-page play available.",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    path.write_text(text, encoding="utf-8")


def update_home() -> None:
    path = ROOT / "index.html"
    defer_player(path, **HOME_CONFIG)
    update_home_copy(path)


def update_detail_pages() -> None:
    for path in game_page_paths(ROOT, LIBRARY, live_only=True, include_home=False):
        slug = path.parent.name
        game = GAMES.get(slug)
        if not game:
            continue

        defer_player(
            path,
            title=game["title"],
            iframe_url=game["iframeUrl"],
            poster_src=game["thumb"],
            heading=f"Load {game['title']} when you are ready to play.",
            copy="Keep the page lighter while you scan the guide, then launch the live build in place or open the full game in a separate tab.",
        )


def update_featured_hubs() -> None:
    for relative_path in FEATURED_PAGE_PATHS:
        path = ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        try:
            iframe_url = extract_iframe_url(text)
        except ValueError:
            continue
        heading_label = extract_h1_text(text)
        game = game_for_iframe(iframe_url)
        title = game["title"] if game else heading_label
        poster_src = game["thumb"] if game else "/dead-strike-thumb.webp"
        defer_player(
            path,
            title=title,
            iframe_url=iframe_url,
            poster_src=poster_src,
            heading=f"Load the featured {heading_label} pick when you are ready to play.",
            copy="Keep the hub lighter while you browse the catalog, then launch the featured game in place or open the full game in a separate tab.",
        )


def main() -> int:
    update_home()
    update_detail_pages()
    update_featured_hubs()
    print("DEFERRED_PLAYERS_BACKFILLED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
