#!/usr/bin/env python3
import argparse
import copy
import json
import sys
from html import escape
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from library_utils import load_library


TARGET_RELEASE_GROUP = "expansion-2026-04"
EXPECTED_PAGE_COUNT = 22
SITE_ORIGIN = "https://dead-strike.com"
GA_ID = "G-RFTD58PLB8"
FONT_HREF = "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"

TEMPO_TEXT = {
    "fast-rush": "fast-rush pacing",
    "frontline-push": "frontline push momentum",
    "mission-surge": "mission surge pressure",
    "breach-and-clear": "breach-and-clear tempo",
    "combat-sprint": "combat sprint flow",
    "panic-firefight": "panic-firefight urgency",
    "live-match-loop": "live-match loop energy",
    "flank-and-peek": "flank-and-peek tempo",
    "jetpack-skirmish": "jetpack skirmish speed",
    "after-dark-scramble": "after-dark scramble pressure",
    "horde-crossfire": "horde-crossfire chaos",
    "patient-trigger": "patient trigger discipline",
    "silent-takedown": "silent takedown rhythm",
    "steady-breath": "steady-breath focus",
    "lane-lock-duel": "lane-lock duel pacing",
    "wave-holdout": "wave-holdout tension",
    "pressure-escalation": "pressure-escalation survival",
    "mass-horde-crush": "mass-horde crush pressure",
    "resort-siege": "resort-siege panic",
    "run-and-gun": "run-and-gun speed",
    "scrappy-survival": "scrappy survival tempo",
    "online-scavenge": "online scavenge tension",
}

SCENE_TEXT = {
    "urban-warzone": "an urban warzone",
    "fortified-checkpoint": "a fortified checkpoint",
    "modern-battlefield": "a modern battlefield",
    "industrial-complex": "an industrial complex",
    "enemy-stronghold": "an enemy stronghold",
    "infected-warzone": "an infected warzone",
    "open-killbox": "an open killbox",
    "voxel-battle-lanes": "voxel battle lanes",
    "lunar-outpost": "a lunar outpost",
    "haunted-streets": "haunted streets",
    "ruined-combat-zone": "a ruined combat zone",
    "battlefield-overwatch": "battlefield overwatch lanes",
    "shadowy-ruins": "shadowy ruins",
    "rooftop-range": "a rooftop range",
    "city-skyline": "a city skyline",
    "barricaded-base": "a barricaded base",
    "collapsed-outpost": "a collapsed outpost",
    "city-perimeter": "a city perimeter",
    "abandoned-holiday-zone": "an abandoned holiday zone",
    "infected-corridor": "an infected corridor",
    "pixel-doomsday-town": "a pixel doomsday town",
    "blocky-wasteland": "a blocky wasteland",
}

INTENT_TEXT = {
    "modern-commando": "modern commando pushes",
    "infantry-breakthrough": "infantry breakthrough pressure",
    "special-ops-patrol": "special-ops patrol missions",
    "command-unit-raider": "command-unit raiding",
    "loadout-driven-shooter": "loadout-driven gunplay",
    "elite-zombie-suppression": "elite zombie suppression",
    "drop-in-arena-duel": "drop-in arena duels",
    "block-style-teamfight": "block-style teamfights",
    "hero-shooter-showdown": "hero-shooter showdowns",
    "survive-online-chaos": "survive-online chaos",
    "squad-vs-undead-match": "squad-vs-undead matches",
    "mission-based-marksmanship": "mission-based marksmanship",
    "stealth-assassin-vantage": "stealth-assassin vantage play",
    "clean-one-shot-focus": "clean one-shot focus",
    "urban-overwatch-pvp": "urban overwatch PvP",
    "last-line-defense": "last-line defense",
    "fortify-until-dawn": "fortify-until-dawn pressure",
    "crowd-control-survivor": "crowd-control survival",
    "vacation-nightmare-defense": "vacation-nightmare defense",
    "straight-ahead-zombie-blast": "straight-ahead zombie blasting",
    "retro-undead-endurance": "retro undead endurance",
    "pixel-coop-undead-survival": "pixel co-op undead survival",
}

