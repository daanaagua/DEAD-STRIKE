#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from tools.build_round_two_manifest import extract_embed_fields, fetch_html
except ModuleNotFoundError:
    from build_round_two_manifest import extract_embed_fields, fetch_html


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_FILE = ROOT / "tools" / "round_two_sources.json"
EXPECTED_RELEASE_GROUP = "expansion-2026-04"
EXPECTED_IFRAME_PREFIX = "https://html5.gamemonetize."
EXPECTED_THUMB_PREFIX = "https://img.gamemonetize.com/"

REQUIRED_ITEM_FIELDS = [
    "title",
    "slug",
    "group",
    "sourcePage",
    "categories",
    "copySeed",
]

REQUIRED_COPY_SEED_FIELDS = ["tempo", "scene", "intent"]

EXPECTED_SOURCE_BINDINGS = {
    "primary": {
        "fps-shooting-game-3d-gun-game": {
            "title": "FPS Shooting Game: 3D Gun Game",
            "slug": "fps-shooting-game-3d-gun-game",
            "group": "tactical-fps",
            "sourcePage": "https://gamemonetize.com/fps-shooting-game-3d-gun-game-game",
            "categories": ["fps", "shooter", "military", "tactical"],
            "copySeed": {
                "tempo": "fast-rush",
                "scene": "urban-warzone",
                "intent": "modern-commando",
            },
        },
        "infantry-attack-battle-3d-fps": {
            "title": "Infantry Attack:Battle 3D FPS",
            "slug": "infantry-attack-battle-3d-fps",
            "group": "tactical-fps",
            "sourcePage": "https://gamemonetize.com/infantry-attack-battle-3d-fps-game",
            "categories": ["fps", "battle", "assault", "squad"],
            "copySeed": {
                "tempo": "frontline-push",
                "scene": "fortified-checkpoint",
                "intent": "infantry-breakthrough",
            },
        },
        "duty-call-modern-warfate-2": {
            "title": "Duty Call Modern Warfate 2",
            "slug": "duty-call-modern-warfate-2",
            "group": "tactical-fps",
            "sourcePage": "https://gamemonetize.com/duty-call-modern-warfate-2-game",
            "categories": ["fps", "military", "campaign", "modern-war"],
            "copySeed": {
                "tempo": "mission-surge",
                "scene": "modern-battlefield",
                "intent": "special-ops-patrol",
            },
        },
        "command-strike-fps-2": {
            "title": "Command Strike FPS 2",
            "slug": "command-strike-fps-2",
            "group": "tactical-fps",
            "sourcePage": "https://gamemonetize.com/command-strike-fps-2-game",
            "categories": ["fps", "command", "strike", "counterforce"],
            "copySeed": {
                "tempo": "breach-and-clear",
                "scene": "industrial-complex",
                "intent": "command-unit-raider",
            },
        },
        "cod-duty-call-fps": {
            "title": "COD Duty Call FPS",
            "slug": "cod-duty-call-fps",
            "group": "tactical-fps",
            "sourcePage": "https://gamemonetize.com/cod-duty-call-fps-game",
            "categories": ["fps", "combat", "guns", "mission"],
            "copySeed": {
                "tempo": "combat-sprint",
                "scene": "enemy-stronghold",
                "intent": "loadout-driven-shooter",
            },
        },
        "special-forces-war-zombie-attack": {
            "title": "Special Forces War Zombie Attack",
            "slug": "special-forces-war-zombie-attack",
            "group": "tactical-fps",
            "sourcePage": "https://gamemonetize.com/special-forces-war-zombie-attack-game",
            "categories": ["fps", "special-forces", "zombie", "survival"],
            "copySeed": {
                "tempo": "panic-firefight",
                "scene": "infected-warzone",
                "intent": "elite-zombie-suppression",
            },
        },
        "shooterz-io": {
            "title": "ShooterZ.io",
            "slug": "shooterz-io",
            "group": "multiplayer-arena",
            "sourcePage": "https://gamemonetize.com/shooterz-io-game",
            "categories": ["multiplayer", "arena", "io", "shooter"],
            "copySeed": {
                "tempo": "live-match-loop",
                "scene": "open-killbox",
                "intent": "drop-in-arena-duel",
            },
        },
        "blocky-siege": {
            "title": "Blocky Siege",
            "slug": "blocky-siege",
            "group": "multiplayer-arena",
            "sourcePage": "https://gamemonetize.com/blocky-siege-game",
            "categories": ["multiplayer", "blocky", "arena", "pvp"],
            "copySeed": {
                "tempo": "flank-and-peek",
                "scene": "voxel-battle-lanes",
                "intent": "block-style-teamfight",
            },
        },
        "moon-clash-heroes": {
            "title": "Moon Clash Heroes",
            "slug": "moon-clash-heroes",
            "group": "multiplayer-arena",
            "sourcePage": "https://gamemonetize.com/moon-clash-heroes-game",
            "categories": ["multiplayer", "heroes", "arena", "sci-fi"],
            "copySeed": {
                "tempo": "jetpack-skirmish",
                "scene": "lunar-outpost",
                "intent": "hero-shooter-showdown",
            },
        },
        "nightwalkers-io": {
            "title": "Nightwalkers.io",
            "slug": "nightwalkers-io",
            "group": "multiplayer-arena",
            "sourcePage": "https://gamemonetize.com/nightwalkers-io-game",
            "categories": ["multiplayer", "io", "survival", "night-battle"],
            "copySeed": {
                "tempo": "after-dark-scramble",
                "scene": "haunted-streets",
                "intent": "survive-online-chaos",
            },
        },
        "combat-zombie-warfare": {
            "title": "Combat Zombie Warfare",
            "slug": "combat-zombie-warfare",
            "group": "multiplayer-arena",
            "sourcePage": "https://gamemonetize.com/combat-zombie-warfare-game",
            "categories": ["multiplayer", "zombie", "arena", "co-op"],
            "copySeed": {
                "tempo": "horde-crossfire",
                "scene": "ruined-combat-zone",
                "intent": "squad-vs-undead-match",
            },
        },
        "sniper-mission-war": {
            "title": "Sniper Mission War",
            "slug": "sniper-mission-war",
            "group": "sniper",
            "sourcePage": "https://gamemonetize.com/sniper-mission-war-game",
            "categories": ["sniper", "precision", "warfare", "mission"],
            "copySeed": {
                "tempo": "patient-trigger",
                "scene": "battlefield-overwatch",
                "intent": "mission-based-marksmanship",
            },
        },
        "sniper-ghost-shooter": {
            "title": "Sniper Ghost Shooter",
            "slug": "sniper-ghost-shooter",
            "group": "sniper",
            "sourcePage": "https://gamemonetize.com/sniper-ghost-shooter-game",
            "categories": ["sniper", "stealth", "ghost", "elimination"],
            "copySeed": {
                "tempo": "silent-takedown",
                "scene": "shadowy-ruins",
                "intent": "stealth-assassin-vantage",
            },
        },
        "sniper-shot-3d": {
            "title": "Sniper Shot 3D",
            "slug": "sniper-shot-3d",
            "group": "sniper",
            "sourcePage": "https://gamemonetize.com/sniper-shot-3d-game",
            "categories": ["sniper", "3d", "aim", "precision"],
            "copySeed": {
                "tempo": "steady-breath",
                "scene": "rooftop-range",
                "intent": "clean-one-shot-focus",
            },
        },
        "urban-sniper-multiplayer": {
            "title": "Urban Sniper Multiplayer",
            "slug": "urban-sniper-multiplayer",
            "group": "sniper",
            "sourcePage": "https://gamemonetize.com/urban-sniper-multiplayer-game",
            "categories": ["sniper", "multiplayer", "urban", "pvp"],
            "copySeed": {
                "tempo": "lane-lock-duel",
                "scene": "city-skyline",
                "intent": "urban-overwatch-pvp",
            },
        },
        "zombie-defense-war-z-survival": {
            "title": "Zombie defense: War Z Survival",
            "slug": "zombie-defense-war-z-survival",
            "group": "zombie-defense",
            "sourcePage": "https://gamemonetize.com/zombie-defense-war-z-survival-game",
            "categories": ["zombie", "defense", "survival", "base-defense"],
            "copySeed": {
                "tempo": "wave-holdout",
                "scene": "barricaded-base",
                "intent": "last-line-defense",
            },
        },
        "zombie-defense-last-stand": {
            "title": "Zombie Defense: Last Stand",
            "slug": "zombie-defense-last-stand",
            "group": "zombie-defense",
            "sourcePage": "https://gamemonetize.com/zombie-defense-last-stand-game",
            "categories": ["zombie", "defense", "last-stand", "apocalypse"],
            "copySeed": {
                "tempo": "pressure-escalation",
                "scene": "collapsed-outpost",
                "intent": "fortify-until-dawn",
            },
        },
        "grand-zombie-swarm": {
            "title": "Grand Zombie Swarm",
            "slug": "grand-zombie-swarm",
            "group": "zombie-defense",
            "sourcePage": "https://gamemonetize.com/grand-zombie-swarm-game",
            "categories": ["zombie", "swarm", "defense", "horde"],
            "copySeed": {
                "tempo": "mass-horde-crush",
                "scene": "city-perimeter",
                "intent": "crowd-control-survivor",
            },
        },
        "zombie-vacation-2": {
            "title": "Zombie Vacation 2",
            "slug": "zombie-vacation-2",
            "group": "zombie-defense",
            "sourcePage": "https://gamemonetize.com/zombie-vacation-2-game",
            "categories": ["zombie", "survival", "vacation", "defense"],
            "copySeed": {
                "tempo": "resort-siege",
                "scene": "abandoned-holiday-zone",
                "intent": "vacation-nightmare-defense",
            },
        },
        "zombie-shooter-3d": {
            "title": "Zombie Shooter 3D",
            "slug": "zombie-shooter-3d",
            "group": "adjacent-long-tail",
            "sourcePage": "https://gamemonetize.com/zombie-shooter-3d-game",
            "categories": ["zombie", "shooter", "3d", "action"],
            "copySeed": {
                "tempo": "run-and-gun",
                "scene": "infected-corridor",
                "intent": "straight-ahead-zombie-blast",
            },
        },
        "zombie-survival-pixel-apocalypse": {
            "title": "Zombie Survival Pixel Apocalypse",
            "slug": "zombie-survival-pixel-apocalypse",
            "group": "adjacent-long-tail",
            "sourcePage": "https://gamemonetize.com/zombie-survival-pixel-apocalypse-game",
            "categories": ["zombie", "pixel", "survival", "apocalypse"],
            "copySeed": {
                "tempo": "scrappy-survival",
                "scene": "pixel-doomsday-town",
                "intent": "retro-undead-endurance",
            },
        },
        "pixel-multiplayer-survival-zombie": {
            "title": "Pixel multiplayer survival zombie",
            "slug": "pixel-multiplayer-survival-zombie",
            "group": "adjacent-long-tail",
            "sourcePage": "https://gamemonetize.com/pixel-multiplayer-survival-zombie-game",
            "categories": ["pixel", "multiplayer", "zombie", "survival"],
            "copySeed": {
                "tempo": "online-scavenge",
                "scene": "blocky-wasteland",
                "intent": "pixel-coop-undead-survival",
            },
        },
    },
    "backup": {
        "counter-strike-survival": {
            "title": "Counter Strike : Survival",
            "slug": "counter-strike-survival",
            "group": "reserve",
            "sourcePage": "https://gamemonetize.com/counter-strike-survival-game",
            "categories": ["fps", "survival", "reserve", "military"],
            "copySeed": {
                "tempo": "team-firefight",
                "scene": "classic-war-map",
                "intent": "fallback-counterstrike-clone",
            },
        },
        "3d-sniper-shooting-game": {
            "title": "3D Sniper Shooting Game",
            "slug": "3d-sniper-shooting-game",
            "group": "reserve",
            "sourcePage": "https://gamemonetize.com/3d-sniper-shooting-game-game",
            "categories": ["sniper", "3d", "reserve", "precision"],
            "copySeed": {
                "tempo": "measured-shot",
                "scene": "reserve-watchtower",
                "intent": "backup-sniper-angle",
            },
        },
        "tank-war-multiplayer": {
            "title": "Tank War Multiplayer",
            "slug": "tank-war-multiplayer",
            "group": "reserve",
            "sourcePage": "https://gamemonetize.com/tank-war-multiplayer-game",
            "categories": ["tank", "multiplayer", "reserve", "vehicle-combat"],
            "copySeed": {
                "tempo": "armor-clash",
                "scene": "battlefield-open-ground",
                "intent": "backup-heavy-firepower",
            },
        },
        "the-rise-of-zombies": {
            "title": "The Rise Of Zombies",
            "slug": "the-rise-of-zombies",
            "group": "reserve",
            "sourcePage": "https://gamemonetize.com/the-rise-of-zombies-game",
            "categories": ["zombie", "reserve", "survival", "action"],
            "copySeed": {
                "tempo": "outbreak-surge",
                "scene": "fallen-city",
                "intent": "backup-zombie-emergency",
            },
        },
    },
}


