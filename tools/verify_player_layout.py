#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import game_page_paths, load_library

# Infrastructure-only phase rule:
# - Existing-page validation may run now.
# - Future new detail pages stay opt-in and are only checked when
#   --new-detail-pages is explicitly requested in a later task.

SITE_JS_NEEDS = [
    "data-player-strip",
    "data-home-popular",
    "data-home-fresh",
    "DEAD_STRIKE_PAGE",
    "renderStrip",
    "renderIconWall",
    "getPoolGames",
    "getRelatedGames",
]

SITE_CSS_NEEDS = [
    ".player-strip",
    ".player-strip-grid",
    ".player-strip-card",
    ".sidebar-icon-grid",
    "repeat(6, minmax(0, 1fr))",
    "repeat(4, minmax(0, 1fr))",
    "repeat(3, minmax(0, 1fr))",
]


DEFAULT_PAGES = ["index.html"]


def load_page_sets(root: Path) -> tuple[list[Path], list[Path]]:
    library = load_library(root / "game-library.js")
    existing_pages = game_page_paths(root, library, live_only=True, include_home=False)
    future_pages = game_page_paths(root, library, live_only=False, include_home=False)
    return existing_pages, future_pages


def page_paths(root: Path, args: argparse.Namespace) -> list[Path]:
    existing_pages, future_pages = load_page_sets(root)
    paths = [root / page for page in args.page]
    if not args.page and not args.existing_detail_pages and not args.new_detail_pages:
        paths.extend(root / page for page in DEFAULT_PAGES)
        paths.extend(existing_pages)
        return list(dict.fromkeys(paths))

    if args.existing_detail_pages:
        paths.extend(root / page for page in DEFAULT_PAGES)
        paths.extend(existing_pages)
    if args.new_detail_pages:
        paths.extend(future_pages)
    return list(dict.fromkeys(paths))


def is_support_readiness_mode(args: argparse.Namespace) -> bool:
    return not args.page and not args.existing_detail_pages and not args.new_detail_pages


def is_default_existing_scan(args: argparse.Namespace) -> bool:
    return is_support_readiness_mode(args)


def require_support_contract(root: Path, errors: list[str]) -> None:
    site_js = (root / "site.js").read_text(encoding="utf-8")
    site_css = (root / "site.css").read_text(encoding="utf-8")

    for token in SITE_JS_NEEDS:
        if token not in site_js:
            errors.append(f"site.js missing required token '{token}'")

    for token in SITE_CSS_NEEDS:
        if token not in site_css:
            errors.append(f"site.css missing required token '{token}'")


def validate_page(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing page: {path}")
        return

    html = path.read_text(encoding="utf-8")
    has_library_hook = any(
        token in html
        for token in [
            "data-player-strip",
            "data-home-popular",
            "data-home-fresh",
            "DEAD_STRIKE_PAGE",
        ]
    )

    if has_library_hook:
        library_pos = html.find("/game-library.js")
        site_pos = html.find("/site.js")
        if library_pos == -1:
            errors.append(f"{path}: missing /game-library.js before /site.js")
        elif site_pos == -1:
            errors.append(f"{path}: missing /site.js")
        elif library_pos > site_pos:
            errors.append(f"{path}: /game-library.js must load before /site.js")

    strip_pos = html.find("data-player-strip")
    if strip_pos != -1:
        title_pos = html.find("<h1")
        if title_pos == -1:
            errors.append(f"{path}: missing <h1> for strip ordering check")
        elif strip_pos > title_pos:
            errors.append(f"{path}: player strip must appear before the title block")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", action="append", default=[], help="Page path relative to repo root")
    parser.add_argument("--existing-detail-pages", action="store_true", help="Validate the current required existing detail-page set")
    parser.add_argument("--new-detail-pages", action="store_true", help="Opt-in check for future new detail pages once those files exist")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    require_support_contract(root, errors)
    for path in page_paths(root, args):
        validate_page(path, errors)

    if errors:
        print("PLAYER_LAYOUT_VERIFICATION_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    if is_default_existing_scan(args):
        print("PLAYER_LAYOUT_SUPPORT_AND_EXISTING_PAGES_VERIFIED")
    else:
        print("PLAYER_LAYOUT_PAGE_CHECKS_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