GROUP_PROFILES = {
    "tactical-fps": {
        "rating": "TACTICAL FPS",
        "group_label": "tactical browser FPS",
        "meta": "Push through {scene} with {tempo} and {intent} in this tactical browser FPS mission.",
        "subtitle": "{title} favors direct firefights, short objective loops, and a military lane that stays readable from drop-in to reload.",
        "compat": "{title} plays best in fullscreen when {scene} opens into longer sightlines. Use the source tab for the cleanest load, then pivot into more tactical missions from the icon walls.",
        "article_one_title": "Compact firefights shaped by {scene_label}",
        "article_one_body": "This page leans on mission pressure rather than wandering downtime. {tempo_cap} keeps every reload meaningful, while {intent} gives the run a clear commando angle from the opening push onward.",
        "article_two_title": "Built for players who want military tempo without menu friction",
        "article_two_body": "The loop suits players chasing clean browser restarts, familiar assault controls, and a shooter lane that gets to the firefight quickly instead of padding the setup.",
        "highlights_title": "Mission rhythm",
        "highlights_intro": "{title} is strongest when you want a short tactical session with obvious pressure beats.",
        "controls_title": "Tactical controls",
        "controls_intro": "Expect familiar keyboard-and-mouse FPS inputs so the focus stays on {tempo} and lane control instead of onboarding.",
        "footer": "{title} on DEAD STRIKE pairs {scene_label} with {intent} for a straight-to-action tactical mission page.",
    },
    "multiplayer-arena": {
        "rating": "ARENA FPS",
        "group_label": "multiplayer arena shooter",
        "meta": "Queue into {scene} with {tempo} and {intent} in this drop-in multiplayer arena shooter.",
        "subtitle": "{title} puts match flow first, keeping browser-ready firefights centered on duels, flanks, and quick respawn energy.",
        "compat": "{title} works best in fullscreen when {scene} turns into a busy lane fight. Open the source tab if you want the cleanest session handoff, then hop through more arena picks from the icon walls.",
        "article_one_title": "Fast match loops built around {scene_label}",
        "article_one_body": "The best part here is how quickly the action starts. {tempo_cap} drives every exchange, and {intent} keeps the page feeling like a live arena queue instead of a slow campaign map.",
        "article_two_title": "A wider PvP branch for players who want instant rematches",
        "article_two_body": "This entry broadens the site's shooter mix with lighter setup, more repeatable rounds, and a stronger focus on positioning, peeking, and out-trading human opponents.",
        "highlights_title": "Arena loop",
        "highlights_intro": "{title} works well when you want browser PvP with clear match pressure and quick re-entry.",
        "controls_title": "Arena controls",
        "controls_intro": "Standard shooter inputs make it easy to settle into {tempo}, track lanes, and keep the next duel moving.",
        "footer": "{title} on DEAD STRIKE expands the arena lane with {scene_label}, {tempo}, and repeat-ready PvP pressure.",
    },
    "sniper": {
        "rating": "SNIPER OPS",
        "group_label": "sniper mission shooter",
        "meta": "Set up over {scene} with {tempo} and {intent} in this sniper mission shooter built around precision.",
        "subtitle": "{title} slows the pace just enough to reward angles, patience, and clean shots while still staying browser-session friendly.",
        "compat": "{title} benefits from fullscreen when {scene} stretches your sightlines. Use the source tab for the cleanest launch, then move into more precision-heavy sniper picks from the icon walls.",
        "article_one_title": "Precision pressure framed by {scene_label}",
        "article_one_body": "The appeal here is how much space each shot gets. {tempo_cap} sharpens the pacing, while {intent} keeps the page rooted in deliberate marksman play instead of spray-heavy firefights.",
        "article_two_title": "A better fit for players who enjoy setup, timing, and payoff",
        "article_two_body": "This branch gives DEAD STRIKE a calmer but sharper lane, trading raw crowd control for angle management, cleaner picks, and browser-friendly mission resets.",
        "highlights_title": "Marksman loop",
        "highlights_intro": "{title} rewards steadier hands, cleaner openings, and one more try when the first angle misses.",
        "controls_title": "Sniper controls",
        "controls_intro": "The controls stay familiar, so most of the challenge comes from {tempo} and lining up the next high-value shot.",
        "footer": "{title} on DEAD STRIKE turns {scene_label} into a precision lane built around {intent} and patient browser sniper play.",
    },
    "zombie-defense": {
        "rating": "Z DEFENSE",
        "group_label": "zombie defense shooter",
        "meta": "Hold {scene} with {tempo} and {intent} in this zombie defense shooter focused on wave pressure.",
        "subtitle": "{title} leans into barricades, survival pressure, and repeated holdout moments that fit short browser sessions well.",
        "compat": "{title} feels best in fullscreen when {scene} fills with a larger horde. Open the source tab for the cleanest load, then rotate into more undead defense pages from the icon walls.",
        "article_one_title": "Wave pressure anchored in {scene_label}",
        "article_one_body": "This page sells the feeling of holding one more line against the undead. {tempo_cap} keeps the threat climbing, and {intent} pushes every session toward fortify-or-fall tension.",
        "article_two_title": "A stronger holdout branch for players who like pressure over wandering",
        "article_two_body": "Instead of roaming too wide, the page keeps the loop tight: defend space, stabilize the lane, and see how long the setup can survive the next spike in undead pressure.",
        "highlights_title": "Holdout loop",
        "highlights_intro": "{title} works best when you want wave-based pressure, defense fantasy, and quick replay value.",
        "controls_title": "Defense controls",
        "controls_intro": "The session uses familiar shooter keys so the focus stays on {tempo}, target priority, and surviving the next breach.",
        "footer": "{title} on DEAD STRIKE adds a hold-the-line defense page shaped by {scene_label} and {intent}.",
    },
    "adjacent-long-tail": {
        "rating": "Z ACTION",
        "group_label": "long-tail zombie shooter",
        "meta": "Charge through {scene} with {tempo} and {intent} in this long-tail zombie shooter built for quick browser action.",
        "subtitle": "{title} sits slightly outside the core branches, giving the site a more flexible zombie-action lane without losing immediate browser access.",
        "compat": "{title} is easiest to read in fullscreen when {scene} starts to crowd the play space. Use the source tab for the cleanest load, then branch into more zombie-action picks from the icon walls.",
        "article_one_title": "Straight-ahead zombie action from {scene_label}",
        "article_one_body": "This page is about momentum and readability. {tempo_cap} keeps the session moving, while {intent} gives the run a clearer flavor than a generic undead shooter clone.",
        "article_two_title": "Useful long-tail coverage for players who want variety without friction",
        "article_two_body": "These pages widen the catalog with alternate tones like pixel survival, direct 3D blasting, or multiplayer scavenging, while still fitting the site's overall shooter lane.",
        "highlights_title": "Action loop",
        "highlights_intro": "{title} is best when you want a lighter, faster zombie run that still feels distinct inside the catalog.",
        "controls_title": "Action controls",
        "controls_intro": "The build keeps standard shooter inputs, so it takes only a moment to settle into {tempo} and start clearing pressure.",
        "footer": "{title} on DEAD STRIKE broadens the zombie-action lane with {scene_label}, {tempo}, and {intent}.",
    },
}


