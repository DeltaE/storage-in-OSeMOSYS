// Light/dark toggle and full-screen toggle for the header buttons.
// The theme restores the colour mode from the "mode" and "theme" localStorage keys on each page.
document.addEventListener("DOMContentLoaded", () => {
  const html = document.documentElement;

  document.querySelectorAll(".mode-btn").forEach((btn) =>
    btn.addEventListener("click", () => {
      const next = html.dataset.theme === "dark" ? "light" : "dark";
      html.dataset.theme = next;
      html.dataset.mode = next;
      try {
        localStorage.setItem("mode", next);
        localStorage.setItem("theme", next);
      } catch (e) {}
    })
  );

  document.querySelectorAll(".fullscreen-btn").forEach((btn) => {
    if (!document.fullscreenEnabled) { btn.style.display = "none"; return; }
    btn.addEventListener("click", () => {
      if (document.fullscreenElement) document.exitFullscreen();
      else html.requestFullscreen();
    });
  });
  document.addEventListener("fullscreenchange", () =>
    html.classList.toggle("is-fullscreen", !!document.fullscreenElement)
  );
});
