const games = [
  {
    id: "modern-fps-strike",
    title: "Modern FPS Strike: Zombie Gun War Ops",
    shortTitle: "Modern FPS Strike",
    iframe: "https://html5.gamemonetize.co/tq813m1zcpoha7zigujhmy9f08idwlab/",
    poster: "https://img.gamemonetize.com/tq813m1zcpoha7zigujhmy9f08idwlab/512x384.jpg",
    category: "Action / Shooting",
    mobile: "Yes",
    publisher: "Artis Web",
    canvas: "1920 x 1080",
    published: "2025",
    provider: "GameMonetize embed",
    summary:
      "Fast browser FPS pressure with zombie targets, modern weapons, and quick session replay value.",
    description:
      "Fight the zombies with FPS Strike Modern Arena, sharpen your shooting skills, complete tactical missions, and defeat enemies in modern browser warfare.",
    controls: "Mouse click or tap to play.",
    tags: ["FPS", "Zombie", "Mobile ready"]
  },
  {
    id: "fps-shooting-survival-sim",
    title: "FPS Shooting Survival Sim",
    shortTitle: "FPS Survival Sim",
    iframe: "https://html5.gamemonetize.co/5rxwjnl6kc368x7uqdc6kzwx0do1731k/",
    poster: "https://img.gamemonetize.com/5rxwjnl6kc368x7uqdc6kzwx0do1731k/512x384.jpg",
    category: "Shooting / Zombie",
    mobile: "No",
    publisher: "AlexGM",
    canvas: "800 x 600",
    published: "2022",
    provider: "GameMonetize embed",
    summary:
      "Desktop-first zombie cleanup with classic WASD controls and heavier survival pressure.",
    description:
      "A zombie virus has taken over. You are the special forces commando, and every run is about staying alive long enough to clear the next wave.",
    controls: "WASD walk, Space jump, Mouse aim and shoot, Shift plus W run.",
    tags: ["Desktop", "WASD", "Zombie"]
  },
  {
    id: "zombie-survival-last-stand",
    title: "Zombie Survival : Last Stand",
    shortTitle: "Zombie Last Stand",
    iframe: "https://html5.gamemonetize.co/o6w1t7bn7a9nw6jv4sny1sag7jsutbfu/",
    poster: "https://img.gamemonetize.com/o6w1t7bn7a9nw6jv4sny1sag7jsutbfu/512x384.jpg",
    category: "Action / Shooting",
    mobile: "No",
    publisher: "Riteshdxy",
    canvas: "800 x 600",
    published: "2026",
    provider: "GameMonetize embed",
    summary:
      "A tighter horror-leaning zombie loop with scope, reload, and survival pacing.",
    description:
      "Survive a zombie-infested city in a fast-paced first-person shooter where ammo control, movement, and headshots matter more every minute.",
    controls:
      "WASD move, left click shoot, right click scope, R reload, middle mouse switch weapon.",
    tags: ["Survival", "Horror", "FPS"]
  },
  {
    id: "sniper-master",
    title: "Sniper Master",
    shortTitle: "Sniper Master",
    iframe: "https://html5.gamemonetize.co/0gus8yum52pw2fq3mjc3dp1idx4p1pm3/",
    poster: "https://img.gamemonetize.com/0gus8yum52pw2fq3mjc3dp1idx4p1pm3/512x384.jpg",
    category: "3D / Action",
    mobile: "Yes",
    publisher: "Raccoon",
    canvas: "750 x 1334",
    published: "2026",
    provider: "GameMonetize embed",
    summary:
      "Cleaner sniper timing gameplay for mobile and fast casual sessions.",
    description:
      "Jump, float, and fire in mid-air while lining up the cleanest possible shot. This one broadens the DEAD STRIKE mix beyond zombie pressure.",
    controls: "Mouse click or tap to play.",
    tags: ["Sniper", "Mobile ready", "Casual"]
  }
];

