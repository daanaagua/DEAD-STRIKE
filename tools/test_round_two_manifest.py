#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_round_two_manifest import extract_embed_fields


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

    print("ROUND_TWO_MANIFEST_PARSER_VERIFIED")


if __name__ == "__main__":
    main()
