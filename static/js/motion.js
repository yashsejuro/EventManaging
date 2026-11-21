document.addEventListener("DOMContentLoaded", () => {
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  if (!gsap || !ScrollTrigger) return;

  const plugins = [ScrollTrigger];
  if (window.SplitText) plugins.push(window.SplitText);
  if (window.Flip) plugins.push(window.Flip);
  gsap.registerPlugin(...plugins);

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const debugMotion = new URLSearchParams(window.location.search).has("debug");
  document.body.classList.toggle("debug-motion", debugMotion);
  const isOrganizer = document.body.className.includes("organizer")
    || document.body.className.includes("page-organizer");
  const publicPage = !isOrganizer
    && ["home", "event_list", "event_detail", "my_registrations"].includes(
      document.body.className.match(/page-([^\s]+)/)?.[1]
    );

  let lenis = null;
  if (!reducedMotion && publicPage && window.Lenis) {
    lenis = new window.Lenis({
      duration: 1.15,
      smoothWheel: true,
      wheelMultiplier: 0.9,
    });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((time) => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  const progress = document.querySelector("[data-scroll-progress]");
  if (progress) {
    gsap.set(progress, { scaleX: 0, transformOrigin: "0 50%" });
    gsap.to(progress, {
      scaleX: 1,
      ease: "none",
      scrollTrigger: { trigger: document.body, start: "top top", end: "bottom bottom", scrub: 0.6 },
    });
  }

  const header = document.querySelector("[data-site-header]");
  if (header && !reducedMotion) {
    let previousY = window.scrollY;
    const updateHeader = () => {
      const currentY = window.scrollY;
      header.classList.toggle("is-scrolled", currentY > 40);
      header.classList.toggle("is-hidden", currentY > previousY && currentY > 160);
      previousY = currentY;
    };
    window.addEventListener("scroll", updateHeader, { passive: true });
    updateHeader();
  } else if (header) {
    header.classList.toggle("is-scrolled", window.scrollY > 40);
  }

  document.querySelectorAll("[data-glass-card]").forEach((card) => {
    card.addEventListener("pointermove", (event) => {
      const rect = card.getBoundingClientRect();
      card.style.setProperty("--mx", `${((event.clientX - rect.left) / rect.width) * 100}%`);
      card.style.setProperty("--my", `${((event.clientY - rect.top) / rect.height) * 100}%`);
    });
  });

  document.querySelectorAll("[data-ambient-blob]").forEach((blob, index) => {
    gsap.to(blob, {
      x: index % 2 ? "8vw" : "-6vw",
      y: index === 1 ? "-8vh" : "10vh",
      duration: 12 + index * 3,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
    });
  });

  gsap.to("[data-ambient-blob]", {
    filter: "blur(110px) hue-rotate(38deg)",
    ease: "none",
    scrollTrigger: { trigger: document.body, start: "top top", end: "bottom bottom", scrub: 1 },
  });

  document.querySelectorAll("[data-magnetic]").forEach((button) => {
    if (reducedMotion) return;
    button.addEventListener("pointermove", (event) => {
      const rect = button.getBoundingClientRect();
      const x = (event.clientX - rect.left - rect.width / 2) * 0.12;
      const y = (event.clientY - rect.top - rect.height / 2) * 0.12;
      gsap.to(button, { x, y, duration: 0.25, ease: "power3.out" });
    });
    button.addEventListener("pointerleave", () => {
      gsap.to(button, { x: 0, y: 0, duration: 0.35, ease: "expo.out" });
    });
  });

  const hero = document.querySelector("[data-hero]");
  if (hero && !reducedMotion) {
    gsap.to(hero.querySelector("[data-hero-intro], [data-split-title]") || hero, {
      y: -90,
      scale: 0.92,
      opacity: 0,
      ease: "none",
      scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: 0.8 },
    });
    gsap.to(hero.querySelector("[data-hero-canvas]"), {
      yPercent: 18,
      ease: "none",
      scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: 1 },
    });
  }

  const statement = document.querySelector("[data-statement-copy]");
  if (statement) {
    if (!reducedMotion) {
      let words = [];
      if (window.SplitText) {
        let splitText = null;
        if (window.SplitText.create) {
          splitText = window.SplitText.create(statement, { type: "words" });
        } else {
          splitText = new window.SplitText(statement, { type: "words" });
        }
        words = splitText.words || [];
      } else {
        const text = statement.textContent;
        statement.textContent = "";
        words = text.trim().split(/\s+/).map((word) => {
          const span = document.createElement("span");
          span.className = "word";
          span.textContent = `${word} `;
          statement.appendChild(span);
          return span;
        });
      }
      if (words.length) {
        gsap.set(words, { opacity: 0.15 });
        gsap.to(words, {
          opacity: 1,
          stagger: 0.08,
          ease: "none",
          scrollTrigger: {
            trigger: statement,
            start: "top 75%",
            end: "bottom 35%",
            scrub: 0.8,
          },
        });
      }
    } else {
      gsap.from(statement, { opacity: 0, y: 20, duration: 0.8, ease: "power3.out" });
    }
  }

  if (!reducedMotion) {
    const mm = gsap.matchMedia();
    mm.add("(min-width: 900px)", () => {
      const pin = document.querySelector("[data-featured-pin]");
      const track = document.querySelector("[data-featured-track]");
      if (pin && track) {
        const distance = () => Math.max(0, track.scrollWidth - track.parentElement.clientWidth);
        if (distance() > 40) {
          gsap.to(track, {
            x: () => -distance(),
            ease: "none",
            scrollTrigger: {
              trigger: pin,
              start: "top top",
              end: () => `+=${distance()}`,
              pin: true,
              scrub: 0.9,
              invalidateOnRefresh: true,
              markers: debugMotion,
            },
          });
          track.querySelectorAll("img").forEach((poster) => {
            gsap.fromTo(poster,
              { yPercent: -8 },
              { yPercent: 8, ease: "none", scrollTrigger: {
                trigger: poster,
                start: "left 100%",
                end: "right 0%",
                scrub: 0.8,
              }});
          });
        }
      }
      return () => mm.revert();
    });
  }

  document.querySelectorAll("[data-reveal]").forEach((item) => {
    gsap.from(item, {
      y: reducedMotion ? 12 : 32,
      opacity: 0,
      duration: 0.8,
      ease: "power3.out",
      scrollTrigger: { trigger: item, start: "top 88%", once: true },
    });
  });

  const tiltCards = gsap.utils.toArray("[data-tilt-card]");
  if (tiltCards.length) {
    if (!reducedMotion) {
      ScrollTrigger.batch(tiltCards, {
        start: "top 88%",
        onEnter: (batch) => gsap.to(batch, {
          clipPath: "inset(0)",
          filter: "blur(0px)",
          y: 0,
          opacity: 1,
          stagger: 0.12,
          duration: 0.9,
          ease: "expo.out",
        }),
        once: true,
      });
    }
    gsap.set(tiltCards, {
      clipPath: reducedMotion ? "inset(0)" : "inset(100% 0 0 0)",
      filter: reducedMotion ? "blur(0px)" : "blur(12px)",
    });
  }

  document.querySelectorAll("[data-poster-parallax]").forEach((poster) => {
    if (reducedMotion) return;
    const image = poster.querySelector("img");
    if (image) {
      gsap.to(image, {
        yPercent: 8,
        ease: "none",
        scrollTrigger: { trigger: poster, start: "top bottom", end: "bottom top", scrub: 0.8 },
      });
    }
  });

  document.querySelectorAll("[data-count]").forEach((item) => {
    const target = Number(item.dataset.count || 0);
    if (reducedMotion) {
      item.textContent = String(target);
      return;
    }
    gsap.fromTo(item, { innerText: 0 }, {
      innerText: target,
      snap: { innerText: 1 },
      duration: 1.2,
      ease: "power3.out",
      scrollTrigger: { trigger: item, start: "top 90%", once: true },
    });
  });

  const howSection = document.querySelector("[data-how-pin]");
  const howSteps = gsap.utils.toArray("[data-how-step]");
  if (howSection && howSteps.length) {
    if (!reducedMotion && window.matchMedia("(min-width: 900px)").matches) {
      gsap.set(howSteps.slice(1), { opacity: 0 });
      gsap.set(howSteps[0], { opacity: 1 });
      gsap.set("[data-how-progress]", { scaleY: 0, transformOrigin: "top top" });
      gsap.timeline({
        scrollTrigger: {
          trigger: howSection,
          start: "top top",
          end: "+=180%",
          pin: true,
          scrub: 0.8,
          markers: debugMotion,
        },
      })
        .to("[data-how-progress]", { scaleY: 1, ease: "none" })
        .to(howSteps[0], { opacity: 0, duration: 0.25 })
        .to(howSteps[1], { opacity: 1, duration: 0.25 })
        .to(howSteps[1], { opacity: 0, duration: 0.25 })
        .to(howSteps[2], { opacity: 1, duration: 0.25 });
      howSteps.forEach((step) => {
        const number = step.querySelector("[data-step-number]");
        if (number) gsap.from(number, {
          scale: 0.7,
          opacity: 0,
          duration: 0.6,
          ease: "expo.out",
          scrollTrigger: { trigger: step, start: "top 75%", once: true },
        });
      });
    } else {
      gsap.set(howSteps, { opacity: 1 });
    }
  }

  const booking = document.querySelector("[data-booking-panel]");
  if (booking) {
    if (!reducedMotion) {
      gsap.set(booking, { position: "sticky", top: 112 });
      gsap.from(booking, {
        y: 24,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
        scrollTrigger: { trigger: booking, start: "top 88%", once: true },
      });
    }
  }

  const seatMeter = document.querySelector(".seat-meter i");
  if (seatMeter) {
    gsap.set(seatMeter, { scaleX: reducedMotion ? 1 : 0, transformOrigin: "0 50%" });
    if (!reducedMotion) {
      gsap.to(seatMeter, {
        scaleX: 1,
        ease: "expo.out",
        duration: 1.1,
        scrollTrigger: { trigger: ".seat-panel", start: "top 88%", once: true },
      });
    }
  }

  const footer = document.querySelector(".site-footer");
  if (footer && !reducedMotion) {
    gsap.to(footer, {
      y: 0,
      opacity: 1,
      ease: "none",
      scrollTrigger: { trigger: footer, start: "top 95%", end: "bottom 70%", scrub: 0.8 },
    });
  }

  const refresh = () => ScrollTrigger.refresh();
  window.addEventListener("load", refresh);
  document.fonts?.ready.then(refresh);
  document.querySelectorAll("img").forEach((image) => {
    if (image.complete) return;
    image.addEventListener("load", refresh, { once: true });
  });
});
