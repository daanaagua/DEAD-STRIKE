#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "tools" / "round_two_sources.json"

EXPECTED_PRIMARY_SLUGS = {
    "fps-shooting-game-3d-gun-game",
    "infantry-attack-battle-3d-fps",
    "duty-call-modern-warfate-2",
    "command-strike-fps-2",
    "cod-duty-call-fps",
    "special-forces-war-zombie-attack",
    "shooterz-io",
    "blocky-siege",
    "moon-clash-heroes",
    "nightwalkers-io",
    "combat-zombie-warfare",
    "sniper-mission-war",
    "sniper-ghost-shooter",
    "sniper-shot-3d",
    "urban-sniper-multiplayer",
    "zombie-defense-war-z-survival",
    "zombie-defense-last-stand",
    "grand-zombie-swarm",
    "zombie-vacation-2",
    "zombie-shooter-3d",
    "zombie-survival-pixel-apocalypse",
    "pixel-multiplayer-survival-zombie",
}

EXPECTED_BACKUP_SLUGS = {
    "counter-strike-survival",
    "3d-sniper-shooting-game",
    "tank-war-multiplayer",
    "the-rise-of-zombies",
}

EXPECTED_PRIMARY_GROUP_COUNTS = {
    "tactical-fps": 6,
    "multiplayer-arena": 5,
    "sniper": 4,
    "zombie-defense": 4,
    "adjacent-long-tail": 3,
}

REQUIRED_ITEM_FIELDS = [
    "title",
    "slug",
    "group",
    "sourcePage",
    "categories",
    "copySeed",
]

REQUIRED_COPY_SEED_FIELDS = ["tempo", "scene", "intent"]


def load_source_list(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bucket(
    bucket_name: str,
    bucket: list[dict],
    expected_slugs: set[str],
    errors: list[str],
) -> None:
    seen_slugs: set[str] = set()
    for index, item in enumerate(bucket):
        if not isinstance(item, dict):
            errors.append(f"{bucket_name}[{index}] must be an object")
            continue

        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                errors.append(f"{bucket_name}[{index}] missing field '{field}'")

        slug = item.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            errors.append(f"{bucket_name}[{index}].slug must be a non-empty string")
        elif slug in seen_slugs:
            errors.append(f"{bucket_name} contains duplicate slug '{slug}'")
        else:
            seen_slugs.add(slug)

        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{bucket_name}[{index}].title must be a non-empty string")

        group = item.get("group")
        if not isinstance(group, str) or not group.strip():
            errors.append(f"{bucket_name}[{index}].group must be a non-empty string")

        source_page = item.get("sourcePage")
        if not isinstance(source_page, str) or not source_page.startswith("https://gamemonetize.com/"):
            errors.append(f"{bucket_name}[{index}].sourcePage must start with 'https://gamemonetize.com/'")

        categories = item.get("categories")
        if not isinstance(categories, list) or not categories:
            errors.append(f"{bucket_name}[{index}].categories must be a non-empty list")
        elif not all(isinstance(category, str) and category.strip() for category in categories):
            errors.append(f"{bucket_name}[{index}].categories must only contain non-empty strings")

        copy_seed = item.get("copySeed")
        if not isinstance(copy_seed, dict):
            errors.append(f"{bucket_name}[{index}].copySeed must be an object")
        else:
            for field in REQUIRED_COPY_SEED_FIELDS:
                value = copy_seed.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{bucket_name}[{index}].copySeed.{field} must be a non-empty string")

    actual_slugs = {item.get("slug") for item in bucket if isinstance(item, dict)}
    if actual_slugs != expected_slugs:
        missing = sorted(expected_slugs - actual_slugs)
        extra = sorted(actual_slugs - expected_slugs)
        if missing:
            errors.append(f"{bucket_name} missing expected slugs: {', '.join(missing)}")
        if extra:
            errors.append(f"{bucket_name} has unexpected slugs: {', '.join(extra)}")


def validate_primary_group_counts(primary: list[dict], errors: list[str]) -> None:
    for group, expected_count in EXPECTED_PRIMARY_GROUP_COUNTS.items():
        actual_count = sum(item.get("group") == group for item in primary if isinstance(item, dict))
        if actual_count != expected_count:
            errors.append(f"primary group '{group}' expected {expected_count}, found {actual_count}")


def main() -> int:
    data = load_source_list(SOURCE_FILE)
    primary = data.get("primary")
    backup = data.get("backup")

    errors: list[str] = []

    if not isinstance(primary, list):
        errors.append("'primary' must be a list")
    if not isinstance(backup, list):
        errors.append("'backup' must be a list")

    if errors:
        print("ROUND_TWO_SOURCE_LIST_VERIFICATION_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    if len(primary) != 22:
        errors.append(f"primary must contain 22 entries, found {len(primary)}")
    if len(backup) != 4:
        errors.append(f"backup must contain 4 entries, found {len(backup)}")

    validate_bucket("primary", primary, EXPECTED_PRIMARY_SLUGS, errors)
    validate_bucket("backup", backup, EXPECTED_BACKUP_SLUGS, errors)
    validate_primary_group_counts(primary, errors)

    if errors:
        print("ROUND_TWO_SOURCE_LIST_VERIFICATION_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ROUND_TWO_SOURCE_LIST_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
