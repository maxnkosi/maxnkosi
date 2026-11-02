import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/examples/jsm/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { defaultSettings, applySettings, buildPanel, mergeSettings } from './settings.js';
import { createLogoGlass, createClearGlass, createStudioBackdrop } from './glassMaterial.js';

const PRESETS = { front: [0, 0], oblique: [38, 14] };

/**
 * Mount the static Currency Stream glass logo into a DOM element.
 * @param {HTMLElement} el  container; the canvas fills it (give it a size)
 * @param {object} [o]
 * @param {string} [o.modelUrl]  URL of currency-stream-logo.glb
 * @param {'branded'|'clear'} [o.material='branded']  'clear' = 100% clear glass, no tint or artwork
 * @param {boolean} [o.panel=false]  show the live settings panel (refraction, reflections, occlusion)
 * @param {object} [o.settings]  partial overrides of the defaults in settings.js
 * @param {ArrayBuffer} [o.modelData]  GLB bytes already in memory (skips the network fetch)
 * @param {'front'|'oblique'} [o.view]  start pose (or pass yaw/pitch in degrees)
 * @param {boolean} [o.controls=true]  allow drag-to-orbit / wheel-to-zoom
 * @param {string|null} [o.background='#ffffff']  CSS colour, or null for transparent
 * @returns {{dispose():void, ready:Promise<void>}}
 */
export function mountCurrencyStreamLogo(el, o = {}) {
  const {
    modelUrl = `${import.meta.env.BASE_URL}models/currency-stream-logo.glb`,
    view = 'front', material = 'branded', panel = false, settings: initial = null, modelData = null, controls: enableControls = true, background = '#ffffff',
  } = o;
  const [yaw, pitch] = o.yaw !== undefined ? [o.yaw, o.pitch ?? 0] : PRESETS[view] ?? PRESETS.front;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: background === null, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.NoToneMapping; // keep supplied artwork colours exact
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none';
  el.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  if (material === 'clear' && background === '#ffffff') scene.add(createStudioBackdrop());
  else if (background !== null) scene.background = new THREE.Color(background);

  // Static lighting: fixed studio environment + two fixed lights.
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-4, 6, 8); scene.add(key);
  const rim = new THREE.DirectionalLight(0xcfeeff, 0.8); rim.position.set(6, -3, 5); scene.add(rim);

  const camera = new THREE.PerspectiveCamera(18, 1, 0.1, 500);

  const defaults = () => defaultSettings(material);
  const settings = defaults();
  for (const k of Object.keys(initial ?? {})) Object.assign(settings[k] ?? (settings[k] = {}), initial[k]);
  // Per-browser persistence (separate for each material). Explicit options win over saved values only on first run.
  const STORE = `currency-stream-logo:${material}`;
  const save = () => { try { localStorage.setItem(STORE, JSON.stringify(settings)); } catch { /* storage unavailable */ } };
  try { mergeSettings(settings, JSON.parse(localStorage.getItem(STORE))); } catch { /* none saved */ }
  let glassMat = null, composer = null, aoPass = null, gui = null;

  const sync = () => {
    if (!glassMat) return;
    if (settings.occlusion.enabled && !composer) {
      const size = renderer.getSize(new THREE.Vector2());
      const rt = new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType, samples: 4 });
      composer = new EffectComposer(renderer, rt);
      composer.setPixelRatio(renderer.getPixelRatio());
      composer.addPass(new RenderPass(scene, camera));
      aoPass = new GTAOPass(scene, camera, size.x, size.y);
      composer.addPass(aoPass);
      composer.addPass(new OutputPass());
      composer.setSize(size.x, size.y);
    }
    applySettings(settings, { mat: glassMat, scene, key, rim, ao: aoPass, kind: material });
    save();
  };
  const reset = () => {
    const d = defaults();
    for (const k of Object.keys(d)) Object.assign(settings[k], d[k]);
    try { localStorage.removeItem(STORE); } catch { /* ignore */ }
    gui?.controllersRecursive().forEach((c) => c.updateDisplay()); sync();
  };
  const settingsIO = {
    get: () => JSON.stringify(settings, null, 1),
    set: (txt) => { try { const ok = mergeSettings(settings, JSON.parse(txt)); sync(); return ok; } catch { return false; } },
  };
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enabled = enableControls;
  controls.enableDamping = true; controls.dampingFactor = 0.08; controls.rotateSpeed = 0.8;
  controls.enablePan = false;

  const resize = () => {
    const w = el.clientWidth || 1, h = el.clientHeight || 1;
    renderer.setSize(w, h, false); composer?.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  const ro = new ResizeObserver(resize); ro.observe(el); resize();

  let visible = true;
  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; }); io.observe(el);

  let radius = 1;
  const setView = (v) => {
    const [yw, pt] = PRESETS[v] ?? PRESETS.front;
    const y = THREE.MathUtils.degToRad(yw), p = THREE.MathUtils.degToRad(pt);
    camera.position.set(Math.sin(y) * Math.cos(p), Math.sin(p), Math.cos(y) * Math.cos(p)).multiplyScalar(radius);
    controls.target.set(0, 0, 0); controls.update();
  };

  const ready = new Promise((resolve, reject) => {
    const onLoad = (gltf) => {
      const logo = gltf.scene.getObjectByName('Currency Stream Logo') ?? gltf.scene;
      const glass = material === 'clear' ? createClearGlass()
        : createLogoGlass(gltf.scene.getObjectByProperty('isMesh', true).material);
      logo.traverse((m) => { if (m.isMesh) m.material = glass; });
      glassMat = glass;

      const box = new THREE.Box3().setFromObject(logo);
      const size = box.getSize(new THREE.Vector3());
      logo.position.sub(box.getCenter(new THREE.Vector3()));
      scene.add(logo);

      radius = Math.max(size.x, size.y) * 0.5 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.12;
      const y = THREE.MathUtils.degToRad(yaw), p = THREE.MathUtils.degToRad(pitch);
      camera.position.set(Math.sin(y) * Math.cos(p), Math.sin(p), Math.cos(y) * Math.cos(p)).multiplyScalar(radius);
      controls.minDistance = radius * 0.4; controls.maxDistance = radius * 3;
      controls.target.set(0, 0, 0); controls.update();

      el.style.position ||= 'relative';
      if (panel) gui = buildPanel(el, settings, material, sync, reset, settingsIO);
      sync();
      renderer.setAnimationLoop(() => {
        if (!visible) return;
        controls.update();
        if (settings.occlusion.enabled && composer) composer.render(); else renderer.render(scene, camera);
      });
      el.dataset.ready = 'true';
      resolve();
    };
    const loader = new GLTFLoader();
    if (modelData) loader.parse(modelData, '', onLoad, reject);
    else loader.load(modelUrl, onLoad, undefined, reject);
  });

  return {
    ready, setView, settings, update: sync,
    dispose() {
      renderer.setAnimationLoop(null); ro.disconnect(); io.disconnect(); controls.dispose();
      gui?.destroy(); composer?.dispose(); renderer.dispose(); renderer.domElement.remove();
    },
  };
}
