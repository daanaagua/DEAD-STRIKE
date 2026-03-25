# DEAD STRIKE Library Expansion Design

## Goal

Expand `dead-strike.com` with 15+ additional zombie / FPS / shooter browser game pages while updating the shared player UI so the site feels like a larger library without losing its lead-game focus.

## Current Context

- The site is a static HTML/CSS/JS project centered on `index.html`, `site.css`, and lightweight per-game `index.html` pages.
- The homepage currently features `DEAD STRIKE` as the lead iframe experience, with a right sidebar showing icon tiles plus per-game labels.
- Existing detail pages already follow a reusable pattern, but the layout order is inconsistent with the desired post-iframe discovery flow.
- The library already includes a mix of zombie, FPS, and shooter pages from iframe-friendly free sources, primarily Gamemonetize and the standalone `dead-strike.1games.io` embed.

## Product Decisions Confirmed

- Expansion direction: stay tightly aligned to zombie / FPS / shooter intent.
- Scope: add 15+ new games in this pass.
- UI scope: homepage and all game detail pages should adopt the new post-iframe recommendation strip.
- Content sources: prefer the current free embeddable sources already used by the site; allow other free iframe-friendly sources if they fit the theme and do not introduce obvious friction.
- UX direction: use the unified library layout approach rather than a full homepage portal remake.

## Experience Design

### Viewport Definitions

Use these viewport bands consistently for implementation, screenshots, and automated verification:

- Desktop: viewport width `>= 1180px`; primary screenshot target `1440 x 1200`
- Tablet: viewport width `768px - 1179px`; primary check target `1024 x 1366`
- Mobile: viewport width `<= 767px`; primary screenshot target `390 x 844`

### 1. Homepage

The homepage stays centered on `DEAD STRIKE` as the featured title, but the surrounding UI should immediately communicate that the site is now a broader game library.

Changes:

- Keep the hero iframe at the top of the main column.
- Add a two-row strip of recommended game icons directly below the iframe.
- Move the title, rating, fullscreen/open-tab controls, and compatibility note below that icon strip.
- Keep the article and FAQ sections, but ensure the homepage still links into deeper library routes.
- Convert the right sidebar panels into compact icon walls: no per-icon text labels, only panel headings such as `Popular Games` and `New Games`.

Concrete UI rules:

- Desktop homepage post-iframe strip: exactly 12 icons shown as `6 x 2` at `>= 1180px`.
- Tablet homepage post-iframe strip: exactly 8 icons shown as `4 x 2` from `768px` to `1179px`.
- Mobile homepage post-iframe strip: exactly 6 icons shown as `3 x 2` at `<= 767px`.
- Desktop sidebar icon walls: `3` columns with square thumbnails and no visible text labels under thumbnails.
- Tablet/mobile sidebar icon walls: still no text labels; grid may collapse, but each panel must stay visually dense and icon-only.

Result:

- The homepage remains a lead-game landing page for SEO and brand focus.
- The newly expanded library becomes visible sooner, above the fold and inside the main play flow.

### 2. Game Detail Pages

All detail pages should align more closely with the homepage play structure.

Changes:

- Keep the iframe first.
- Insert a two-row related-games icon strip immediately below the iframe.
- Place the game title, rating/tags, and action buttons after the icon strip.
- Keep supporting copy blocks below the main metadata area.
- Preserve a secondary sidebar for additional related missions or category routes where it already helps internal linking.

Concrete UI rules:

- Desktop detail-page post-iframe strip: exactly 12 icons shown as `6 x 2` at `>= 1180px`.
- Tablet detail-page post-iframe strip: exactly 8 icons shown as `4 x 2` from `768px` to `1179px`.
- Mobile detail-page post-iframe strip: exactly 6 icons shown as `3 x 2` at `<= 767px`.
- The post-iframe strip must appear in DOM order before the title/rating/action block on every detail page.
- If a page has fewer than the target count available from its related pool, it should still render two rows by filling from the broader shooter library rather than collapsing to one row.

Result:

- Users can jump to another game before scrolling into long-form copy.
- The layout becomes consistent across homepage and detail pages, which lowers maintenance cost for future game additions.

### 3. Library Density and Visual Behavior

To support a visibly larger catalog without making the UI noisy:

