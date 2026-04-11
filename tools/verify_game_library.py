#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import href_to_file_path, load_library


REQUIRED_FIELDS = [
    "slug",
    "title",
    "href",
    "iframeUrl",
    "thumb",
    "categories",
    "isLive",
    "releaseGroup",
    "related",
]

REQUIRED_STRING_FIELDS = ["slug", "title", "href", "iframeUrl", "thumb", "releaseGroup"]

POOL_MINIMUMS = {
    "playerStrip": 12,
    "popular": 8,
    "fresh": 6,
}

FALLBACK_MINIMUMS = {
    "fps": 12,
    "liveLibrary": 12,
    "zombie": 12,
    "sniper": 6,
    "shooter": 12,
}

ROUND_TWO_RELEASE_GROUP = "expansion-2026-04"
ROUND_TWO_EXPECTED = 22

REPRESENTATIVE_PAGE_SLUGS = [
    "dead-strike",
    "sniper-master",
    "wacky-strike",
    "pubg-hack",
    "noob-vs-zombie",
]

HOMEPAGE_POOL_SAMPLES = ["playerStrip", "popular", "fresh"]

EXPECTED_CATEGORY_PAGES = {
    "zombie-games": "/games/zombie-games/",
    "fps-games": "/games/fps-games/",
    "shooter-games": "/games/shooter-games/",
}

REQUIRED_EXISTING_SLUGS = [
    "dead-strike",
    "fps-shooting-survival-sim",
    "zombie-survival-last-stand",
    "wacky-strike",
    "survival-wave-zombie-multiplayer",
    "super-cat-free-fire",
    "space-adventure-noobiks-battle-vs-zombies",
    "sniper-master",
    "rpg-soldier-shooter",
    "pubg-hack",
    "noob-vs-zombie-2",
    "noob-vs-zombie",
    "multigun-arena-zombie-survival",
    "minecraft-noob-vs-zombies-3",
    "guns-vs-magic",
    "edge-of-survival",
    "dusk-warz",
    "challenge-the-zombies",
    "blocky-combat-swat-original-2026",
    "battledudes-io",
    "modern-fps-strike-zombie-gun-war-ops",
]

REQUIRED_NEW_SLUGS = [
    "call-of-ops-3-zombies",
    "zombie-reform",
    "zombie-incursion-world",
    "pixel-zombie-survival",
    "zombie-last-guard",
    "biozombie-outbreak",
    "super-sergeant-zombies",
    "minewar-soldiers-vs-zombies",
    "counter-craft-sniper",
    "urban-sniper-multiplayer-2",
    "sniper-clash-3d",
    "zombie-clash-3d",
    "subway-clash-3d",
    "rocket-clash-3d",
    "fort-clash-survival",
    "lone-wolf-strike",
]


def validate_game(game: dict, slug_set: set[str], errors: list[str]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in game:
            errors.append(f"Game '{game.get('slug', '<missing-slug>')}' missing field '{field}'")

    for field in REQUIRED_STRING_FIELDS:
        value = game.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"Game '{game.get('slug', '<missing-slug>')}' field '{field}' must be a non-empty string"
            )

    slug = game.get("slug")
    if not isinstance(slug, str) or not slug:
        errors.append("Every game must have a non-empty string slug")
    elif slug in slug_set:
        errors.append(f"Duplicate slug: {slug}")
    else:
        slug_set.add(slug)

    if isinstance(game.get("href"), str) and not game["href"].startswith("/"):
        errors.append(f"Game '{slug}' href must start with '/'")

    if isinstance(game.get("categories"), list):
        if not game["categories"]:
            errors.append(f"Game '{slug}' must have at least one category")
    else:
        errors.append(f"Game '{slug}' categories must be a list")

    if not isinstance(game.get("isLive"), bool):
        errors.append(f"Game '{slug}' isLive must be a boolean")

    if isinstance(game.get("related"), list):
        if slug in game["related"]:
            errors.append(f"Game '{slug}' cannot relate to itself")
    else:
        errors.append(f"Game '{slug}' related must be a list")

    if game.get("releaseGroup") == "legacy-alias":
        canonical_slug = game.get("canonicalSlug")
        if not isinstance(canonical_slug, str) or not canonical_slug or canonical_slug == slug:
            errors.append(f"Legacy alias game '{slug}' must set canonicalSlug to a different live slug")


