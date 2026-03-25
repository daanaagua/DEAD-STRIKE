(() => {
  const DESKTOP_COUNT = 12;
  const TABLET_COUNT = 8;
  const MOBILE_COUNT = 6;
  const MOBILE_MAX = 767;
  const TABLET_MAX = 1179;

  let renderTimer = 0;
  let initialized = false;
  let libraryCache = null;
  let librarySource = null;
  let gamesMapCache = new Map();
  let fullscreenDelegated = false;
  let missingLibraryWarned = false;

  function pageNeedsLibrary() {
    return Boolean(
      window.DEAD_STRIKE_PAGE ||
      document.querySelector("[data-player-strip], [data-home-popular], [data-home-fresh]")
    );
  }

  function noteMissingLibrary() {
    if (!pageNeedsLibrary()) {
      return;
    }

    document.documentElement.dataset.deadStrikeLibraryMissing = "true";

    if (missingLibraryWarned) {
      return;
    }

    missingLibraryWarned = true;
    console.warn("Missing window.DEAD_STRIKE_LIBRARY. Check that /game-library.js loads before /site.js.");
  }

  function getLibrary() {
    const nextLibrary = window.DEAD_STRIKE_LIBRARY || null;

    if (!nextLibrary) {
      noteMissingLibrary();
      return libraryCache;
    }

    if (nextLibrary !== librarySource) {
      librarySource = nextLibrary;
      libraryCache = nextLibrary;
      gamesMapCache = new Map();
      missingLibraryWarned = false;
      delete document.documentElement.dataset.deadStrikeLibraryMissing;

      if (libraryCache && Array.isArray(libraryCache.games)) {
        libraryCache.games.forEach((game) => {
          gamesMapCache.set(game.slug, game);
        });
      }
    }

    return libraryCache;
  }

  function getGamesMap() {
    getLibrary();
    return gamesMapCache;
  }

  function getRenderRules() {
    const library = getLibrary();
    return (library && library.renderRules) || {};
  }

  function getGame(slug) {
    return getGamesMap().get(slug) || null;
  }

  function getCanonicalSlug(game) {
    return game && game.canonicalSlug ? game.canonicalSlug : game ? game.slug : "";
  }

  function getRenderableGame(game) {
    const gamesMap = getGamesMap();
    const canonicalSlug = getCanonicalSlug(game);
    return gamesMap.get(canonicalSlug) || game || null;
  }

  function isGameLive(game) {
    return Boolean(game && game.isLive);
  }

  function getResponsiveCount() {
    const counts = getRenderRules().responsiveCounts || {};
    const desktop = counts.desktop || DESKTOP_COUNT;
    const tablet = counts.tablet || TABLET_COUNT;
    const mobile = counts.mobile || MOBILE_COUNT;
    const width = window.innerWidth || document.documentElement.clientWidth || 0;

    if (width <= MOBILE_MAX) {
      return mobile;
    }

    if (width <= TABLET_MAX) {
      return tablet;
    }

    return desktop;
  }

  function getPool(poolName) {
    const library = getLibrary();

    if (!library || !library.pools) {
      return [];
    }

    const parts = poolName.split(".");
    let value = library.pools;

    parts.forEach((part) => {
      value = value && value[part];
    });

    return Array.isArray(value) ? value : [];
  }

  function dedupeGames(slugs, excludeSlugs, limit) {
    const gamesMap = getGamesMap();
    const exclude = new Set(excludeSlugs || []);
    const seen = new Set();
    const results = [];

    slugs.forEach((slug) => {
      if (results.length >= limit || exclude.has(slug) || seen.has(slug)) {
        return;
      }

      const game = gamesMap.get(slug);
      if (!game || !isGameLive(game)) {
        return;
      }

      const renderableGame = getRenderableGame(game);
      if (!renderableGame || !isGameLive(renderableGame)) {
        return;
      }

      const canonicalSlug = getCanonicalSlug(renderableGame);
      if (!canonicalSlug || exclude.has(canonicalSlug) || seen.has(canonicalSlug)) {
        return;
      }

      seen.add(canonicalSlug);
      results.push(renderableGame);
    });

    return results;
  }

  function getFallbackOrder(game) {
    const categories = new Set((game && game.categories) || []);
    const rules = getRenderRules();
    const order = [];
    const categoryFallbackPriority = Array.isArray(rules.categoryFallbackPriority)
      ? rules.categoryFallbackPriority
      : [];
    const terminalFallbackPools = Array.isArray(rules.terminalFallbackPools)
      ? rules.terminalFallbackPools
      : [];

    categoryFallbackPriority.forEach((rule) => {
      if (rule && categories.has(rule.category) && rule.pool) {
        order.push(rule.pool);
      }
    });

    terminalFallbackPools.forEach((poolName) => {
      order.push(poolName);
    });

    return order;
  }

  function getPoolFillOrder(poolName) {
    const rules = getRenderRules();
    const homePoolFillOrder = rules.homePoolFillOrder || {};
    return Array.isArray(homePoolFillOrder[poolName]) ? homePoolFillOrder[poolName] : [];
  }

  function getRelatedGames(slug, limit) {
    const currentGame = getGame(slug);

    if (!currentGame) {
      return [];
    }

    const requestedLimit = limit || DESKTOP_COUNT;
    const combined = [];
    const related = Array.isArray(currentGame.related) ? currentGame.related : [];
    const currentCanonicalSlug = getCanonicalSlug(getRenderableGame(currentGame));

    combined.push(...related);
    getFallbackOrder(currentGame).forEach((poolName) => {
      combined.push(...getPool(poolName));
    });

    return dedupeGames(combined, [currentCanonicalSlug], requestedLimit);
  }

  function getCurrentPageSlug() {
    return window.DEAD_STRIKE_PAGE && window.DEAD_STRIKE_PAGE.slug ? window.DEAD_STRIKE_PAGE.slug : "";
  }

  function getPoolGames(poolName, limit, excludeSlugs) {
    const requestedLimit = limit || DESKTOP_COUNT;
    const combined = [...getPool(poolName)];

    getPoolFillOrder(poolName).forEach((fallbackPoolName) => {
      combined.push(...getPool(fallbackPoolName));
    });

    return dedupeGames(combined, excludeSlugs || [], requestedLimit);
  }

  function createImage(game) {
    const image = document.createElement("img");
    image.src = game.thumb;
    image.alt = game.title;
    image.loading = "lazy";
    image.decoding = "async";
    return image;
  }

  function createStripCard(game) {
    const link = document.createElement("a");
    const label = document.createElement("span");

    link.className = "player-strip-card";
    link.href = game.href;
    link.setAttribute("aria-label", game.title);
    link.appendChild(createImage(game));

    label.className = "player-strip-title";
    label.textContent = game.title;
    link.appendChild(label);
    return link;
  }

  function createIconWallCard(game) {
    const link = document.createElement("a");
    const label = document.createElement("span");

    link.className = "sidebar-icon-card";
    link.href = game.href;
    link.setAttribute("aria-label", game.title);
    link.appendChild(createImage(game));

    label.className = "sr-only";
    label.textContent = game.title;
    link.appendChild(label);
    return link;
  }

  function renderStrip(element, games) {
    const grid = document.createElement("div");

    element.innerHTML = "";
    element.classList.add("player-strip");

    grid.className = "player-strip-grid";
    games.forEach((game) => {
      grid.appendChild(createStripCard(game));
    });

    element.appendChild(grid);
  }

  function renderIconWall(element, games) {
    const grid = document.createElement("div");

    element.innerHTML = "";
    element.classList.add("sidebar-icon-wall");

    grid.className = "sidebar-icon-grid";
    games.forEach((game) => {
      grid.appendChild(createIconWallCard(game));
    });

    element.appendChild(grid);
  }

  function resolveStripGames(element) {
    const limit = getResponsiveCount();
    const explicitPool = element.getAttribute("data-player-strip");
    const currentSlug = getCurrentPageSlug();

    if (explicitPool && explicitPool !== "auto") {
      return getPoolGames(explicitPool, limit, currentSlug ? [currentSlug] : []);
    }

    if (currentSlug) {
      return getRelatedGames(currentSlug, limit);
    }

    return getPoolGames("playerStrip", limit);
  }

  function renderLibraryHooks() {
    if (!getLibrary()) {
      document.documentElement.dataset.deadStrikeLibraryStatus = "missing";
      return;
    }

    document.documentElement.dataset.deadStrikeLibraryStatus = "ready";

    const limit = getResponsiveCount();

    document.querySelectorAll("[data-player-strip]").forEach((element) => {
      renderStrip(element, resolveStripGames(element));
    });

    document.querySelectorAll("[data-home-popular]").forEach((element) => {
      const currentSlug = getCurrentPageSlug();
      renderIconWall(element, getPoolGames("popular", limit, currentSlug ? [currentSlug] : []));
    });

    document.querySelectorAll("[data-home-fresh]").forEach((element) => {
      const currentSlug = getCurrentPageSlug();
      renderIconWall(element, getPoolGames("fresh", limit, currentSlug ? [currentSlug] : []));
    });
  }

  async function toggleFullscreen(button) {
    const selector = button.getAttribute("data-fullscreen-target");
    const target = selector ? document.querySelector(selector) : null;

    if (!target) {
      return;
    }

    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await target.requestFullscreen();
      }
    } catch (error) {
      console.error("Fullscreen request failed", error);
    }
  }

  function bindFullscreenButtons() {
    if (fullscreenDelegated) {
      return;
    }

    fullscreenDelegated = true;
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-fullscreen-target]");
      if (!button) {
        return;
      }

      event.preventDefault();
      toggleFullscreen(button);
    });
  }

  function scheduleLibraryRender() {
    if (!pageNeedsLibrary() || !getLibrary()) {
      return;
    }

    window.clearTimeout(renderTimer);
    renderTimer = window.setTimeout(renderLibraryHooks, 80);
  }

  function init() {
    if (initialized) {
      return;
    }

    initialized = true;
    bindFullscreenButtons();
    if (pageNeedsLibrary()) {
      renderLibraryHooks();
      window.addEventListener("resize", scheduleLibraryRender);
    }
  }

  window.DEAD_STRIKE_SITE = {
    getGame,
    getRelatedGames,
    getPoolGames,
    renderStrip,
    renderIconWall,
    renderLibraryHooks
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
