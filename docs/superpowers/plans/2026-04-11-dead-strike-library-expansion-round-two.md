# DEAD STRIKE Round Two Library Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不重做首页结构的前提下，为 `dead-strike.com` 新增 22 个 round-two 射击/生存详情页、扩展目录页与分类页承接，并将结果 push 到远端。

**Architecture:** 先冻结 round-two 候选源清单，再用本地 Python 工具把来源页补全为包含 iframe、缩略图、分类与文案种子字段的 manifest。随后把 manifest 同步进 `game-library.js` 和 22 个静态详情页，并只扩展 `games/`、三大分类页与 `sitemap.xml`，不改首页结构。

**Tech Stack:** Static HTML/CSS/vanilla JS, Python 3 scripts, existing `tools/verify_game_library.py` / `tools/verify_player_layout.py`, local `python -m http.server`, web-access for source validation.

---

## 文件结构

### 新建

- `docs/superpowers/plans/2026-04-11-dead-strike-library-expansion-round-two.md`
- `tools/round_two_sources.json`
- `tools/verify_round_two_release.py`
- `tools/build_round_two_manifest.py`
- `tools/test_round_two_manifest.py`
- `tools/round_two_manifest.json`
- `tools/render_round_two_pages.py`
- `fps-shooting-game-3d-gun-game/index.html`
- `infantry-attack-battle-3d-fps/index.html`
- `duty-call-modern-warfate-2/index.html`
- `command-strike-fps-2/index.html`
- `cod-duty-call-fps/index.html`
- `special-forces-war-zombie-attack/index.html`
- `shooterz-io/index.html`
- `blocky-siege/index.html`
- `moon-clash-heroes/index.html`
- `nightwalkers-io/index.html`
- `combat-zombie-warfare/index.html`
- `sniper-mission-war/index.html`
- `sniper-ghost-shooter/index.html`
- `sniper-shot-3d/index.html`
- `urban-sniper-multiplayer/index.html`
- `zombie-defense-war-z-survival/index.html`
- `zombie-defense-last-stand/index.html`
- `grand-zombie-swarm/index.html`
- `zombie-vacation-2/index.html`
- `zombie-shooter-3d/index.html`
- `zombie-survival-pixel-apocalypse/index.html`
- `pixel-multiplayer-survival-zombie/index.html`

### 修改

- `game-library.js`
- `games/index.html`
- `games/zombie-games/index.html`
- `games/fps-games/index.html`
- `games/shooter-games/index.html`
- `sitemap.xml`
- `tools/verify_game_library.py`

### 只读参考

- `site.js`
- `site.css`
- `call-of-ops-3-zombies/index.html`
- `tools/library_utils.py`

## 冻结后的候选源清单

### 22 个主候选