def sentence_case_token(value: str) -> str:
    return value.replace("-", " ")


def title_case_token(value: str) -> str:
    return sentence_case_token(value).title()


def humanize(mapping: dict[str, str], key: str) -> str:
    return mapping.get(key, sentence_case_token(key))


def dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


class RenderContext:
    def __init__(self, library: dict):
        self.library = library
        self.games = {
            game["slug"]: game
            for game in library.get("games", [])
            if isinstance(game, dict) and isinstance(game.get("slug"), str)
        }

    def canonical_slug(self, game: dict) -> str:
        canonical = game.get("canonicalSlug")
        if isinstance(canonical, str) and canonical:
            return canonical
        return game["slug"]

    def renderable_game(self, slug: str) -> dict | None:
        game = self.games.get(slug)
        if not game:
            return None
        return self.games.get(self.canonical_slug(game), game)

    def is_live(self, game: dict | None) -> bool:
        return bool(game and game.get("isLive"))

    def get_pool(self, pool_name: str) -> list[str]:
        value = self.library.get("pools", {})
        for part in pool_name.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        return value if isinstance(value, list) else []

    def dedupe_games(self, slugs: list[str], exclude_slugs: set[str], limit: int) -> list[dict]:
        exclude = set(exclude_slugs)
        seen: set[str] = set()
        results: list[dict] = []
        for slug in slugs:
            if len(results) >= limit or slug in exclude:
                continue
            game = self.games.get(slug)
            if not self.is_live(game):
                continue
            game = self.renderable_game(slug)
            if not self.is_live(game):
                continue
            canonical = self.canonical_slug(game)
            if canonical in exclude or canonical in seen:
                continue
            seen.add(canonical)
            results.append(game)
        return results

    def get_pool_games(self, pool_name: str, exclude_slugs: set[str], limit: int = 12) -> list[dict]:
        combined = list(self.get_pool(pool_name))
        fill_order = self.library.get("renderRules", {}).get("homePoolFillOrder", {}).get(pool_name, [])
        for fallback in fill_order:
            if isinstance(fallback, str):
                combined.extend(self.get_pool(fallback))
        return self.dedupe_games(combined, exclude_slugs, limit)

    def get_related_games(self, slug: str, limit: int = 12) -> list[dict]:
        current = self.games.get(slug)
        if not current:
            return []
        current_renderable = self.renderable_game(slug)
        exclude = {self.canonical_slug(current_renderable)} if current_renderable else {slug}
        combined = list(current.get("related", []))
        categories = set(current.get("categories", []))
        render_rules = self.library.get("renderRules", {})
        for rule in render_rules.get("categoryFallbackPriority", []):
            if isinstance(rule, dict) and rule.get("category") in categories and isinstance(rule.get("pool"), str):
                combined.extend(self.get_pool(rule["pool"]))
        for pool_name in render_rules.get("terminalFallbackPools", []):
            if isinstance(pool_name, str):
                combined.extend(self.get_pool(pool_name))
        return self.dedupe_games(combined, exclude, limit)


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def live_release_copy(library: dict, release_group: str) -> dict:
    rendered = copy.deepcopy(library)
    for game in rendered.get("games", []):
        if isinstance(game, dict) and game.get("releaseGroup") == release_group:
            game["isLive"] = True
    return rendered