- Sidebar icons should use tighter spacing and remain purely visual.
- The post-iframe icon strips should use two compact rows with consistent thumbnail sizing.
- The icon strips should surface a curated mix of top performers, fresh additions, and strongly related genres.
- Mobile breakpoints should preserve the same ordering, with icon strips wrapping cleanly before metadata blocks.

Selection behavior:

- Homepage strip priority: lead with newly added games, then fill remaining slots with strong existing performers.
- Detail-page strip priority: first same-subgenre pages, then broader zombie/FPS/shooter alternatives.
- Homepage sidebar `Popular Games`: fixed icon set chosen from the strongest evergreen pages.
- Homepage sidebar `New Games`: fixed icon set chosen from the newly added pages in this release.

## Content Expansion Design

### Confirmed New Game Batch

This release should add these 16 new playable routes in the order listed below:

| Title | Local slug | Source page | iframe source | Thumbnail |
| --- | --- | --- | --- | --- |
| Call of Ops 3 Zombies | `call-of-ops-3-zombies` | `https://gamemonetize.com/call-of-ops-3-zombies-game` | `https://html5.gamemonetize.co/cj2i0xkpesbl0e3m3tqf5pqpc6fzvxoh/` | `https://img.gamemonetize.com/cj2i0xkpesbl0e3m3tqf5pqpc6fzvxoh/512x384.jpg` |
| Zombie Reform | `zombie-reform` | `https://gamemonetize.com/zombie-reform-game` | `https://html5.gamemonetize.co/warvlut0300fplhmljw6wwglp5v11dae/` | `https://img.gamemonetize.com/warvlut0300fplhmljw6wwglp5v11dae/512x384.jpg` |
| Zombie Incursion World | `zombie-incursion-world` | `https://gamemonetize.com/zombie-incursion-world-game` | `https://html5.gamemonetize.co/fpdudatpsx7v8d8pbanmcu5ptilf69vm/` | `https://img.gamemonetize.com/fpdudatpsx7v8d8pbanmcu5ptilf69vm/512x384.jpg` |
| Pixel Zombie Survival | `pixel-zombie-survival` | `https://gamemonetize.com/pixel-zombie-survival-game` | `https://html5.gamemonetize.co/p1kzu5rt2ccr02gzr1sf5sarx8if93er/` | `https://img.gamemonetize.com/p1kzu5rt2ccr02gzr1sf5sarx8if93er/512x384.jpg` |
| Zombie Last Guard | `zombie-last-guard` | `https://gamemonetize.com/zombie-last-guard-game` | `https://html5.gamemonetize.co/eyywle3xrpioeuwfmf6df1jcipppnlp1/` | `https://img.gamemonetize.com/eyywle3xrpioeuwfmf6df1jcipppnlp1/512x384.jpg` |
| Biozombie Outbreak | `biozombie-outbreak` | `https://gamemonetize.com/biozombie-outbreak-game` | `https://html5.gamemonetize.co/48csp3lbmdvja2zw83p2rnwosl8tmhgu/` | `https://img.gamemonetize.com/48csp3lbmdvja2zw83p2rnwosl8tmhgu/512x384.jpg` |
| Super Sergeant Zombies | `super-sergeant-zombies` | `https://gamemonetize.com/super-sergeant-zombies-game` | `https://html5.gamemonetize.co/74qw93iiv7my1825omj4pbxxskb4zo46/` | `https://img.gamemonetize.com/74qw93iiv7my1825omj4pbxxskb4zo46/512x384.jpg` |
| MineWar Soldiers vs Zombies | `minewar-soldiers-vs-zombies` | `https://gamemonetize.com/minewar-soldiers-vs-zombies-game` | `https://html5.gamemonetize.co/1jzax4ooric6e3qz75rw3zta730cwf6a/` | `https://img.gamemonetize.com/1jzax4ooric6e3qz75rw3zta730cwf6a/512x384.jpg` |
| Counter Craft Sniper | `counter-craft-sniper` | `https://gamemonetize.com/counter-craft-sniper-game` | `https://html5.gamemonetize.co/xrwzvqdm8dhzzqpc97crxfgabb2i6bvd/` | `https://img.gamemonetize.com/xrwzvqdm8dhzzqpc97crxfgabb2i6bvd/512x384.jpg` |
| Urban Sniper Multiplayer 2 | `urban-sniper-multiplayer-2` | `https://gamemonetize.com/urban-sniper-multiplayer-2-game` | `https://html5.gamemonetize.co/bfjzhrdpwl2rkyoxrop4l6bfkmx5f1v8/` | `https://img.gamemonetize.com/bfjzhrdpwl2rkyoxrop4l6bfkmx5f1v8/512x384.jpg` |
| Sniper Clash 3D | `sniper-clash-3d` | `https://gamemonetize.com/sniper-clash-3d-game` | `https://html5.gamemonetize.co/20qv2eol679xos3gu39edys4yvn2b8ed/` | `https://img.gamemonetize.com/20qv2eol679xos3gu39edys4yvn2b8ed/512x384.jpg` |
| Zombie Clash 3D | `zombie-clash-3d` | `https://gamemonetize.com/zombie-clash-3d-game` | `https://html5.gamemonetize.co/qf4bszktq31gtznbfro0ih23k7dg53ws/` | `https://img.gamemonetize.com/qf4bszktq31gtznbfro0ih23k7dg53ws/512x384.jpg` |
| Subway Clash 3D | `subway-clash-3d` | `https://gamemonetize.com/subway-clash-3d-game` | `https://html5.gamemonetize.co/nduhdua0yup2i0k4llj5wjplk62np2md/` | `https://img.gamemonetize.com/nduhdua0yup2i0k4llj5wjplk62np2md/512x384.jpg` |
| Rocket Clash 3D | `rocket-clash-3d` | `https://gamemonetize.com/rocket-clash-3d-game` | `https://html5.gamemonetize.co/jiybs4emy2vc1utvpov7qgfmgnzdwcaf/` | `https://img.gamemonetize.com/jiybs4emy2vc1utvpov7qgfmgnzdwcaf/512x384.jpg` |
| Fort Clash Survival | `fort-clash-survival` | `https://gamemonetize.com/fort-clash-survival-game` | `https://html5.gamemonetize.co/hwx6v25biq7www5qh9jxe7vjda61r1fg/` | `https://img.gamemonetize.com/hwx6v25biq7www5qh9jxe7vjda61r1fg/512x384.jpg` |
| Lone Wolf Strike | `lone-wolf-strike` | `https://gamemonetize.com/lone-wolf-strike-game` | `https://html5.gamemonetize.co/xlv6xmnkfwj27yes8ly9t73icin4dmda/` | `https://img.gamemonetize.com/xlv6xmnkfwj27yes8ly9t73icin4dmda/512x384.jpg` |

