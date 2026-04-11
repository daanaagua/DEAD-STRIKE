#!/usr/bin/env python3
import json
import re
import sys
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "tools" / "round_two_sources.json"
MANIFEST_FILE = ROOT / "tools" / "round_two_manifest.json"
RELEASE_GROUP = "expansion-2026-04"
HTML5_PREFIX = "https://html5.gamemonetize."
UNCACHED_PREFIX = "https://uncached.gamemonetize."
THUMB_PREFIX = "https://img.gamemonetize.com/"
USER_AGENT = "Mozilla/5.0 (compatible; round-two-manifest-builder/1.0)"


def load_source_list(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_html(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise RuntimeError(f"Failed to fetch {url}: HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc.reason}") from exc


class EmbedFieldParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.iframe_srcs: list[str] = []
        self.canonical_urls: list[str] = []
        self.og_image: str | None = None
        self._capture_textarea = False
        self._textarea_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value for name, value in attrs}
        tag_name = tag.lower()

        if tag_name == "meta":
            key = (attr_map.get("property") or attr_map.get("name") or "").lower()
            content = (attr_map.get("content") or "").strip()
            if key == "og:image" and content:
                self.og_image = content
            return

        if tag_name == "iframe":
            src = (attr_map.get("src") or "").strip()
            if src:
                self.iframe_srcs.append(src)
            return

        if tag_name == "textarea":
            self._capture_textarea = True
            self._textarea_chunks = []
            return

        onclick = (attr_map.get("onclick") or "").strip()
        if onclick:
            for url in extract_candidate_urls(onclick):
                self.canonical_urls.append(url)

    def handle_data(self, data: str) -> None:
        if self._capture_textarea:
            self._textarea_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "textarea" and self._capture_textarea:
            value = "".join(self._textarea_chunks).strip()
            if value:
                self.canonical_urls.append(value)
            self._capture_textarea = False
            self._textarea_chunks = []


def extract_candidate_urls(text: str) -> list[str]:
    return re.findall(r"https://[^\s'\"<>()]+", text)


def normalize_url_candidates(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for url in urls:
        cleaned = url.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)
    return normalized


def same_game_path(left: str, right: str) -> bool:
    return urlparse(left).path.rstrip("/") == urlparse(right).path.rstrip("/")


def resolve_iframe_url(iframe_srcs: list[str], canonical_urls: list[str]) -> str:
    if not iframe_srcs:
        raise ValueError("Missing iframe src in source page HTML")

    normalized_iframes = normalize_url_candidates(iframe_srcs)
    normalized_canonicals = normalize_url_candidates(canonical_urls)

    for src in normalized_iframes:
        if src.startswith(HTML5_PREFIX):
            return src

    html5_candidates = [url for url in normalized_canonicals if url.startswith(HTML5_PREFIX)]
    uncached_iframes = [src for src in normalized_iframes if src.startswith(UNCACHED_PREFIX)]
    for src in uncached_iframes:
        for candidate in html5_candidates:
            if same_game_path(src, candidate):
                return candidate

    if uncached_iframes and html5_candidates:
        raise ValueError(
            "Could not resolve canonical iframe URL from source page HTML; "
            f"iframe src {uncached_iframes[0]!r} had no matching html5 candidate"
        )

    if html5_candidates:
        return html5_candidates[0]

    first_iframe = normalized_iframes[0]
    raise ValueError(
        "Could not resolve canonical iframe URL from source page HTML; "
        f"found iframe src {first_iframe!r}"
    )


def extract_embed_fields(html: str) -> dict[str, str]:
    parser = EmbedFieldParser()
    parser.feed(html)
    parser.close()

    thumb = (parser.og_image or "").strip()
    if not thumb:
        raise ValueError("Missing og:image in source page HTML")
    if not thumb.startswith(THUMB_PREFIX):
        raise ValueError(f"og:image must start with {THUMB_PREFIX!r}, found {thumb!r}")

    iframe_url = resolve_iframe_url(parser.iframe_srcs, parser.canonical_urls)
    if not iframe_url.startswith(HTML5_PREFIX):
        raise ValueError(f"iframeUrl must start with {HTML5_PREFIX!r}, found {iframe_url!r}")

    return {"iframeUrl": iframe_url, "thumb": thumb}


def build_manifest(source_data: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "releaseGroup": RELEASE_GROUP,
        "primary": [],
        "backup": [],
    }

    for bucket_name in ("primary", "backup"):
        items = source_data.get(bucket_name)
        if not isinstance(items, list):
            raise ValueError(f"Source bucket {bucket_name!r} must be a list")

        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"Source bucket {bucket_name!r} contains non-object entries")

            source_page = item.get("sourcePage")
            slug = item.get("slug", "<unknown>")
            if not isinstance(source_page, str) or not source_page.strip():
                raise ValueError(f"{bucket_name} slug '{slug}' missing valid sourcePage")

            html = fetch_html(source_page)
            fields = extract_embed_fields(html)
            enriched = deepcopy(item)
            enriched.update(fields)
            manifest[bucket_name].append(enriched)

    return manifest


def write_manifest(manifest: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    try:
        source_data = load_source_list(SOURCE_FILE)
        manifest = build_manifest(source_data)
        write_manifest(manifest, MANIFEST_FILE)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    print("ROUND_TWO_MANIFEST_WRITTEN: tools/round_two_manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