def ensure_round_two_manifest(manifest: dict, library: dict) -> tuple[str, list[dict]]:
    release_group = manifest.get("releaseGroup")
    if release_group != TARGET_RELEASE_GROUP:
        raise ValueError(f"Manifest releaseGroup must be '{TARGET_RELEASE_GROUP}', found '{release_group}'")
    primary = manifest.get("primary")
    if not isinstance(primary, list) or len(primary) != EXPECTED_PAGE_COUNT:
        raise ValueError(f"Manifest primary must contain {EXPECTED_PAGE_COUNT} entries")

    games_by_slug = {
        game["slug"]: game
        for game in library.get("games", [])
        if isinstance(game, dict) and isinstance(game.get("slug"), str)
    }
    for entry in primary:
        slug = entry.get("slug")
        if not isinstance(slug, str) or slug not in games_by_slug:
            raise ValueError(f"Manifest slug missing from library: {slug}")
        if games_by_slug[slug].get("releaseGroup") != release_group:
            raise ValueError(f"Library slug '{slug}' must stay in releaseGroup '{release_group}'")
    return release_group, primary


def render_card(game: dict, css_class: str) -> str:
    href = escape(game["href"], quote=True)
    title = escape(game["title"])
    thumb = escape(game["thumb"], quote=True)
    return (
        f'<a aria-label="{title}" class="{css_class}" href="{href}">'
        f'<img alt="{title}" decoding="async" loading="lazy" src="{thumb}"/>'
        f'<span class="sr-only">{title}</span>'
        "</a>"
    )


