/**
 * ClubEvents UI Controller
 * Floating navbar scroll behavior, sliding active indicator,
 * accessible dropdowns, mobile navigation drawer, and interactive components.
 */

document.addEventListener("DOMContentLoaded", () => {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // =========================================================================
  // 1. Navbar Scroll Behavior (Single passive listener with requestAnimationFrame)
  // =========================================================================
  const header = document.querySelector("[data-site-header]");
  if (header) {
    let lastScrollY = window.pageYOffset || document.documentElement.scrollTop;
    let ticking = false;

    const updateNavbar = () => {
      const currentScrollY = Math.max(0, window.pageYOffset || document.documentElement.scrollTop);
      const deltaY = currentScrollY - lastScrollY;

      // 1. Condense styling after ~40px scroll
      header.classList.toggle("is-scrolled", currentScrollY > 40);

      // 2. Hide on scroll down, show on scroll up (only when > 120px)
      // Never hide if mobile drawer or user dropdown is currently open
      const isMobileOpen = document.body.classList.contains("nav-open");
      const isDropdownOpen = document.querySelector("[data-user-dropdown]:not([hidden])");

      if (!reducedMotion && !isMobileOpen && !isDropdownOpen) {
        if (currentScrollY > 120 && deltaY > 6) {
          header.classList.add("is-hidden");
        } else if (deltaY < -6 || currentScrollY <= 40) {
          header.classList.remove("is-hidden");
        }
      }

      lastScrollY = currentScrollY;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(updateNavbar);
        ticking = true;
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    updateNavbar();
  }

  // =========================================================================
  // 2. Sliding Active Pill Indicator
  // =========================================================================
  const navLinksContainer = document.querySelector("[data-nav-links]");
  const indicator = document.querySelector("[data-nav-indicator]");

  if (navLinksContainer && indicator) {
    const activeLink = navLinksContainer.querySelector(".nav-link.is-active");
    const links = navLinksContainer.querySelectorAll(".nav-link");

    const moveIndicator = (target) => {
      if (!target) {
        indicator.style.opacity = "0";
        return;
      }
      const containerRect = navLinksContainer.getBoundingClientRect();
      const targetRect = target.getBoundingClientRect();
      const left = targetRect.left - containerRect.left;
      const width = targetRect.width;

      indicator.style.width = `${width}px`;
      indicator.style.transform = `translateX(${left}px)`;
      indicator.style.opacity = "1";
    };

    // Position on active link on load
    if (activeLink) {
      window.requestAnimationFrame(() => moveIndicator(activeLink));
      window.addEventListener("resize", () => moveIndicator(activeLink), { passive: true });
    }

    links.forEach((link) => {
      link.addEventListener("mouseenter", () => moveIndicator(link));
      link.addEventListener("focus", () => moveIndicator(link));
    });

    navLinksContainer.addEventListener("mouseleave", () => {
      if (activeLink) {
        moveIndicator(activeLink);
      } else {
        indicator.style.opacity = "0";
      }
    });
  }

  // =========================================================================
  // 3. Logged-in User Menu Dropdown (Accessible keyboard & outside-click)
  // =========================================================================
  const userMenuTrigger = document.querySelector("[data-user-menu-trigger]");
  const userDropdown = document.querySelector("[data-user-dropdown]");

  if (userMenuTrigger && userDropdown) {
    const toggleUserMenu = (open) => {
      const willOpen = open !== undefined ? open : userDropdown.hasAttribute("hidden");
      userMenuTrigger.setAttribute("aria-expanded", String(willOpen));
      if (willOpen) {
        userDropdown.removeAttribute("hidden");
        window.requestAnimationFrame(() => userDropdown.classList.add("is-open"));
      } else {
        userDropdown.classList.remove("is-open");
        userDropdown.setAttribute("hidden", "");
      }
    };

    userMenuTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleUserMenu();
    });

    // Close on click outside
    document.addEventListener("click", (e) => {
      if (!userDropdown.hasAttribute("hidden") && !userDropdown.contains(e.target) && !userMenuTrigger.contains(e.target)) {
        toggleUserMenu(false);
      }
    });

    // Close on Escape and return focus to trigger
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !userDropdown.hasAttribute("hidden")) {
        toggleUserMenu(false);
        userMenuTrigger.focus();
      }
    });
  }

  // =========================================================================
  // 4. Mobile Navigation Drawer (<768px Morphing Toggle & Glass Panel)
  // =========================================================================
  const navToggle = document.querySelector("[data-nav-toggle]");
  const mobileNav = document.querySelector("[data-mobile-nav]");
  const mobileBackdrop = document.querySelector("[data-mobile-backdrop]");

  if (navToggle && mobileNav) {
    const toggleMobileNav = (open) => {
      const willOpen = open !== undefined ? open : !mobileNav.classList.contains("is-open");
      navToggle.classList.toggle("is-open", willOpen);
      navToggle.setAttribute("aria-expanded", String(willOpen));
      mobileNav.classList.toggle("is-open", willOpen);
      mobileNav.setAttribute("aria-hidden", String(!willOpen));
      document.body.classList.toggle("nav-open", willOpen);

      if (willOpen) {
        const firstLink = mobileNav.querySelector("a, button");
        if (firstLink) firstLink.focus();
      }
    };

    navToggle.addEventListener("click", () => toggleMobileNav());

    if (mobileBackdrop) {
      mobileBackdrop.addEventListener("click", () => toggleMobileNav(false));
    }

    // Close on link click inside mobile panel
    mobileNav.querySelectorAll("a, button[type='submit']").forEach((item) => {
      item.addEventListener("click", () => toggleMobileNav(false));
    });

    // Close on Escape key and return focus to toggle button
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && mobileNav.classList.contains("is-open")) {
        toggleMobileNav(false);
        navToggle.focus();
      }
    });
  }

  // =========================================================================
  // 5. Existing App Interactive Features (Toasts, View Switchers, Seats Bar)
  // =========================================================================
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