| 组别 | 标题 | slug | sourcePage |
| --- | --- | --- | --- |
| tactical-fps | FPS Shooting Game: 3D Gun Game | `fps-shooting-game-3d-gun-game` | `https://gamemonetize.com/fps-shooting-game-3d-gun-game-game` |
| tactical-fps | Infantry Attack:Battle 3D FPS | `infantry-attack-battle-3d-fps` | `https://gamemonetize.com/infantry-attack-battle-3d-fps-game` |
| tactical-fps | Duty Call Modern Warfate 2 | `duty-call-modern-warfate-2` | `https://gamemonetize.com/duty-call-modern-warfate-2-game` |
| tactical-fps | Command Strike FPS 2 | `command-strike-fps-2` | `https://gamemonetize.com/command-strike-fps-2-game` |
| tactical-fps | COD Duty Call FPS | `cod-duty-call-fps` | `https://gamemonetize.com/cod-duty-call-fps-game` |
| tactical-fps | Special Forces War Zombie Attack | `special-forces-war-zombie-attack` | `https://gamemonetize.com/special-forces-war-zombie-attack-game` |
| multiplayer-arena | ShooterZ.io | `shooterz-io` | `https://gamemonetize.com/shooterz-io-game` |
| multiplayer-arena | Blocky Siege | `blocky-siege` | `https://gamemonetize.com/blocky-siege-game` |
| multiplayer-arena | Moon Clash Heroes | `moon-clash-heroes` | `https://gamemonetize.com/moon-clash-heroes-game` |
| multiplayer-arena | Nightwalkers.io | `nightwalkers-io` | `https://gamemonetize.com/nightwalkers-io-game` |
| multiplayer-arena | Combat Zombie Warfare | `combat-zombie-warfare` | `https://gamemonetize.com/combat-zombie-warfare-game` |
| sniper | Sniper Mission War | `sniper-mission-war` | `https://gamemonetize.com/sniper-mission-war-game` |
| sniper | Sniper Ghost Shooter | `sniper-ghost-shooter` | `https://gamemonetize.com/sniper-ghost-shooter-game` |
| sniper | Sniper Shot 3D | `sniper-shot-3d` | `https://gamemonetize.com/sniper-shot-3d-game` |
| sniper | Urban Sniper Multiplayer | `urban-sniper-multiplayer` | `https://gamemonetize.com/urban-sniper-multiplayer-game` |
| zombie-defense | Zombie defense: War Z Survival | `zombie-defense-war-z-survival` | `https://gamemonetize.com/zombie-defense-war-z-survival-game` |
| zombie-defense | Zombie Defense: Last Stand | `zombie-defense-last-stand` | `https://gamemonetize.com/zombie-defense-last-stand-game` |
| zombie-defense | Grand Zombie Swarm | `grand-zombie-swarm` | `https://gamemonetize.com/grand-zombie-swarm-game` |
| zombie-defense | Zombie Vacation 2 | `zombie-vacation-2` | `https://gamemonetize.com/zombie-vacation-2-game` |
| adjacent-long-tail | Zombie Shooter 3D | `zombie-shooter-3d` | `https://gamemonetize.com/zombie-shooter-3d-game` |
| adjacent-long-tail | Zombie Survival Pixel Apocalypse | `zombie-survival-pixel-apocalypse` | `https://gamemonetize.com/zombie-survival-pixel-apocalypse-game` |
| adjacent-long-tail | Pixel multiplayer survival zombie | `pixel-multiplayer-survival-zombie` | `https://gamemonetize.com/pixel-multiplayer-survival-zombie-game` |

### 4 个备胎

| 组别 | 标题 | slug | sourcePage |
| --- | --- | --- | --- |
| reserve | Counter Strike : Survival | `counter-strike-survival` | `https://gamemonetize.com/counter-strike-survival-game` |
| reserve | 3D Sniper Shooting Game | `3d-sniper-shooting-game` | `https://gamemonetize.com/3d-sniper-shooting-game-game` |
| reserve | Tank War Multiplayer | `tank-war-multiplayer` | `https://gamemonetize.com/tank-war-multiplayer-game` |
| reserve | The Rise Of Zombies | `the-rise-of-zombies` | `https://gamemonetize.com/the-rise-of-zombies-game` |

### Task 0: 创建隔离 worktree 与分支

**Files:**
- Create: `.worktrees/round-two-seo-expansion/`

- [ ] **Step 1: 创建独立 worktree 和工作分支**

Run: `git -c safe.directory=D:/llm/seo_7/DEAD-STRIKE worktree add .worktrees/round-two-seo-expansion -b codex/dead-strike-round-two-expansion`
Expected: 输出包含 `Preparing worktree` 与新分支 `codex/dead-strike-round-two-expansion`

- [ ] **Step 2: 确认新 worktree 可写且状态干净**

Run: `git -C .worktrees/round-two-seo-expansion -c safe.directory=D:/llm/seo_7/DEAD-STRIKE status --short`
Expected: 无输出

### Task 1: 冻结 round-two 来源清单并建立 release 验证器

**Files:**
- Create: `tools/round_two_sources.json`
- Create: `tools/verify_round_two_release.py`

- [ ] **Step 1: 先写会失败的 release 验证器**

```python
#!/usr/bin/env python3
import json
from pathlib import Path

path = Path("tools/round_two_sources.json")
data = json.loads(path.read_text(encoding="utf-8"))

primary = data["primary"]
backup = data["backup"]

expected_primary = {
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
expected_backup = {
    "counter-strike-survival",
    "3d-sniper-shooting-game",
    "tank-war-multiplayer",
    "the-rise-of-zombies",
}

assert len(primary) == 22
assert len(backup) == 4
assert {item["slug"] for item in primary} == expected_primary
assert {item["slug"] for item in backup} == expected_backup
assert sum(item["group"] == "tactical-fps" for item in primary) == 6
assert sum(item["group"] == "multiplayer-arena" for item in primary) == 5
assert sum(item["group"] == "sniper" for item in primary) == 4
assert sum(item["group"] == "zombie-defense" for item in primary) == 4
assert sum(item["group"] == "adjacent-long-tail" for item in primary) == 3

for bucket_name, bucket in (("primary", primary), ("backup", backup)):
    for item in bucket:
        assert item["sourcePage"].startswith("https://gamemonetize.com/")
        assert item["slug"]
        assert item["title"]
        assert item["categories"]
        assert bucket_name

print("ROUND_TWO_SOURCE_LIST_VERIFIED")
```

