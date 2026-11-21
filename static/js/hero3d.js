import * as THREE from "three";

const canvas = document.querySelector("[data-hero-canvas]");
if (canvas) {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0, 7);

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const geometry = new THREE.TorusKnotGeometry(1.35, 0.38, 180, 24);
  const material = new THREE.MeshStandardMaterial({
    color: 0xd6ff3f,
    roughness: 0.3,
    metalness: 0.15,
  });
  const knot = new THREE.Mesh(geometry, material);
  knot.position.set(2.4, 0, 0);
  scene.add(knot);

  scene.add(new THREE.HemisphereLight(0xffffff, 0x8067ff, 2.4));
  const light = new THREE.DirectionalLight(0xffffff, 3);
  light.position.set(-3, 4, 5);
  scene.add(light);

  const resize = () => {
    const parent = canvas.parentElement;
    const width = parent.clientWidth;
    const height = parent.clientHeight;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  resize();
  window.addEventListener("resize", resize);

  const animate = () => {
    knot.rotation.x += 0.002;
    knot.rotation.y += 0.004;
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  };
  animate();
}