Embed failure is defined as any one of the following during local preview:

- iframe source does not load a playable shell within `15` seconds on desktop preview
- iframe source returns an obvious block, error, or blank state instead of playable content
- iframe source cannot be embedded with the same iframe pattern used by the rest of the site

Reserve candidates must be used only if one of the primary 16 fails under the criteria above, and must be substituted in this exact order:

1. `brutal-battle-royale-2` — `https://gamemonetize.com/brutal-battle-royale-2-game`
2. `universal-multiplayer-shooter` — `https://gamemonetize.com/universal-multiplayer-shooter-game`

The final shipped batch must contain at least `15` new pages even if one primary candidate is replaced.

### Selection Rules

New pages should be chosen using these filters:

- Strong relevance to zombie, FPS, shooter, combat survival, military firefight, wave defense, or closely adjacent action-shooter intents.
- Playable through direct iframe embedding without account requirements.
- Acceptable thumbnail availability for homepage, category, and related-game usage.
- Distinct enough from the current catalog to widen coverage rather than repeating near-identical pages.

### Target Library Shape

The new batch should broaden the catalog in several directions while staying within the same traffic cluster:

- Zombie survival shooters
- Military / tactical FPS missions
- Arcade shooters with strong overlap to current audience intent
- Wave-defense / arena survival shooters
- Sniper / precision shooter variants when they still fit the action cluster

### Page Model

Each new game page should include:

- A dedicated route with `/<slug>/index.html`
- Unique title, description, and canonical tags
- The embedded game iframe
- Short original supporting copy tailored to the game angle
- Internal links into hubs and nearby games
- Inclusion in one or more relevant category or recommendation surfaces

## Information Architecture

To prevent the expanded library from becoming fragmented, recommendations should be treated as a shared content pool rather than hard-coded in isolated pockets.