- [ ] **Step 2: 运行验证器，确认在数据文件缺失时失败**

Run: `python tools/verify_round_two_release.py`
Expected: FAIL，报 `FileNotFoundError` 或 `No such file`

- [ ] **Step 3: 写入冻结后的 `tools/round_two_sources.json`**

按下列 schema 写入完整主清单和备胎清单，主清单与备胎必须与上方冻结表逐条一致：

```json
{
  "primary": [
    {
      "title": "FPS Shooting Game: 3D Gun Game",
      "slug": "fps-shooting-game-3d-gun-game",
      "group": "tactical-fps",
      "sourcePage": "https://gamemonetize.com/fps-shooting-game-3d-gun-game-game",
      "categories": ["fps", "shooter", "military", "tactical"],
      "copySeed": {
        "tempo": "fast-rush",
        "scene": "urban-warzone",
        "intent": "modern-commando"
      }
    }
  ],
  "backup": [
    {
      "title": "Counter Strike : Survival",
      "slug": "counter-strike-survival",
      "group": "reserve",
      "sourcePage": "https://gamemonetize.com/counter-strike-survival-game",
      "categories": ["fps", "shooter", "multiplayer", "military"],
      "copySeed": {
        "tempo": "team-firefight",
        "scene": "war-map",
        "intent": "survival-counterstrike"
      }
    }
  ]
}
```

要求：

- `primary` 中包含上表 22 条
- `backup` 中包含上表 4 条
- 每条记录都必须包含 `title`、`slug`、`group`、`sourcePage`、`categories`、`copySeed`
- `copySeed` 必须包含 `tempo`、`scene`、`intent`

- [ ] **Step 4: 再次运行验证器，确认来源清单冻结成功**

Run: `python tools/verify_round_two_release.py`
Expected: PASS，输出 `ROUND_TWO_SOURCE_LIST_VERIFIED`

- [ ] **Step 5: 提交来源清单与验证器**

```bash
git add tools/round_two_sources.json tools/verify_round_two_release.py
git commit -m "feat: freeze dead strike round two source roster"
```

### Task 2: 生成带 iframe 与缩略图的 round-two manifest

**Files:**
- Create: `tools/build_round_two_manifest.py`
- Create: `tools/test_round_two_manifest.py`
- Create: `tools/round_two_manifest.json`
- Modify: `tools/verify_round_two_release.py`

- [ ] **Step 1: 先写会失败的 manifest 解析测试**

```python
#!/usr/bin/env python3
from tools.build_round_two_manifest import extract_embed_fields

html = """
<html>
  <head>
    <meta property="og:image" content="https://img.gamemonetize.com/demo/512x384.jpg" />
  </head>
  <body>
    <iframe src="https://html5.gamemonetize.co/demo/"></iframe>
  </body>
</html>
"""

fields = extract_embed_fields(html)
assert fields["iframeUrl"] == "https://html5.gamemonetize.co/demo/"
assert fields["thumb"] == "https://img.gamemonetize.com/demo/512x384.jpg"
print("ROUND_TWO_MANIFEST_PARSER_VERIFIED")
```

- [ ] **Step 2: 运行测试，确认在解析器缺失时失败**

Run: `python tools/test_round_two_manifest.py`
Expected: FAIL，报 `ModuleNotFoundError` 或 `ImportError`

- [ ] **Step 3: 实现 `tools/build_round_two_manifest.py`**