def load_source_list(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def format_value(value: Any) -> str:
    return repr(value)


def add_frozen_field_error(bucket_name: str, slug: str, field_name: str, actual: Any, expected: Any, errors: list[str]) -> None:
    errors.append(
        f"{bucket_name} slug '{slug}' field '{field_name}' expected {format_value(expected)}, found {format_value(actual)}"
    )


def validate_copy_seed(bucket_name: str, slug: str, copy_seed: Any, expected_copy_seed: dict[str, str], errors: list[str]) -> None:
    if not isinstance(copy_seed, dict):
        errors.append(f"{bucket_name} slug '{slug}' copySeed must be an object")
        return

    for field in REQUIRED_COPY_SEED_FIELDS:
        value = copy_seed.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{bucket_name} slug '{slug}' copySeed.{field} must be a non-empty string")

    if copy_seed != expected_copy_seed:
        add_frozen_field_error(bucket_name, slug, "copySeed", copy_seed, expected_copy_seed, errors)


def validate_categories(bucket_name: str, slug: str, categories: Any, expected_categories: list[str], errors: list[str]) -> None:
    if not isinstance(categories, list) or not categories:
        errors.append(f"{bucket_name} slug '{slug}' categories must be a non-empty list")
        return

    if not all(isinstance(category, str) and category.strip() for category in categories):
        errors.append(f"{bucket_name} slug '{slug}' categories must only contain non-empty strings")
        return

    if categories != expected_categories:
        add_frozen_field_error(bucket_name, slug, "categories", categories, expected_categories, errors)


def validate_item_shape(bucket_name: str, slug_label: str, item: Any, errors: list[str]) -> bool:
    if not isinstance(item, dict):
        errors.append(f"{bucket_name} slug '{slug_label}' entry must be an object")
        return False

    for field in REQUIRED_ITEM_FIELDS:
        if field not in item:
            errors.append(f"{bucket_name} slug '{slug_label}' missing field '{field}'")

    return True


def validate_item_against_expected(
    bucket_name: str,
    item: dict[str, Any],
    expected_item: dict[str, Any] | None,
    seen_slugs: set[str],
    errors: list[str],
) -> None:
    slug = item.get("slug")
    slug_label = slug if isinstance(slug, str) and slug.strip() else format_value(slug)
    if not validate_item_shape(bucket_name, slug_label, item, errors):
        return

    if not isinstance(slug, str) or not slug.strip():
        errors.append(f"{bucket_name} slug must be a non-empty string, found {format_value(slug)}")
        return

    if slug in seen_slugs:
        errors.append(f"{bucket_name} contains duplicate slug '{slug}'")
        return
    seen_slugs.add(slug)

    if expected_item is None:
        errors.append(f"{bucket_name} has unexpected slug '{slug}'")
        return

    for field in ("title", "group", "sourcePage"):
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{bucket_name} slug '{slug}' field '{field}' must be a non-empty string")
            continue
        if value != expected_item[field]:
            add_frozen_field_error(bucket_name, slug, field, value, expected_item[field], errors)

    if item.get("slug") != expected_item["slug"]:
        add_frozen_field_error(bucket_name, slug, "slug", item.get("slug"), expected_item["slug"], errors)

    source_page = item.get("sourcePage")
    if isinstance(source_page, str) and not source_page.startswith("https://gamemonetize.com/"):
        errors.append(f"{bucket_name} slug '{slug}' sourcePage must start with 'https://gamemonetize.com/'")

    validate_categories(bucket_name, slug, item.get("categories"), expected_item["categories"], errors)
    validate_copy_seed(bucket_name, slug, item.get("copySeed"), expected_item["copySeed"], errors)


def validate_bucket(bucket_name: str, bucket: Any, expected_items: dict[str, dict[str, Any]], errors: list[str]) -> None:
    if not isinstance(bucket, list):
        errors.append(f"'{bucket_name}' must be a list")
        return

    if len(bucket) != len(expected_items):
        errors.append(f"{bucket_name} must contain {len(expected_items)} entries, found {len(bucket)}")

    seen_slugs: set[str] = set()
    invalid_slug_values: list[Any] = []
    for item in bucket:
        slug = item.get("slug") if isinstance(item, dict) else None
        if isinstance(slug, str) and slug.strip():
            validate_item_against_expected(bucket_name, item, expected_items.get(slug), seen_slugs, errors)
        else:
            validate_item_against_expected(bucket_name, item, None, seen_slugs, errors)
            invalid_slug_values.append(slug)

    missing_slugs = sorted(set(expected_items) - seen_slugs)
    for slug in missing_slugs:
        errors.append(f"{bucket_name} missing expected slug '{slug}'")

    if invalid_slug_values:
        formatted = ", ".join(format_value(value) for value in invalid_slug_values)
        errors.append(f"{bucket_name} contains invalid slug values: {formatted}")


def validate_source_payload(data: Any, errors: list[str]) -> None:
    if not isinstance(data, dict):
        errors.append("source payload must be a JSON object")
        return

    for bucket_name, expected_items in EXPECTED_SOURCE_BINDINGS.items():
        validate_bucket(bucket_name, data.get(bucket_name), expected_items, errors)


def resolve_manifest_media_for_source_page(source_page: str) -> dict[str, str]:
    html = fetch_html(source_page)
    return extract_embed_fields(html)


def validate_manifest_media_fields(
    bucket_name: str,
    item: Any,
    expected_item: dict[str, Any] | None,
    errors: list[str],
) -> None:
    if not isinstance(item, dict):
        return

    slug = item.get("slug")
    slug_label = slug if isinstance(slug, str) and slug.strip() else format_value(slug)

    iframe_url = item.get("iframeUrl")
    if not isinstance(iframe_url, str) or not iframe_url.strip():
        errors.append(f"{bucket_name} slug '{slug_label}' iframeUrl must be a non-empty string")
    elif not iframe_url.startswith(EXPECTED_IFRAME_PREFIX):
        errors.append(
            f"{bucket_name} slug '{slug_label}' iframeUrl must start with '{EXPECTED_IFRAME_PREFIX}'"
        )

    thumb = item.get("thumb")
    if not isinstance(thumb, str) or not thumb.strip():
        errors.append(f"{bucket_name} slug '{slug_label}' thumb must be a non-empty string")
    elif not thumb.startswith(EXPECTED_THUMB_PREFIX):
        errors.append(
            f"{bucket_name} slug '{slug_label}' thumb must start with '{EXPECTED_THUMB_PREFIX}'"
        )

    if expected_item is None:
        return

    if not isinstance(iframe_url, str) or not iframe_url.strip():
        return
    if not isinstance(thumb, str) or not thumb.strip():
        return
    if not iframe_url.startswith(EXPECTED_IFRAME_PREFIX) or not thumb.startswith(EXPECTED_THUMB_PREFIX):
        return

    try:
        expected_media = resolve_manifest_media_for_source_page(expected_item["sourcePage"])
    except Exception as exc:
        errors.append(
            f"{bucket_name} slug '{slug_label}' could not resolve expected media from frozen sourcePage: {exc}"
        )
        return

    if iframe_url != expected_media["iframeUrl"]:
        add_frozen_field_error(bucket_name, slug_label, "iframeUrl", iframe_url, expected_media["iframeUrl"], errors)
    if thumb != expected_media["thumb"]:
        add_frozen_field_error(bucket_name, slug_label, "thumb", thumb, expected_media["thumb"], errors)


def validate_manifest_payload(data: Any, errors: list[str]) -> None:
    if not isinstance(data, dict):
        errors.append("manifest payload must be a JSON object")
        return

    release_group = data.get("releaseGroup")
    if release_group != EXPECTED_RELEASE_GROUP:
        errors.append(
            f"manifest releaseGroup expected {format_value(EXPECTED_RELEASE_GROUP)}, found {format_value(release_group)}"
        )

    for bucket_name, expected_items in EXPECTED_SOURCE_BINDINGS.items():
        bucket = data.get(bucket_name)
        validate_bucket(bucket_name, bucket, expected_items, errors)
        if isinstance(bucket, list):
            for item in bucket:
                slug = item.get("slug") if isinstance(item, dict) else None
                expected_item = expected_items.get(slug) if isinstance(slug, str) else None
                validate_manifest_media_fields(bucket_name, item, expected_item, errors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-file",
        default=str(DEFAULT_SOURCE_FILE),
        help="Path to round-two frozen source JSON",
    )
    parser.add_argument(
        "--manifest",
        help="Path to round-two manifest JSON",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    try:
        data = load_source_list(Path(args.source_file))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    validate_source_payload(data, errors)

    if args.manifest:
        try:
            manifest_data = load_source_list(Path(args.manifest))
        except Exception as exc:
            print(f"ERROR: {exc}")
            return 1

        validate_manifest_payload(manifest_data, errors)

    if errors:
        print("ROUND_TWO_SOURCE_LIST_VERIFICATION_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ROUND_TWO_SOURCE_LIST_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
