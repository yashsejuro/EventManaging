document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.querySelector("[data-nav-toggle]");
  const navMenu = document.querySelector("[data-nav-menu]");
  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      const open = navMenu.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
  }

  document.querySelectorAll("[data-toast]").forEach((toast) => {
    const close = () => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px)";
      window.setTimeout(() => toast.remove(), 180);
    };
    toast.querySelector("[data-toast-close]")?.addEventListener("click", close);
    window.setTimeout(close, 5000);
  });

  const grid = document.querySelector("[data-event-grid]");
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-view]").forEach((item) => {
        item.classList.toggle("is-active", item === button);
        item.setAttribute("aria-pressed", String(item === button));
      });
      grid?.classList.toggle("is-list", button.dataset.view === "list");
    });
  });

  document.querySelectorAll("[data-seats-bar]").forEach((panel) => {
    const capacity = Number(panel.dataset.capacity || 0);
    const left = Number(panel.dataset.seatsLeft || 0);
    const meter = panel.querySelector(".seat-meter i");
    if (meter) meter.style.width = `${capacity ? (left / capacity) * 100 : 0}%`;
  });
});
