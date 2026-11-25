import * as THREE from "three";

const canvas = document.querySelector("[data-hero-canvas]");
if (canvas) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0, 7);

  const renderer = new THREE.WebGLRenderer({
    canvas,
    alpha: true,
    antialias: true,
    powerPreference: "high-performance",
  });

  const geometry = new THREE.TorusKnotGeometry(1.35, 0.38, 110, 16);
  const material = new THREE.MeshStandardMaterial({
    color: 0xd6ff3f,
    roughness: 0.3,
    metalness: 0.15,
  });
  const knot = new THREE.Mesh(geometry, material);
  scene.add(knot);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x8067ff, 2.4));
  const light = new THREE.DirectionalLight(0xffffff, 3);
  light.position.set(-3, 4, 5);
  scene.add(light);

  const resize = () => {
    const parent = canvas.parentElement;
    const width = Math.max(1, parent.clientWidth);
    const height = Math.max(1, parent.clientHeight);
    const aspect = width / height;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, width < 768 ? 1.25 : 1.5));
    renderer.setSize(width, height, false);
    camera.aspect = aspect;

    if (aspect < 0.9) {
      // Portrait mobile: pull camera back and tuck smaller knot cleanly in lower-right
      camera.position.set(0, 0, 8.6);
      knot.scale.setScalar(0.62);
      knot.position.set(0.68, -1.05, 0);
    } else if (aspect < 1.35) {
      camera.position.set(0, 0, 7.6);
      knot.scale.setScalar(0.84);
      knot.position.set(1.55, 0, 0);
    } else {
      camera.position.set(0, 0, 7);
      knot.scale.setScalar(1);
      knot.position.set(2.4, 0, 0);
    }
    camera.updateProjectionMatrix();
  };
  resize();
  window.addEventListener("resize", resize, { passive: true });

  let isVisible = true;
  let rafId = null;

  const animate = () => {
    rafId = null;
    if (!isVisible || document.hidden) return;
    knot.rotation.x += 0.002;
    knot.rotation.y += 0.004;
    renderer.render(scene, camera);
    rafId = requestAnimationFrame(animate);
  };

  const startLoop = () => {
    if (rafId === null && isVisible && !document.hidden) {
      rafId = requestAnimationFrame(animate);
    }
  };

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        isVisible = entries[0]?.isIntersecting ?? true;
        if (isVisible) startLoop();
      },
      { threshold: 0.05 }
    );
    observer.observe(canvas);
  }

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) startLoop();
  });

  startLoop();
}