def render_player_strip(games: list[dict]) -> str:
    cards = "".join(render_card(game, "player-strip-card") for game in games)
    return f'<div aria-label="Recommended games" data-player-strip="auto"><div class="player-strip-grid">{cards}</div></div>'


def render_sidebar_wall(games: list[dict], hook: str, label: str) -> str:
    cards = "".join(render_card(game, "sidebar-icon-card") for game in games)
    return (
        '<section class="sidebar-icon-panel sidebar-icon-panel-flat">'
        f'<div aria-label="{escape(label)}" {hook}><div class="sidebar-icon-grid">{cards}</div></div>'
        "</section>"
    )


def build_keywords(entry: dict, group_label: str, scene_label: str, intent_label: str) -> str:
    categories = [sentence_case_token(value) for value in entry.get("categories", [])[:4]]
    raw = [
        entry["title"].lower(),
        f"{group_label} online",
        categories[0] if categories else "shooter game",
        scene_label.lower(),
        intent_label.lower(),
        "dead strike",
    ]
    return ",".join(dedupe_preserve(raw))


def build_copy(entry: dict) -> dict:
    profile = GROUP_PROFILES[entry["group"]]
    tempo_label = humanize(TEMPO_TEXT, entry["copySeed"]["tempo"])
    scene_label = humanize(SCENE_TEXT, entry["copySeed"]["scene"])
    intent_label = humanize(INTENT_TEXT, entry["copySeed"]["intent"])
    tempo_cap = tempo_label[0].upper() + tempo_label[1:]
    scene_cap = scene_label[0].upper() + scene_label[1:]
    categories = [title_case_token(value) for value in entry.get("categories", [])]

    highlight_items = [
        f"{scene_cap} gives the match a more distinct backdrop than a generic browser shooter.",
        f"{tempo_cap} keeps the session readable for short play windows and quick re-queues.",
        f"{intent_label.capitalize()} helps this entry stand apart inside the {profile['group_label']} lane.",
        f"Category fit: {', '.join(categories[:3])}." if categories else "Category fit: Shooter.",
    ]
    return {
        "profile": profile,
        "meta_description": f"Play {entry['title']} online at DEAD STRIKE. " + profile["meta"].format(
            scene=scene_label,
            tempo=tempo_label,
            intent=intent_label,
        ),
        "subtitle": profile["subtitle"].format(
            title=entry["title"],
            tempo=tempo_label,
            scene=scene_label,
            intent=intent_label,
        ),
        "compat": profile["compat"].format(
            title=entry["title"],
            scene=scene_label,
            tempo=tempo_label,
            intent=intent_label,
        ),
        "article_one_title": profile["article_one_title"].format(scene_label=scene_label),
        "article_one_body": profile["article_one_body"].format(
            tempo_cap=tempo_cap,
            intent=intent_label,
        ),
        "article_two_title": profile["article_two_title"],
        "article_two_body": profile["article_two_body"].format(
            tempo=tempo_label,
            scene=scene_label,
            intent=intent_label,
        ),
        "highlights_title": profile["highlights_title"],
        "highlights_intro": profile["highlights_intro"].format(
            title=entry["title"],
            tempo=tempo_label,
            scene=scene_label,
            intent=intent_label,
        ),
        "highlight_items": highlight_items,
        "controls_title": profile["controls_title"],
        "controls_intro": profile["controls_intro"].format(
            tempo=tempo_label,
            scene=scene_label,
            intent=intent_label,
        ),
        "footer": profile["footer"].format(
            title=entry["title"],
            scene_label=scene_label,
            tempo=tempo_label,
            intent=intent_label,
        ),
        "keywords": build_keywords(entry, profile["group_label"], scene_label, intent_label),
        "scene_label": scene_label,
    }