def validate_live_files(root: Path, games: list[dict], errors: list[str]) -> None:
    for game in games:
        if not game.get("isLive"):
            continue

        href = game.get("href")
        slug = game.get("slug")
        if not isinstance(href, str) or not href:
            continue

        expected_path = href_to_file_path(root, href)
        if not expected_path.exists():
            errors.append(f"Live game '{slug}' points to missing file '{expected_path}'")


def validate_live_pool_coverage(library: dict, games: list[dict], errors: list[str]) -> None:
    pools = library.get("pools")
    render_rules = get_render_rules(library)
    if not isinstance(pools, dict):
        return

    game_lookup = {game["slug"]: game for game in games if isinstance(game, dict) and isinstance(game.get("slug"), str)}

    for pool_name, minimum in POOL_MINIMUMS.items():
        combined = list(get_pool(pool_name, pools))
        for fallback_pool in pool_fill_order(pool_name, render_rules):
            combined.extend(get_pool(fallback_pool, pools))

        effective_games = dedupe_live_games(combined, game_lookup, set(), minimum)
        if len(effective_games) < minimum:
            errors.append(f"Pool '{pool_name}' must yield at least {minimum} usable live games after filtering, found {len(effective_games)}")

    fallbacks = pools.get("fallbacks")
    if not isinstance(fallbacks, dict):
        return

    for pool_name, minimum in FALLBACK_MINIMUMS.items():
        values = get_pool(f"fallbacks.{pool_name}", pools)
        effective_games = dedupe_live_games(values, game_lookup, set(), minimum)
        if len(effective_games) < minimum:
            errors.append(
                f"Fallback pool '{pool_name}' must yield at least {minimum} usable live games after filtering, found {len(effective_games)}"
            )


def validate_slug_pool(name: str, values: list[str], known_slugs: set[str], minimum: int, errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f"Pool '{name}' must be a list")
        return

    if len(values) < minimum:
        errors.append(f"Pool '{name}' must contain at least {minimum} slugs, found {len(values)}")

    seen: set[str] = set()
    for slug in values:
        if slug not in known_slugs:
            errors.append(f"Pool '{name}' references unknown slug '{slug}'")
        if slug in seen:
            errors.append(f"Pool '{name}' contains duplicate slug '{slug}'")
        seen.add(slug)


def validate_category_pages(category_pages: dict, known_slugs: set[str], errors: list[str]) -> None:
    if not isinstance(category_pages, dict):
        errors.append("categoryPages must be an object")
        return

    for key, href in EXPECTED_CATEGORY_PAGES.items():
        page = category_pages.get(key)
        if not isinstance(page, dict):
            errors.append(f"Missing categoryPages entry '{key}'")
            continue

        if page.get("href") != href:
            errors.append(f"categoryPages['{key}'].href must equal '{href}'")

        placeholder = page.get("placeholder")
        if not isinstance(placeholder, str) or not placeholder.startswith("data-"):
            errors.append(f"categoryPages['{key}'] needs a data-* placeholder string")

        slugs = page.get("slugs")
        if not isinstance(slugs, list) or len(slugs) < 6:
            errors.append(f"categoryPages['{key}'].slugs must contain at least 6 entries")
            continue

        for slug in slugs:
            if slug not in known_slugs:
                errors.append(f"categoryPages['{key}'] references unknown slug '{slug}'")


def canonical_slug_of(game: dict) -> str:
    canonical_slug = game.get("canonicalSlug")
    if isinstance(canonical_slug, str) and canonical_slug:
        return canonical_slug
    return game["slug"]


def get_render_rules(library: dict) -> dict:
    render_rules = library.get("renderRules")
    return render_rules if isinstance(render_rules, dict) else {}


def validate_render_rules(library: dict, errors: list[str]) -> None:
    render_rules = get_render_rules(library)
    responsive_counts = render_rules.get("responsiveCounts")
    if not isinstance(responsive_counts, dict):
        errors.append("renderRules.responsiveCounts must be an object")
    else:
        for key, expected_minimum in (("desktop", 12), ("tablet", 8), ("mobile", 6)):
            value = responsive_counts.get(key)
            if not isinstance(value, int) or value < expected_minimum:
                errors.append(f"renderRules.responsiveCounts.{key} must be an integer >= {expected_minimum}")

    category_rules = render_rules.get("categoryFallbackPriority")
    if not isinstance(category_rules, list) or not category_rules:
        errors.append("renderRules.categoryFallbackPriority must be a non-empty list")
    else:
        for index, rule in enumerate(category_rules):
            if not isinstance(rule, dict):
                errors.append(f"renderRules.categoryFallbackPriority[{index}] must be an object")
                continue
            if not isinstance(rule.get("category"), str) or not rule["category"]:
                errors.append(f"renderRules.categoryFallbackPriority[{index}].category must be a non-empty string")
            if not isinstance(rule.get("pool"), str) or not rule["pool"]:
                errors.append(f"renderRules.categoryFallbackPriority[{index}].pool must be a non-empty string")

    terminal_pools = render_rules.get("terminalFallbackPools")
    if not isinstance(terminal_pools, list) or not terminal_pools:
        errors.append("renderRules.terminalFallbackPools must be a non-empty list")

    home_fill = render_rules.get("homePoolFillOrder")
    if not isinstance(home_fill, dict):
        errors.append("renderRules.homePoolFillOrder must be an object")
    else:
        for pool_name in HOMEPAGE_POOL_SAMPLES:
            if not isinstance(home_fill.get(pool_name), list) or not home_fill.get(pool_name):
                errors.append(f"renderRules.homePoolFillOrder['{pool_name}'] must be a non-empty list")


