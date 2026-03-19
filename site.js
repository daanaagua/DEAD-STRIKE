document.querySelectorAll("[data-fullscreen-target]").forEach((button) => {
  button.addEventListener("click", async () => {
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
  });
});
