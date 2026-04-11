#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_round_two_manifest import extract_embed_fields
from tools import verify_round_two_release


SAMPLE_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta property="og:image" content="https://img.gamemonetize.com/example-thumb-512x384.png" />
    <title>Sample</title>
  </head>
  <body>
    <iframe
      src="https://html5.gamemonetize.com/example-game/"
      width="800"
      height="600"
    ></iframe>
  </body>
</html>
"""

LIVE_STYLE_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta property="og:image" content="https://img.gamemonetize.com/live-thumb/512x384.jpg" />
    <title>Live Style</title>
  </head>
  <body>
    <div class="clipboard" data-type="url">
      <textarea id="urlTextAreaId">https://html5.gamemonetize.co/live-game-id/</textarea>
      <button onClick="window.open('https://html5.gamemonetize.co/live-game-id/')">Open</button>
    </div>
    <iframe
      id="html5-GameEmbed"
      src="https://uncached.gamemonetize.co/live-game-id/"
      width="100%"
      height="600"
    ></iframe>
  </body>
</html>
"""

LIVE_STYLE_MISMATCHED_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta property="og:image" content="https://img.gamemonetize.com/live-thumb/512x384.jpg" />
    <title>Live Style Mismatch</title>
  </head>
  <body>
    <div class="clipboard" data-type="url">
      <textarea id="urlTextAreaId">https://html5.gamemonetize.co/game-b/</textarea>
      <button onClick="window.open('https://html5.gamemonetize.co/game-b/')">Open</button>
    </div>
    <iframe
      id="html5-GameEmbed"
      src="https://uncached.gamemonetize.co/game-a/"
      width="100%"
      height="600"
    ></iframe>
  </body>
</html>
"""


def assert_raises(callable_obj, expected_message: str) -> None:
    try:
        callable_obj()
    except Exception as exc:
        message = str(exc)
        assert expected_message in message, message
        return

    raise AssertionError(f"Expected exception containing {expected_message!r}")


def make_source_item(slug: str) -> dict:
    return {
        "title": f"Game {slug.upper()}",
        "slug": slug,
        "group": "test-group",
        "sourcePage": f"https://gamemonetize.com/{slug}-game",
        "categories": ["test", slug],
        "copySeed": {
            "tempo": f"{slug}-tempo",
            "scene": f"{slug}-scene",
            "intent": f"{slug}-intent",
        },
    }


def build_manifest_fixture() -> tuple[dict, dict[str, dict[str, str]]]:
    primary_items = [make_source_item("game-a"), make_source_item("game-b")]
    media_by_source_page = {
        "https://gamemonetize.com/game-a-game": {
            "iframeUrl": "https://html5.gamemonetize.com/game-a/",
            "thumb": "https://img.gamemonetize.com/game-a/512x384.jpg",
        },
        "https://gamemonetize.com/game-b-game": {
            "iframeUrl": "https://html5.gamemonetize.com/game-b/",
            "thumb": "https://img.gamemonetize.com/game-b/512x384.jpg",
        },
    }
    manifest = {
        "releaseGroup": verify_round_two_release.EXPECTED_RELEASE_GROUP,
        "primary": [],
        "backup": [],
    }
    for item in primary_items:
        enriched = deepcopy(item)
        enriched.update(media_by_source_page[item["sourcePage"]])
        manifest["primary"].append(enriched)
    return manifest, media_by_source_page


def validate_manifest_with_stubbed_media(manifest: dict, media_by_source_page: dict[str, dict[str, str]]) -> list[str]:
    fake_bindings = {
        "primary": {
            item["slug"]: make_source_item(item["slug"])
            for item in manifest["primary"]
        },
        "backup": {},
    }
    original_bindings = verify_round_two_release.EXPECTED_SOURCE_BINDINGS
    had_resolver = hasattr(verify_round_two_release, "resolve_manifest_media_for_source_page")
    original_resolver = getattr(verify_round_two_release, "resolve_manifest_media_for_source_page", None)
    verify_round_two_release.EXPECTED_SOURCE_BINDINGS = fake_bindings
    verify_round_two_release.resolve_manifest_media_for_source_page = media_by_source_page.__getitem__
    try:
        errors: list[str] = []
        verify_round_two_release.validate_manifest_payload(manifest, errors)
        return errors
    finally:
        verify_round_two_release.EXPECTED_SOURCE_BINDINGS = original_bindings
        if had_resolver:
            verify_round_two_release.resolve_manifest_media_for_source_page = original_resolver
        else:
            delattr(verify_round_two_release, "resolve_manifest_media_for_source_page")


def main() -> None:
    fields = extract_embed_fields(SAMPLE_HTML)
    assert fields == {
        "iframeUrl": "https://html5.gamemonetize.com/example-game/",
        "thumb": "https://img.gamemonetize.com/example-thumb-512x384.png",
    }

    live_style_fields = extract_embed_fields(LIVE_STYLE_HTML)
    assert live_style_fields == {
        "iframeUrl": "https://html5.gamemonetize.co/live-game-id/",
        "thumb": "https://img.gamemonetize.com/live-thumb/512x384.jpg",
    }

    assert_raises(
        lambda: extract_embed_fields(LIVE_STYLE_MISMATCHED_HTML),
        "Could not resolve canonical iframe URL",
    )

    manifest, media_by_source_page = build_manifest_fixture()
    manifest_errors = validate_manifest_with_stubbed_media(manifest, media_by_source_page)
    assert manifest_errors == [], manifest_errors

    swapped_manifest = deepcopy(manifest)
    swapped_manifest["primary"][0]["iframeUrl"] = manifest["primary"][1]["iframeUrl"]
    swapped_manifest["primary"][0]["thumb"] = manifest["primary"][1]["thumb"]
    swapped_manifest["primary"][1]["iframeUrl"] = manifest["primary"][0]["iframeUrl"]
    swapped_manifest["primary"][1]["thumb"] = manifest["primary"][0]["thumb"]
    swapped_errors = validate_manifest_with_stubbed_media(swapped_manifest, media_by_source_page)
    assert any("iframeUrl" in error for error in swapped_errors), swapped_errors
    assert any("thumb" in error for error in swapped_errors), swapped_errors

    print("ROUND_TWO_MANIFEST_PARSER_VERIFIED")


if __name__ == "__main__":
    main()