def validate_canonical_targets(games: list[dict], errors: list[str]) -> None:
    games_by_slug = {game["slug"]: game for game in games if isinstance(game, dict) and isinstance(game.get("slug"), str)}

    for game in games:
        canonical_slug = game.get("canonicalSlug")
        if not canonical_slug:
            continue

        target_game = games_by_slug.get(canonical_slug)
        if not target_game or not target_game.get("isLive"):
            errors.append(
                f"Game '{game.get('slug')}' canonicalSlug must point to an existing live game, found '{canonical_slug}'"
            )


def validate_category_page_live_targets(category_pages: dict, games: list[dict], errors: list[str]) -> None:
    if not isinstance(category_pages, dict):
        return

    games_by_slug = {game["slug"]: game for game in games if isinstance(game, dict) and isinstance(game.get("slug"), str)}

    for page_name, page in category_pages.items():
        if not isinstance(page, dict):
            continue

        slugs = page.get("slugs")
        if not isinstance(slugs, list):
            continue

        for slug in slugs:
            game = games_by_slug.get(slug)
            if not game:
                continue
            if game.get("isLive"):
                continue
            if game.get("releaseGroup") == ROUND_TWO_RELEASE_GROUP:
                continue
            if not game.get("isLive"):
                errors.append(f"categoryPages['{page_name}'] slug '{slug}' must point to a live game")


def validate_round_two_inventory(games: list[dict], errors: list[str]) -> None:
    round_two_games = [
        game
        for game in games
        if isinstance(game, dict) and game.get("releaseGroup") == ROUND_TWO_RELEASE_GROUP
    ]

    if len(round_two_games) != ROUND_TWO_EXPECTED:
        errors.append(
            f"Expected {ROUND_TWO_EXPECTED} round-two games in releaseGroup '{ROUND_TWO_RELEASE_GROUP}', found {len(round_two_games)}"
        )

    live_round_two = [game.get("slug") for game in round_two_games if game.get("isLive")]
    if live_round_two:
        errors.append(
            f"Round-two games must stay staged with isLive=false, found live slugs: {', '.join(sorted(live_round_two))}"
        )


def dedupe_live_games(slugs: list[str], games_by_slug: dict[str, dict], exclude_canonical_slugs: set[str], limit: int) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []

    for slug in slugs:
        game = games_by_slug.get(slug)
        if not game or not game.get("isLive"):
            continue

        canonical_slug = canonical_slug_of(game)
        canonical_game = games_by_slug.get(canonical_slug, game)
        if not canonical_game.get("isLive"):
            continue

        if canonical_slug in exclude_canonical_slugs or canonical_slug in seen:
            continue

        seen.add(canonical_slug)
        results.append(canonical_game)
        if len(results) >= limit:
            break

    return results


def fallback_order_for(game: dict, render_rules: dict) -> list[str]:
    categories = set(game.get("categories", []))
    order: list[str] = []
    category_rules = render_rules.get("categoryFallbackPriority")
    terminal_pools = render_rules.get("terminalFallbackPools")

    if isinstance(category_rules, list):
        for rule in category_rules:
            if isinstance(rule, dict) and rule.get("category") in categories and isinstance(rule.get("pool"), str):
                order.append(rule["pool"])

    if isinstance(terminal_pools, list):
        for pool_name in terminal_pools:
            if isinstance(pool_name, str):
                order.append(pool_name)

    return order


def pool_fill_order(pool_name: str, render_rules: dict) -> list[str]:
    home_fill = render_rules.get("homePoolFillOrder")
    if not isinstance(home_fill, dict):
        return []

    value = home_fill.get(pool_name)
    return value if isinstance(value, list) else []


