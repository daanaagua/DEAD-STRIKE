#!/usr/bin/env python3
import json
import re
from pathlib import Path


def load_library(library_path: Path) -> dict:
    if not library_path.exists():
        raise FileNotFoundError(f"Missing library file: {library_path}")

    raw = library_path.read_text(encoding="utf-8")
    match = re.search(
        r"window\.DEAD_STRIKE_LIBRARY\s*=\s*(\{.*\})\s*;?\s*$",
        raw,
        re.S,
    )
    if not match:
        raise ValueError("game-library.js must assign strict JSON to window.DEAD_STRIKE_LIBRARY")

    return json.loads(match.group(1))


def href_to_file_path(root: Path, href: str) -> Path:
    if href == "/":
        return root / "index.html"

    relative = href.strip("/")
    return root / relative / "index.html"


def game_page_paths(root: Path, library: dict, *, live_only: bool | None = None, include_home: bool = False) -> list[Path]:
    games = library.get("games")
    if not isinstance(games, list):
        return []

    paths: list[Path] = []
    for game in games:
        if not isinstance(game, dict):
            continue

        href = game.get("href")
        if not isinstance(href, str) or not href:
            continue

        if href == "/" and not include_home:
            continue

        if live_only is not None and game.get("isLive") is not live_only:
            continue

        paths.append(href_to_file_path(root, href))

    return list(dict.fromkeys(paths))
