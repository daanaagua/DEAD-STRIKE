# DEAD STRIKE

DEAD STRIKE is a static browser shooter site focused on zombie FPS and action game traffic. The project is designed for direct play, SEO-friendly game pages, and lightweight deployment on Cloudflare Workers/Pages.

## Live Links

- Main site: `https://dead-strike.com/`
- GitHub repository: `https://github.com/daanaagua/DEAD-STRIKE`
- GitHub Pages landing page: `https://daanaagua.github.io/DEAD-STRIKE/`

## What Is Included

- Game-first homepage with a large playable stage
- Category hubs for zombie, FPS, and shooter intent
- Individual game detail pages with summaries and controls
- Static assets only: HTML, CSS, JS, images, manifest, sitemap, robots, ads.txt

## Main Files

- `index.html` - primary landing page
- `site.css` - shared styles
- `site.js` - small UI behaviors such as fullscreen
- `games/` - category hub pages
- `docs/` - lightweight GitHub Pages landing page for external linking

## Local Preview

Use any static server from the repository root, for example:

```bash
python -m http.server 8000
```

Then open:

```text
http://127.0.0.1:8000/
```

## GitHub Pages Setup

This repository includes a simple backlink landing page in `docs/` so GitHub Pages can be enabled without affecting the main production deployment.

In GitHub:

1. Open `Settings`
2. Open `Pages`
3. Set `Build and deployment` to `Deploy from a branch`
4. Choose branch `main`
5. Choose folder `/docs`
6. Save and wait for GitHub Pages to publish

The published URL should be:

```text
https://daanaagua.github.io/DEAD-STRIKE/
```

## Deployment Notes

- Production domain uses Cloudflare
- `wrangler.jsonc` is included for Workers static assets deployment
- `ads.txt`, `robots.txt`, and `sitemap.xml` are already present in the root

## License

Private project repository unless otherwise specified by the owner.