def get_pool(pool_name: str, pools: dict) -> list[str]:
    value = pools
    for part in pool_name.split("."):
        if not isinstance(value, dict):
            return []
        value = value.get(part)
    return value if isinstance(value, list) else []


def validate_derived_recommendations(library: dict, games: list[dict], errors: list[str]) -> None:
    pools = library.get("pools")
    if not isinstance(pools, dict):
        return

    render_rules = get_render_rules(library)
    games_by_slug = {game["slug"]: game for game in games}

    for pool_name in HOMEPAGE_POOL_SAMPLES:
        combined = list(get_pool(pool_name, pools))
        for fallback_pool in pool_fill_order(pool_name, render_rules):
            combined.extend(get_pool(fallback_pool, pools))

        derived = dedupe_live_games(combined, games_by_slug, set(), 12)
        if len(derived) < 12:
            errors.append(f"Derived homepage pool '{pool_name}' must yield 12 live recommendations, found {len(derived)}")

        canonical_slugs = [canonical_slug_of(game) for game in derived]
        if len(canonical_slugs) != len(set(canonical_slugs)):
            errors.append(f"Derived homepage pool '{pool_name}' contains canonical duplicates")

    for slug in REPRESENTATIVE_PAGE_SLUGS:
        game = games_by_slug.get(slug)
        if not game or not game.get("isLive"):
            continue

        combined = list(game.get("related", []))
        for fallback_pool in fallback_order_for(game, render_rules):
            combined.extend(get_pool(fallback_pool, pools))

        derived = dedupe_live_games(combined, games_by_slug, {canonical_slug_of(game)}, 12)
        if len(derived) < 12:
            errors.append(f"Derived related recommendations for '{slug}' must yield 12 live games, found {len(derived)}")

        canonical_slugs = [canonical_slug_of(result) for result in derived]
        if len(canonical_slugs) != len(set(canonical_slugs)):
            errors.append(f"Derived related recommendations for '{slug}' contain canonical duplicates")


def validate_required_inventory(known_slugs: set[str], errors: list[str]) -> None:
    for slug in REQUIRED_EXISTING_SLUGS:
        if slug not in known_slugs:
            errors.append(f"Missing required existing slug '{slug}'")

    for slug in REQUIRED_NEW_SLUGS:
        if slug not in known_slugs:
            errors.append(f"Missing required new slug '{slug}'")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--library",
        default=str(Path(__file__).resolve().parents[1] / "game-library.js"),
        help="Path to game-library.js",
    )
    args = parser.parse_args()

    errors: list[str] = []
    try:
        library = load_library(Path(args.library))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    games = library.get("games")
    if not isinstance(games, list):
        print("ERROR: 'games' must be a list")
        return 1

    slug_set: set[str] = set()
    for game in games:
        if not isinstance(game, dict):
            errors.append("Each game entry must be an object")
            continue
        validate_game(game, slug_set, errors)

    pools = library.get("pools")
    if not isinstance(pools, dict):
        errors.append("pools must be an object")
    else:
        validate_live_pool_coverage(library, games, errors)
        for pool_name, minimum in POOL_MINIMUMS.items():
            validate_slug_pool(pool_name, pools.get(pool_name), slug_set, minimum, errors)

        fallbacks = pools.get("fallbacks")
        if not isinstance(fallbacks, dict):
            errors.append("pools.fallbacks must be an object")
        else:
            for pool_name, minimum in FALLBACK_MINIMUMS.items():
                validate_slug_pool(
                    f"fallbacks.{pool_name}",
                    fallbacks.get(pool_name),
                    slug_set,
                    minimum,
                    errors,
                )

    for game in games:
        slug = game.get("slug")
        for related_slug in game.get("related", []):
            if related_slug not in slug_set:
                errors.append(f"Game '{slug}' has unknown related slug '{related_slug}'")

    validate_render_rules(library, errors)
    validate_canonical_targets(games, errors)
    validate_required_inventory(slug_set, errors)
    validate_round_two_inventory(games, errors)
    validate_category_pages(library.get("categoryPages"), slug_set, errors)
    validate_category_page_live_targets(library.get("categoryPages"), games, errors)
    validate_live_files(Path(args.library).resolve().parent, games, errors)
    validate_derived_recommendations(library, games, errors)

    if errors:
        print("GAME_LIBRARY_VERIFICATION_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"GAME_LIBRARY_VERIFIED: {len(games)} games, {len(slug_set)} unique slugs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
