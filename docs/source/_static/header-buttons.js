// Light/dark toggle, full-screen toggle and the "On this page" button.
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

  // "On this page": on wide screens the panel stays hidden until this button opens it.
  const toc = document.getElementById("pst-secondary-sidebar");
  if (!toc || !toc.querySelector(".page-toc li")) return;
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "toc-toggle";
  btn.setAttribute("aria-expanded", "false");
  btn.setAttribute("aria-controls", "pst-secondary-sidebar");
  btn.innerHTML =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/></svg>On this page';
  document.body.appendChild(btn);
  html.classList.add("has-toc-toggle");

  const setOpen = (open) => {
    html.classList.toggle("toc-open", open);
    btn.setAttribute("aria-expanded", String(open));
  };
  btn.addEventListener("click", (e) => { e.stopPropagation(); setOpen(!html.classList.contains("toc-open")); });
  toc.addEventListener("click", (e) => { if (e.target.closest("a")) setOpen(false); });
  document.addEventListener("click", (e) => {
    if (html.classList.contains("toc-open") && !toc.contains(e.target)) setOpen(false);
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
});