def render_article_grid(copy_bits: dict) -> str:
    highlights = "".join(f"<li>{escape(item)}</li>" for item in copy_bits["highlight_items"])
    return (
        '<div class="article-grid">'
        f'<article class="article-card"><p class="eyebrow">Mission profile</p><h2 class="copy-headline">{escape(copy_bits["article_one_title"])}</h2><p>{escape(copy_bits["article_one_body"])}</p></article>'
        f'<article class="article-card"><p class="eyebrow">Why it fits</p><h2 class="copy-headline">{escape(copy_bits["article_two_title"])}</h2><p>{escape(copy_bits["article_two_body"])}</p></article>'
        "</div>"
        '<div class="article-grid">'
        f'<article class="article-card"><p class="eyebrow">Highlights</p><h2 class="copy-headline">{escape(copy_bits["highlights_title"])}</h2><p>{escape(copy_bits["highlights_intro"])}</p><ul>{highlights}</ul></article>'
        f'<article class="article-card"><p class="eyebrow">Game controls</p><h2 class="copy-headline">{escape(copy_bits["controls_title"])}</h2><p>{escape(copy_bits["controls_intro"])}</p><ul><li>WASD: move</li><li>Left click: shoot</li><li>Right click: aim</li><li>R: reload</li><li>Space: jump</li></ul></article>'
        "</div>"
    )