```python
#!/usr/bin/env python3
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen


def extract_embed_fields(html: str) -> dict[str, str]:
    iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', html, re.I)
    image_match = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html, re.I)
    if not iframe_match:
        raise ValueError("Missing iframe src in source page")
    if not image_match:
        raise ValueError("Missing og:image in source page")
    return {
        "iframeUrl": iframe_match.group(1).strip(),
        "thumb": image_match.group(1).strip(),
    }


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 DEAD-STRIKE round-two builder"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def build_manifest(source_file: Path) -> dict:
    source = json.loads(source_file.read_text(encoding="utf-8"))
    manifest = {"releaseGroup": "expansion-2026-04", "primary": [], "backup": []}

    for bucket in ("primary", "backup"):
      for item in source[bucket]:
        html = fetch_html(item["sourcePage"])
        enriched = dict(item)
        enriched.update(extract_embed_fields(html))
        manifest[bucket].append(enriched)

    return manifest


def main() -> None:
    source_file = Path("tools/round_two_sources.json")
    out_file = Path("tools/round_two_manifest.json")
    manifest = build_manifest(source_file)
    out_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ROUND_TWO_MANIFEST_WRITTEN: {out_file}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 扩展 release 验证器，要求 manifest 具备 iframe 与缩略图**

把 `tools/verify_round_two_release.py` 扩展为可接受 `--manifest tools/round_two_manifest.json`，并增加以下断言：

```python
assert item["iframeUrl"].startswith("https://html5.gamemonetize.")
assert item["thumb"].startswith("https://img.gamemonetize.com/")
```

- [ ] **Step 5: 运行解析测试与 manifest 生成**

Run: `python tools/test_round_two_manifest.py`
Expected: PASS，输出 `ROUND_TWO_MANIFEST_PARSER_VERIFIED`

Run: `python tools/build_round_two_manifest.py`
Expected: PASS，输出 `ROUND_TWO_MANIFEST_WRITTEN: tools/round_two_manifest.json`

Run: `python tools/verify_round_two_release.py --manifest tools/round_two_manifest.json`
Expected: PASS，输出 `ROUND_TWO_SOURCE_LIST_VERIFIED`

- [ ] **Step 6: 提交 manifest 构建工具**

```bash
git add tools/build_round_two_manifest.py tools/test_round_two_manifest.py tools/round_two_manifest.json tools/verify_round_two_release.py
git commit -m "feat: build round two manifest from source pages"
```

### Task 3: 把 round-two 数据接入 `game-library.js`，先以非 live 方式落库

**Files:**
- Modify: `game-library.js`
- Modify: `tools/verify_game_library.py`

- [ ] **Step 1: 先让共享库验证器对 round-two 数据报错**

在 `tools/verify_game_library.py` 增加 round-two 校验：

```python
ROUND_TWO_RELEASE_GROUP = "expansion-2026-04"
ROUND_TWO_EXPECTED = 22

round_two_games = [game for game in games if game.get("releaseGroup") == ROUND_TWO_RELEASE_GROUP]
if len(round_two_games) != ROUND_TWO_EXPECTED:
    errors.append(
        f"Expected {ROUND_TWO_EXPECTED} round-two games in releaseGroup '{ROUND_TWO_RELEASE_GROUP}', found {len(round_two_games)}"
    )