const state = {
  activeIndex: 0,
  launched: false
};

const refs = {
  panelStatus: document.getElementById("panelStatus"),
  heroGameTitle: document.getElementById("heroGameTitle"),
  heroGameSummary: document.getElementById("heroGameSummary"),
  heroCategory: document.getElementById("heroCategory"),
  heroMobile: document.getElementById("heroMobile"),
  heroPublisher: document.getElementById("heroPublisher"),
  heroCanvas: document.getElementById("heroCanvas"),
  featuredTitle: document.getElementById("featuredTitle"),
  featuredDescription: document.getElementById("featuredDescription"),
  featuredControls: document.getElementById("featuredControls"),
  featuredProvider: document.getElementById("featuredProvider"),
  featuredPublished: document.getElementById("featuredPublished"),
  posterTitle: document.getElementById("posterTitle"),
  posterDescription: document.getElementById("posterDescription"),
  playerPoster: document.getElementById("playerPoster"),
  gameFrame: document.getElementById("gameFrame"),
  launchButton: document.getElementById("launchButton"),
  openSourceButton: document.getElementById("openSourceButton"),
  fullscreenButton: document.getElementById("fullscreenButton"),
  gameCards: document.getElementById("gameCards")
};

function renderCards() {
  refs.gameCards.innerHTML = games
    .map(
      (game, index) => `
        <article class="game-card${index === state.activeIndex ? " is-active" : ""}" data-index="${index}">
          <div class="game-card-media" style="background-image:url('${game.poster}')"></div>
          <div class="tag-row">
            ${game.tags.map((tag) => `<span>${tag}</span>`).join("")}
          </div>
          <div>
            <h3>${game.title}</h3>
            <p>${game.summary}</p>
          </div>
        </article>
      `
    )
    .join("");

  refs.gameCards.querySelectorAll(".game-card").forEach((card) => {
    card.addEventListener("click", () => {
      const nextIndex = Number(card.dataset.index);
      setActiveGame(nextIndex, state.launched);
    });
  });
}

function setPoster(game) {
  refs.playerPoster.style.backgroundImage = `url('${game.poster}')`;
  refs.posterTitle.textContent = game.title;
  refs.posterDescription.textContent = game.description;
}

function setActiveGame(index, loadFrame) {
  const game = games[index];
  state.activeIndex = index;

  refs.panelStatus.textContent = `Featured mission active - ${game.shortTitle}`;
  refs.heroGameTitle.textContent = game.title;
  refs.heroGameSummary.textContent = game.summary;
  refs.heroCategory.textContent = game.category;
  refs.heroMobile.textContent = game.mobile;
  refs.heroPublisher.textContent = game.publisher;
  refs.heroCanvas.textContent = game.canvas;

  refs.featuredTitle.textContent = game.title;
  refs.featuredDescription.textContent = game.description;
  refs.featuredControls.textContent = game.controls;
  refs.featuredProvider.textContent = game.provider;
  refs.featuredPublished.textContent = game.published;
  refs.openSourceButton.href = game.iframe;

  setPoster(game);

  if (loadFrame) {
    refs.gameFrame.src = game.iframe;
    refs.playerPoster.hidden = true;
    state.launched = true;
  } else {
    refs.gameFrame.removeAttribute("src");
    refs.playerPoster.hidden = false;
  }

  renderCards();
}

function launchCurrentGame() {
  const game = games[state.activeIndex];
  refs.gameFrame.src = game.iframe;
  refs.playerPoster.hidden = true;
  state.launched = true;
}

async function openFullscreen() {
  const wrap = document.getElementById("playerFrameWrap");
  if (!document.fullscreenElement) {
    await wrap.requestFullscreen();
  } else {
    await document.exitFullscreen();
  }
}

refs.launchButton.addEventListener("click", launchCurrentGame);
refs.fullscreenButton.addEventListener("click", openFullscreen);

setActiveGame(0, false);