def render_page(entry: dict, context: RenderContext) -> str:
    copy_bits = build_copy(entry)
    slug = entry["slug"]
    title = entry["title"]
    page_title = f"{title} | Play Online | DEAD STRIKE"
    canonical = f"{SITE_ORIGIN}/{slug}/"
    related = context.get_related_games(slug, limit=12)
    popular = context.get_pool_games("popular", {slug}, limit=12)
    fresh = context.get_pool_games("fresh", {slug}, limit=12)
    if len(related) < 12:
        raise ValueError(f"Related recommendations for '{slug}' must yield 12 cards")
    if len(popular) < 6 or len(fresh) < 6:
        raise ValueError(f"Sidebar recommendations for '{slug}' must yield at least 6 cards")

    player_strip = render_player_strip(related)
    sidebar = render_sidebar_wall(popular, 'data-home-popular=""', "Popular Games icon wall") + render_sidebar_wall(
        fresh,
        'data-home-fresh=""',
        "New Games icon wall",
    )
    article_grid = render_article_grid(copy_bits)
    score = copy_bits["scene_label"].replace("a ", "").replace("an ", "").title()

    return f"""<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{escape(page_title)}</title>
<meta content="{escape(copy_bits["meta_description"], quote=True)}" name="description"/>
<meta content="{escape(copy_bits["keywords"], quote=True)}" name="keywords"/>
<meta content="index,follow,max-image-preview:large" name="robots"/>
<link href="{escape(canonical, quote=True)}" rel="canonical"/>
<link href="{SITE_ORIGIN}/social-preview.png" rel="image_src"/>
<meta content="website" property="og:type"/>
<meta content="{escape(page_title, quote=True)}" property="og:title"/>
<meta content="{escape(copy_bits["meta_description"], quote=True)}" property="og:description"/>
<meta content="{escape(canonical, quote=True)}" property="og:url"/>
<meta content="{escape(entry["thumb"], quote=True)}" property="og:image"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="{escape(page_title, quote=True)}" name="twitter:title"/>
<meta content="{escape(copy_bits["meta_description"], quote=True)}" name="twitter:description"/>
<meta content="{escape(entry["thumb"], quote=True)}" name="twitter:image"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="{FONT_HREF}" rel="stylesheet"/>
<link href="/favicon.ico" rel="icon" sizes="any"/>
<link href="/favicon.svg" rel="icon" type="image/svg+xml"/>
<link href="/icon.png" rel="icon" sizes="512x512" type="image/png"/>
<link href="/apple-touch-icon.png" rel="apple-touch-icon"/>
<link href="/site.css" rel="stylesheet"/>
<script async="" src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {{ dataLayer.push(arguments); }}
      gtag("js", new Date());
      gtag("config", "{GA_ID}");
    </script>
</head>
<body>
<div aria-hidden="true" class="backdrop-grid"></div>
<div aria-hidden="true" class="noise"></div>
<header class="topbar topbar-arcade">
<a aria-label="DEAD STRIKE home" class="brand" href="/">
<span class="brand-mark">DS</span>
<span class="brand-copy"><strong>DEAD STRIKE</strong><small>Browser shooter command</small></span>
</a>
<nav aria-label="Primary" class="topnav topnav-pills">
<a href="/games/">Games</a><a href="/games/zombie-games/">Zombie</a><a href="/games/fps-games/">FPS</a><a href="/games/shooter-games/">Shooter</a>
</nav>
</header>
<main class="shell arcade-shell">
<section class="section detail-stage" id="play">
<div class="arcade-stage detail-stage-grid">
<div class="arcade-main detail-main-column">
<div class="player-shell arcade-player-shell" id="playerShell">
<iframe allow="fullscreen *; gamepad *" class="player-frame arcade-player-frame" loading="eager" referrerpolicy="strict-origin-when-cross-origin" src="{escape(entry["iframeUrl"], quote=True)}" title="{escape(title, quote=True)}"></iframe>
</div>
{player_strip}
<div class="arcade-titlebar detail-titlebar">
<div>
<h1 class="arcade-title">{escape(title)}</h1>
<p class="arcade-subtitle">{escape(copy_bits["subtitle"])}</p>
</div>
<div class="arcade-title-actions">
<div aria-label="Game focus" class="rating-cluster"><span class="rating-stars">{escape(copy_bits["profile"]["rating"])}</span><span class="rating-score">{escape(score)}</span></div>
<button aria-label="Open fullscreen" class="icon-button" data-fullscreen-target="#playerShell" type="button">FS</button>
<a aria-label="Open source tab" class="icon-button" href="{escape(entry["iframeUrl"], quote=True)}" rel="noreferrer" target="_blank">GO</a>
</div>
</div>
<div class="compat-note"><div><p class="compat-note-kicker">Mission briefing</p><h2>Best in fullscreen or a dedicated tab.</h2><p>{escape(copy_bits["compat"])}</p></div><div class="compat-note-actions"><a class="button button-primary" href="{escape(entry["iframeUrl"], quote=True)}" rel="noreferrer" target="_blank">Open Full Game</a><a class="button button-ghost" href="/games/">Browse All Games</a></div></div>
{article_grid}
</div>
<aside class="arcade-sidebar detail-sidebar">{sidebar}</aside>
</div>
</section>
</main>
<footer class="footer"><div><p class="footer-brand">DEAD STRIKE</p><p class="footer-copy">{escape(copy_bits["footer"])}</p></div><div class="footer-links"><a href="/">Home</a><a href="/games/">Games</a><a href="/games/zombie-games/">Zombie</a><a href="/games/fps-games/">FPS</a></div></footer>
<script>
window.DEAD_STRIKE_PAGE = {{ slug: "{escape(slug)}" }};
</script>
<script src="/game-library.js"></script>
<script src="/site.js"></script>
</body>
</html>
"""


def write_round_two_pages(repo_root: Path, entries: list[dict], context: RenderContext) -> int:
    written = 0
    for entry in entries:
        target_dir = repo_root / entry["slug"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "index.html").write_text(render_page(entry, context), encoding="utf-8")
        written += 1
    return written


def write_library_with_live_round_two(repo_root: Path, library: dict, release_group: str) -> None:
    for game in library.get("games", []):
        if isinstance(game, dict) and game.get("releaseGroup") == release_group:
            game["isLive"] = True
    output = "window.DEAD_STRIKE_LIBRARY = " + json.dumps(library, indent=2) + ";\n"
    (repo_root / "game-library.js").write_text(output, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to tools/round_two_manifest.json")
    parser.add_argument("--repo-root", required=True, help="Repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (repo_root / manifest_path).resolve()

    library = load_library(repo_root / "game-library.js")
    manifest = load_manifest(manifest_path)
    release_group, entries = ensure_round_two_manifest(manifest, library)

    context = RenderContext(live_release_copy(library, release_group))
    written = write_round_two_pages(repo_root, entries, context)
    write_library_with_live_round_two(repo_root, library, release_group)

    print(f"ROUND_TWO_PAGES_WRITTEN: {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
