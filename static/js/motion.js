document.addEventListener("DOMContentLoaded", () => {
  if (!window.gsap || !window.ScrollTrigger) return;
  window.gsap.registerPlugin(window.ScrollTrigger);

  window.gsap.utils.toArray("[data-reveal]").forEach((item) => {
    window.gsap.from(item, {
      y: 32,
      opacity: 0,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: { trigger: item, start: "top 88%" },
    });
  });

  window.gsap.utils.toArray("[data-count]").forEach((item) => {
    const target = Number(item.dataset.count || 0);
    window.gsap.to(item, {
      innerText: target,
      duration: 1.2,
      snap: { innerText: 1 },
      scrollTrigger: { trigger: item, start: "top 90%", once: true },
    });
  });

  document.querySelectorAll("[data-magnetic]").forEach((button) => {
    button.addEventListener("pointermove", (event) => {
      const rect = button.getBoundingClientRect();
      const x = (event.clientX - rect.left - rect.width / 2) * 0.12;
      const y = (event.clientY - rect.top - rect.height / 2) * 0.12;
      window.gsap.to(button, { x, y, duration: 0.25 });
    });
    button.addEventListener("pointerleave", () => {
      window.gsap.to(button, { x: 0, y: 0, duration: 0.35 });
    });
  });
});