```

- [ ] **Step 2: 运行共享库验证器，确认因 round-two 数据不存在而失败**

Run: `python tools/verify_game_library.py`
Expected: FAIL，输出包含 `Expected 22 round-two games`

- [ ] **Step 3: 把 22 条 manifest 记录写入 `game-library.js`**

每条 round-two 记录必须使用如下结构，先以 `isLive: false` 进入库，避免在页面生成前触发缺页报错：

```json
{
  "slug": "command-strike-fps-2",
  "title": "Command Strike FPS 2",
  "href": "/command-strike-fps-2/",
  "iframeUrl": "https://html5.gamemonetize.co/fiogowuzog6jowbgvabdxrcqaub4cubc/",
  "thumb": "https://img.gamemonetize.com/fiogowuzog6jowbgvabdxrcqaub4cubc/512x384.jpg",
  "categories": ["fps", "shooter", "military", "multiplayer"],
  "releaseGroup": "expansion-2026-04",
  "related": [
    "duty-call-modern-warfate-2",
    "command-strike-fps-2",
    "cod-duty-call-fps",
    "dead-strike",
    "sniper-master",
    "pubg-hack"
  ],
  "isLive": false
}
```

同时完成以下更新：

- 将 22 条新 slug 写入合适的 fallback pools，但首页 `playerStrip`、`popular`、`fresh` 不改结构、不换位
- 扩展 `categoryPages.zombie-games.slugs`
- 扩展 `categoryPages.fps-games.slugs`
- 扩展 `categoryPages.shooter-games.slugs`

- [ ] **Step 4: 重新运行共享库验证器，确认 round-two 已入库**

Run: `python tools/verify_game_library.py`
Expected: PASS，输出 `GAME_LIBRARY_VERIFIED`

- [ ] **Step 5: 提交共享库数据接入**

```bash
git add game-library.js tools/verify_game_library.py
git commit -m "feat: stage round two library metadata"
```

### Task 4: 用生成器产出 22 个详情页，然后把 round-two 条目标记为 live

**Files:**
- Create: `tools/render_round_two_pages.py`
- Modify: `game-library.js`
- Create: `fps-shooting-game-3d-gun-game/index.html`
- Create: `infantry-attack-battle-3d-fps/index.html`
- Create: `duty-call-modern-warfate-2/index.html`
- Create: `command-strike-fps-2/index.html`
- Create: `cod-duty-call-fps/index.html`
- Create: `special-forces-war-zombie-attack/index.html`
- Create: `shooterz-io/index.html`
- Create: `blocky-siege/index.html`
- Create: `moon-clash-heroes/index.html`
- Create: `nightwalkers-io/index.html`
- Create: `combat-zombie-warfare/index.html`
- Create: `sniper-mission-war/index.html`
- Create: `sniper-ghost-shooter/index.html`
- Create: `sniper-shot-3d/index.html`
- Create: `urban-sniper-multiplayer/index.html`
- Create: `zombie-defense-war-z-survival/index.html`
- Create: `zombie-defense-last-stand/index.html`
- Create: `grand-zombie-swarm/index.html`
- Create: `zombie-vacation-2/index.html`
- Create: `zombie-shooter-3d/index.html`
- Create: `zombie-survival-pixel-apocalypse/index.html`
- Create: `pixel-multiplayer-survival-zombie/index.html`

- [ ] **Step 1: 先让布局验证在新页集合上失败**

Run: `python tools/verify_player_layout.py --new-detail-pages`
Expected: FAIL，输出包含若干 `Missing page`

- [ ] **Step 2: 实现 `tools/render_round_two_pages.py`**

渲染器读入 `tools/round_two_manifest.json`，为每条主记录写出一个页面。模板骨架必须直接沿用现有 detail page 顺序：

```python
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | Play Online | DEAD STRIKE</title>
  <meta name="description" content="{description}" />
  <meta name="keywords" content="{keywords}" />
  <meta name="robots" content="index,follow,max-image-preview:large" />
  <link rel="canonical" href="https://dead-strike.com/{slug}/" />
  <link rel="stylesheet" href="/site.css" />
</head>
<body>
  <main class="shell arcade-shell">
    <section class="section detail-stage" id="play">
      <div class="arcade-stage detail-stage-grid">
        <div class="arcade-main detail-main-column">
          <div class="player-shell arcade-player-shell" id="playerShell">
            <iframe class="player-frame arcade-player-frame" src="{iframe_url}" title="{title}" loading="eager" referrerpolicy="strict-origin-when-cross-origin" allow="fullscreen *; gamepad *"></iframe>
          </div>
          <div data-player-strip="auto" aria-label="Recommended games"></div>
          <div class="arcade-titlebar detail-titlebar">
            <div>
              <h1 class="arcade-title">{title}</h1>
              <p class="arcade-subtitle">{description}</p>
            </div>
          </div>
          <div class="compat-note">{compat_html}</div>
          <div class="article-grid">{article_html}</div>
        </div>
        <aside class="arcade-sidebar detail-sidebar">{sidebar_html}</aside>
      </div>
    </section>
  </main>
  <script>window.DEAD_STRIKE_PAGE = {{ slug: "{slug}" }};</script>
  <script src="/game-library.js"></script>
  <script src="/site.js"></script>
