#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "index.html"
SITE_CSS = ROOT / "site.css"

EXPECTED_TOC_IDS = [
    "what-is-dead-strike",
    "how-to-play-dead-strike",
    "dead-strike-controls",
    "dead-strike-tips",
    "more-zombie-fps-games",
    "dead-strike-faq",
]

EXPECTED_FAQ = [
    (
        "What kind of game is Dead Strike?",
        "Dead Strike is a browser zombie FPS that focuses on wave survival, weapon upgrades, and quick mission pacing instead of long setup screens.",
    ),
    (
        "How do I play Dead Strike better after the first few waves?",
        "Start rotating earlier, upgrade before the arena gets crowded, and reload only when you have already created space with movement.",
    ),
    (
        "What are the controls for Dead Strike?",
        "Use W, A, S, and D to move, mouse to aim, click to shoot, Shift to sprint, Spacebar to jump or dodge, and number keys 1 through 6 to swap weapons.",
    ),
    (
        "Where can I find more games like Dead Strike?",
        "Use the More Zombie FPS Games section on this page, or jump into the Zombie Games, FPS Games, and Shooter Games hubs for similar browser missions.",
    ),
]


def fail(message: str) -> int:
    print("HOMEPAGE_SEO_VERIFICATION_FAILED")
    print(f"- {message}")
    return 1


def main() -> int:
    soup = BeautifulSoup(HOME.read_text(encoding="utf-8"), "html.parser")
    site_css = SITE_CSS.read_text(encoding="utf-8")

    toc = soup.select_one(".seo-toc")
    if toc is None:
        return fail("missing homepage SEO table of contents block")

    links = [link.get("href", "") for link in toc.select("a[href]")]
    expected_links = [f"#{section_id}" for section_id in EXPECTED_TOC_IDS]
    missing_links = [link for link in expected_links if link not in links]
    if missing_links:
        return fail(f"table of contents missing links: {', '.join(missing_links)}")

    content_section = soup.select_one(".arcade-seo-stack")
    if content_section is None:
        return fail("missing homepage SEO content stack")

    frame_card = soup.select_one(".arcade-frame-card")
    player_shell = soup.select_one("#playerShell")
    player_strip = soup.select_one("[data-player-strip]")
    titlebar = soup.select_one(".arcade-titlebar")
    compat_note = soup.select_one(".compat-note")

    if frame_card is None:
        return fail("homepage playable frame card is missing")
    if player_shell is None or player_shell.select_one("iframe") is None:
        return fail("homepage playable iframe shell is missing")
    if player_strip is None:
        return fail("homepage player strip is missing")
    if titlebar is None or compat_note is None:
        return fail("homepage titlebar or compatibility note is missing")

    frame_children = [child for child in frame_card.find_all(recursive=False)]
    expected_order = [player_shell, player_strip, titlebar, compat_note, toc]
    child_positions = []
    for node in expected_order:
        try:
            child_positions.append(frame_children.index(node))
        except ValueError:
            return fail("homepage SEO and play skeleton elements must stay in the main frame card")
    if child_positions != sorted(child_positions):
        return fail("homepage iframe, strip, titlebar, compat note, and TOC must keep the expected order")

    sidebar = soup.select_one("aside.arcade-sidebar")
    if sidebar is None:
        return fail("homepage arcade sidebar is missing")
    if sidebar.select_one("[data-home-popular]") is None:
        return fail("homepage popular sidebar icon wall is missing")
    if sidebar.select_one("[data-home-fresh]") is None:
        return fail("homepage fresh sidebar icon wall is missing")
    if sidebar.select_one(".sidebar-panel-title") is not None:
        return fail("homepage sidebar must stay frameless and title-free")
    sidebar_sections = sidebar.find_all("section", recursive=False)
    if len(sidebar_sections) != 2:
        return fail("homepage sidebar must keep exactly two direct icon-wall panels")
    if any("sidebar-icon-panel-flat" not in (section.get("class") or []) for section in sidebar_sections):
        return fail("homepage sidebar must keep two frameless icon panels")

    for section_id in EXPECTED_TOC_IDS[:-1]:
        node = soup.select_one(f"#{section_id}")
        if node is None:
            return fail(f"missing section id #{section_id}")

    faq_section = soup.select_one("section.faq-promoted")
    if faq_section is None:
        return fail("missing FAQ section")
    if faq_section.get("id") != "dead-strike-faq":
        return fail("FAQ section must expose #dead-strike-faq anchor")
    if re.search(r"#dead-strike-faq\s*\{[^}]*scroll-margin-top\s*:\s*104px", site_css, re.S) is None:
        return fail("FAQ anchor needs sticky-header scroll compensation in site.css")

    visible_faq = [
        (item.select_one("summary").get_text(strip=True), item.select_one("p").get_text(strip=True))
        for item in faq_section.select("details")
    ]
    if visible_faq != EXPECTED_FAQ:
        return fail("visible FAQ content does not match the expected Dead Strike SEO copy")

    faq_schema = None
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if data.get("@type") == "FAQPage":
            faq_schema = data
            break
    if faq_schema is None:
        return fail("missing FAQPage structured data")

    schema_faq = [
        (
            item.get("name", ""),
            item.get("acceptedAnswer", {}).get("text", ""),
        )
        for item in faq_schema.get("mainEntity", [])
    ]
    if schema_faq != EXPECTED_FAQ:
        return fail("FAQ structured data must match visible FAQ content exactly")

    toc_top = len(list(toc.previous_elements))
    content_top = len(list(content_section.previous_elements))
    faq_top = len(list(faq_section.previous_elements))
    if not toc_top < content_top < faq_top:
        return fail("table of contents, SEO content, and FAQ sections are out of order")

    more_games = soup.select_one("#more-zombie-fps-games")
    if more_games is None or more_games.select_one(".mini-cards-row") is None:
        return fail("more games section must keep the linked mini cards row")

    print("HOMEPAGE_SEO_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
