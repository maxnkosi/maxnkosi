import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { createLogoGlass } from './glassMaterial.js';

const PRESETS = { front: [0, 0], oblique: [38, 14] };

/**
 * Mount the static Currency Stream glass logo into a DOM element.
 * @param {HTMLElement} el  container; the canvas fills it (give it a size)
 * @param {object} [o]
 * @param {string} [o.modelUrl]  URL of currency-stream-logo.glb
 * @param {'front'|'oblique'} [o.view]  start pose (or pass yaw/pitch in degrees)
 * @param {boolean} [o.controls=true]  allow drag-to-orbit / wheel-to-zoom
 * @param {string|null} [o.background='#ffffff']  CSS colour, or null for transparent
 * @returns {{dispose():void, ready:Promise<void>}}
 */
export function mountCurrencyStreamLogo(el, o = {}) {
  const {
    modelUrl = `${import.meta.env.BASE_URL}models/currency-stream-logo.glb`,
    view = 'front', controls: enableControls = true, background = '#ffffff',
  } = o;
  const [yaw, pitch] = o.yaw !== undefined ? [o.yaw, o.pitch ?? 0] : PRESETS[view] ?? PRESETS.front;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: background === null, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.NoToneMapping; // keep supplied artwork colours exact
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none';
  el.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  if (background !== null) scene.background = new THREE.Color(background);

  // Static lighting: fixed studio environment + two fixed lights.
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-4, 6, 8); scene.add(key);
  const rim = new THREE.DirectionalLight(0xcfeeff, 0.8); rim.position.set(6, -3, 5); scene.add(rim);

  const camera = new THREE.PerspectiveCamera(18, 1, 0.1, 500);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enabled = enableControls;
  controls.enableDamping = true; controls.dampingFactor = 0.08; controls.rotateSpeed = 0.8;
  controls.enablePan = false;

  const resize = () => {
    const w = el.clientWidth || 1, h = el.clientHeight || 1;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  const ro = new ResizeObserver(resize); ro.observe(el); resize();

  let visible = true;
  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; }); io.observe(el);

  const ready = new Promise((resolve, reject) => {
    new GLTFLoader().load(modelUrl, (gltf) => {
      const logo = gltf.scene.getObjectByName('Currency Stream Logo') ?? gltf.scene;
      const glass = createLogoGlass(gltf.scene.getObjectByProperty('isMesh', true).material);
      logo.traverse((m) => { if (m.isMesh) m.material = glass; });

      const box = new THREE.Box3().setFromObject(logo);
      const size = box.getSize(new THREE.Vector3());
      logo.position.sub(box.getCenter(new THREE.Vector3()));
      scene.add(logo);

      const radius = Math.max(size.x, size.y) * 0.5 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.12;
      const y = THREE.MathUtils.degToRad(yaw), p = THREE.MathUtils.degToRad(pitch);
      camera.position.set(Math.sin(y) * Math.cos(p), Math.sin(p), Math.cos(y) * Math.cos(p)).multiplyScalar(radius);
      controls.minDistance = radius * 0.4; controls.maxDistance = radius * 3;
      controls.target.set(0, 0, 0); controls.update();

      renderer.setAnimationLoop(() => { if (visible) { controls.update(); renderer.render(scene, camera); } });
      el.dataset.ready = 'true';
      resolve();
    }, undefined, reject);
  });

  return {
    ready,
    dispose() {
      renderer.setAnimationLoop(null); ro.disconnect(); io.disconnect(); controls.dispose();
      renderer.dispose(); renderer.domElement.remove();
    },
  };
}