</body>
</html>"""
```

要求：

- 所有 22 页都包含 `data-player-strip="auto"`
- 所有 22 页都包含 `data-home-popular` 与 `data-home-fresh`
- 描述、关键词、正文文案基于 `copySeed` 与 `categories` 生成，不能逐页完全重复
- 底部脚本顺序必须是 `DEAD_STRIKE_PAGE` -> `/game-library.js` -> `/site.js`

- [ ] **Step 3: 运行渲染器，生成 22 个页面**

Run: `python tools/render_round_two_pages.py --manifest tools/round_two_manifest.json --repo-root .`
Expected: PASS，输出 `ROUND_TWO_PAGES_WRITTEN: 22`

- [ ] **Step 4: 把 22 条 round-two 记录从 `isLive: false` 切换为 `isLive: true`**

完成后再次确认：

- 每条 `href` 指向对应新目录
- `validate_live_files()` 不再报缺页
- round-two 新页可以出现在 fallback pools 和 related recommendations 中

- [ ] **Step 5: 运行静态验证**

Run: `python tools/verify_player_layout.py --new-detail-pages`
Expected: PASS，输出 `PLAYER_LAYOUT_PAGE_CHECKS_VERIFIED`

Run: `python tools/verify_game_library.py`
Expected: PASS，输出 `GAME_LIBRARY_VERIFIED`

- [ ] **Step 6: 提交 round-two 详情页生成结果**

```bash
git add game-library.js tools/render_round_two_pages.py fps-shooting-game-3d-gun-game infantry-attack-battle-3d-fps duty-call-modern-warfate-2 command-strike-fps-2 cod-duty-call-fps special-forces-war-zombie-attack shooterz-io blocky-siege moon-clash-heroes nightwalkers-io combat-zombie-warfare sniper-mission-war sniper-ghost-shooter sniper-shot-3d urban-sniper-multiplayer zombie-defense-war-z-survival zombie-defense-last-stand grand-zombie-swarm zombie-vacation-2 zombie-shooter-3d zombie-survival-pixel-apocalypse pixel-multiplayer-survival-zombie
git commit -m "feat: add round two shooter mission pages"
```

### Task 5: 更新目录页、分类页与 sitemap

**Files:**
- Modify: `games/index.html`
- Modify: `games/zombie-games/index.html`
- Modify: `games/fps-games/index.html`
- Modify: `games/shooter-games/index.html`
- Modify: `sitemap.xml`
- Modify: `tools/verify_round_two_release.py`

- [ ] **Step 1: 先写会失败的 coverage 检查**

在 `tools/verify_round_two_release.py` 中增加 `--check-live-coverage` 模式，并加入以下检查：

```python
required_files = [
    Path("games/index.html"),
    Path("games/zombie-games/index.html"),
    Path("games/fps-games/index.html"),
    Path("games/shooter-games/index.html"),
    Path("sitemap.xml"),
]

manifest = json.loads(Path("tools/round_two_manifest.json").read_text(encoding="utf-8"))
primary = manifest["primary"]

for file_path in required_files:
    text = file_path.read_text(encoding="utf-8")
    for item in primary:
        if file_path.name == "sitemap.xml":
            needle = f"https://dead-strike.com/{item['slug']}/"
            assert needle in text
```

额外要求：

- 每个主候选 slug 必须出现在 `games/index.html`
- 每个主候选 slug 必须至少出现在 1 个分类页
- 每个主候选 URL 必须出现在 `sitemap.xml`

- [ ] **Step 2: 运行 coverage 检查，确认目录与分类尚未承接这些新页**

Run: `python tools/verify_round_two_release.py --check-live-coverage`
Expected: FAIL，报若干缺失 slug

- [ ] **Step 3: 扩展 `games/index.html`**

做法：

- 在现有 “Freshly promoted game routes” 区块中加入 22 个新页卡片
- 把最强 8 页放在前两行：
  - `fps-shooting-game-3d-gun-game`
  - `command-strike-fps-2`
  - `shooterz-io`
  - `nightwalkers-io`
  - `sniper-mission-war`
  - `urban-sniper-multiplayer`
  - `zombie-defense-last-stand`
  - `zombie-shooter-3d`

卡片结构直接沿用现有目录页模式：

```html
<a class="list-card" href="/fps-shooting-game-3d-gun-game/">
  <div class="list-media" style="background-image:url('https://img.gamemonetize.com/fiogowuzog6jowbgvabdxrcqaub4cubc/512x384.jpg')"></div>
  <div class="chip-row"><span>FPS</span><span>Shooter</span></div>
  <h3>FPS Shooting Game: 3D Gun Game</h3>
  <p>Modern commando missions with short firefights, direct browser launch, and tactical pressure.</p>
</a>
```

- [ ] **Step 4: 扩展三大分类页**

分类挂载规则：

- `games/zombie-games/index.html`：`special-forces-war-zombie-attack`、`nightwalkers-io`、`combat-zombie-warfare`、`zombie-defense-war-z-survival`、`zombie-defense-last-stand`、`grand-zombie-swarm`、`zombie-vacation-2`、`zombie-shooter-3d`、`zombie-survival-pixel-apocalypse`、`pixel-multiplayer-survival-zombie`
- `games/fps-games/index.html`：`fps-shooting-game-3d-gun-game`、`infantry-attack-battle-3d-fps`、`duty-call-modern-warfate-2`、`command-strike-fps-2`、`cod-duty-call-fps`、`shooterz-io`、`blocky-siege`、`sniper-mission-war`
- `games/shooter-games/index.html`：全部 22 页都应可被收录，但文案说明仍强调 wider shooter mix

- [ ] **Step 5: 更新 `sitemap.xml`**

对 22 个 round-two 页都写入：

```xml
<url>
  <loc>https://dead-strike.com/fps-shooting-game-3d-gun-game/</loc>
  <lastmod>2026-04-11</lastmod>
</url>
```

同时把这 5 个 hub 页的 `lastmod` 改为 `2026-04-11`：

- `/`
- `/games/`
- `/games/zombie-games/`
- `/games/fps-games/`
- `/games/shooter-games/`

- [ ] **Step 6: 重新运行 coverage 检查**

Run: `python tools/verify_round_two_release.py --manifest tools/round_two_manifest.json --check-live-coverage`
Expected: PASS，输出 `ROUND_TWO_SOURCE_LIST_VERIFIED`

- [ ] **Step 7: 提交承接页与 sitemap 更新**

```bash
git add games/index.html games/zombie-games/index.html games/fps-games/index.html games/shooter-games/index.html sitemap.xml tools/verify_round_two_release.py
git commit -m "feat: expand round two discovery hubs and sitemap"
```

### Task 6: 最终验证、推送并交付

**Files:**
- Test: `tools/verify_round_two_release.py`
- Test: `tools/verify_game_library.py`
- Test: `tools/verify_player_layout.py`

- [ ] **Step 1: 运行所有静态验证**

Run: `python tools/verify_round_two_release.py --manifest tools/round_two_manifest.json --check-live-coverage`
Expected: PASS

Run: `python tools/verify_game_library.py`
Expected: PASS

Run: `python tools/verify_player_layout.py --page games/index.html --page games/zombie-games/index.html --page games/fps-games/index.html --page games/shooter-games/index.html --new-detail-pages`
Expected: PASS

- [ ] **Step 2: 启动本地静态预览，并做代表性页面响应检查**

Run: `python -m http.server 8000`
Expected: `Serving HTTP on 0.0.0.0 port 8000`

另开一个终端后运行：

Run: `powershell -Command "(Invoke-WebRequest http://127.0.0.1:8000/fps-shooting-game-3d-gun-game/).StatusCode"`
Expected: `200`

Run: `powershell -Command "(Invoke-WebRequest http://127.0.0.1:8000/nightwalkers-io/).StatusCode"`
Expected: `200`

Run: `powershell -Command "(Invoke-WebRequest http://127.0.0.1:8000/games/).StatusCode"`
Expected: `200`

- [ ] **Step 3: 查看 git 状态，确认只包含本轮变更**

Run: `git status --short`
Expected: 只出现本轮新增/修改文件，无意外删除

- [ ] **Step 4: 提交最终整合提交**

```bash
git add game-library.js games/index.html games/zombie-games/index.html games/fps-games/index.html games/shooter-games/index.html sitemap.xml tools fps-shooting-game-3d-gun-game infantry-attack-battle-3d-fps duty-call-modern-warfate-2 command-strike-fps-2 cod-duty-call-fps special-forces-war-zombie-attack shooterz-io blocky-siege moon-clash-heroes nightwalkers-io combat-zombie-warfare sniper-mission-war sniper-ghost-shooter sniper-shot-3d urban-sniper-multiplayer zombie-defense-war-z-survival zombie-defense-last-stand grand-zombie-swarm zombie-vacation-2 zombie-shooter-3d zombie-survival-pixel-apocalypse pixel-multiplayer-survival-zombie
git commit -m "feat: expand dead strike round two game library"
```

- [ ] **Step 5: 推送分支**

Run: `git push -u origin codex/dead-strike-round-two-expansion`
Expected: 输出包含 `branch 'codex/dead-strike-round-two-expansion' set up to track 'origin/codex/dead-strike-round-two-expansion'`