Recommended structure:

- Create one shared static game-data source, for example `game-library.js`, containing the metadata needed for thumbnails, hrefs, labels, categories, and source groupings.
- Homepage sidebar pools: `Popular Games`, `New Games`
- Homepage main-column strip: a curated playable-now selection
- Detail-page main-column strip: strongly related games, prioritizing same-intent alternatives
- Category pages: updated cards and internal links reflecting the newly added titles

This does not require introducing a build system. The site can stay static, but the HTML should be reorganized so recommendation clusters are easier to update consistently across pages.

Concrete implementation mechanism:

- Keep the site static.
- Store recommendation metadata in a shared static JS file rather than copying dozens of hand-edited icon blocks into every page.
- Use lightweight DOM hooks in homepage/detail templates so the same data source can render sidebar icon walls and post-iframe strips consistently.
- Keep per-page SEO copy and metadata in each HTML file; only recommendation pools and reusable card/icon metadata should be centralized.

## Implementation Boundaries

### Files Likely Affected

- `index.html`
- `site.css`
- `site.js`
- `game-library.js` or equivalent new shared static data file
- `games/index.html`
- `games/zombie-games/index.html`
- `games/fps-games/index.html`
- `games/shooter-games/index.html`
- 16 new `/<slug>/index.html` detail pages listed in the confirmed game batch
- Exhaustive current playable detail-page inventory that must adopt the new shared player order as of `2026-03-25`:
  - `battledudes-io/index.html`
  - `blocky-combat-swat-original-2026/index.html`
  - `challenge-the-zombies/index.html`
  - `dusk-warz/index.html`
  - `edge-of-survival/index.html`
  - `fps-shooting-survival-sim/index.html`
  - `guns-vs-magic/index.html`
  - `minecraft-noob-vs-zombies-3/index.html`
  - `modern-fps-strike-zombie-gun-war-ops/index.html`
  - `multigun-arena-zombie-survival/index.html`
  - `noob-vs-zombie/index.html`
  - `noob-vs-zombie-2/index.html`
  - `pubg-hack/index.html`
  - `rpg-soldier-shooter/index.html`
  - `sniper-master/index.html`
  - `space-adventure-noobiks-battle-vs-zombies/index.html`
  - `super-cat-free-fire/index.html`
  - `survival-wave-zombie-multiplayer/index.html`
  - `wacky-strike/index.html`
  - `zombie-survival-last-stand/index.html`
- `docs/index.html` is explicitly out of scope because it is the external landing page, not a playable detail page.
- Supporting SEO/static files if game URLs need to be surfaced there

### Non-Goals

- No framework migration
- No CMS introduction
- No dynamic data layer
- No unrelated visual rebrand of the whole site
- No broad topic expansion outside the zombie / FPS / shooter cluster in this pass

## SEO and Internal Linking

The expansion should reinforce topical authority rather than merely inflate page count.

- New pages should be woven into the homepage, category hubs, and related-game clusters.
- Category pages should be refreshed so the added pages are crawlable within a few clicks.
- Titles and descriptions should remain readable and distinct, avoiding boilerplate duplication.
- The homepage should continue signaling that the site is both a lead-game destination and a discoverable shooter library.

## QA and Validation

Before push, the implementation should be checked through:

- Local static preview of homepage and multiple detail pages
- Desktop screenshot confirmation for homepage, one existing updated detail page, and at least two newly added detail pages
- Tablet screenshot confirmation for homepage and at least one updated detail page using the defined tablet viewport
- Mobile screenshot confirmation for homepage, one existing updated detail page, and at least two newly added detail pages
- Link sanity checks for newly added pages and category routes
- Layout verification that sidebar icons no longer show per-item labels
- Automated verification across every existing and new detail page that the post-iframe two-row icon strip appears before the title/rating block in DOM order
- Automated verification across homepage and every detail page that the post-iframe strip renders the expected two-row count for its breakpoint target
- Automated verification across homepage sidebar panels that icon tiles render without visible text labels in the DOM structure used for display

## Rollout Outcome

If implemented as designed, `dead-strike.com` should feel substantially larger within the current visual language:

- A broader library of 15+ new themed games
- Stronger game discovery directly around the player
- A more compact sidebar that scales with future additions
- A reusable page structure that makes future expansions faster and safer
