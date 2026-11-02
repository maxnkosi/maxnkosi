import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { defaultSettings, applySettings, buildPanel, mergeSettings } from './settings.js';
import { createLogoGlass, createClearGlass, createStudioBackdrop } from './glassMaterial.js';

const PRESETS = { front: [0, 0], oblique: [38, 14] };

/**
 * Mount the static Currency Stream glass logo into a DOM element.
 *
 * Built to be light on a page:
 *  - nothing loads until the element is near the viewport (`lazy`)
 *  - renders only when something changes (orbit, resize, setting), never in an idle loop
 *  - the settings panel and the occlusion pass are separate chunks, fetched only if used
 *  - optional `poster` image shows instantly and is the fallback if WebGL is unavailable
 *
 * @param {HTMLElement} el  container; the canvas fills it (give it a size)
 * @param {object} [o]
 * @param {string} [o.modelUrl]  URL of currency-stream-logo.glb
 * @param {string} [o.poster]  image URL shown until the 3D view is ready (and if WebGL fails)
 * @param {boolean} [o.lazy=true]  wait until the element is within 300px of the viewport
 * @param {number} [o.maxPixelRatio=2]  cap device pixel ratio (lower = faster on phones)
 * @param {'branded'|'clear'} [o.material='branded']  'clear' = 100% clear glass, no tint or artwork
 * @param {boolean} [o.panel=false]  show the live settings panel
 * @param {object} [o.settings]  partial overrides of the defaults in settings.js
 * @param {ArrayBuffer} [o.modelData]  GLB bytes already in memory (skips the network fetch)
 * @param {'front'|'oblique'} [o.view]  start pose (or pass yaw/pitch in degrees)
 * @param {boolean} [o.controls=true]  allow drag-to-orbit / wheel-to-zoom
 * @param {string|null} [o.background='#ffffff']  CSS colour, or null for transparent
 * @returns {{dispose():void, ready:Promise<void>, setView(v:string):void, settings:object, update():void}}
 */
export function mountCurrencyStreamLogo(el, o = {}) {
  const {
    modelUrl = `${import.meta.env.BASE_URL}models/currency-stream-logo.glb`,
    poster = null, lazy = true, maxPixelRatio = 2,
    view = 'front', material = 'branded', panel = false, settings: initial = null, modelData = null,
    controls: enableControls = true, background = '#ffffff',
  } = o;
  const [yaw, pitch] = o.yaw !== undefined ? [o.yaw, o.pitch ?? 0] : PRESETS[view] ?? PRESETS.front;

  if (poster) Object.assign(el.style, { backgroundImage: `url(${poster})`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'center' });

  // Settings (+ per-browser persistence, separate for each material).
  const defaults = () => defaultSettings(material);
  const settings = defaults();
  for (const k of Object.keys(initial ?? {})) Object.assign(settings[k] ?? (settings[k] = {}), initial[k]);
  const STORE = `currency-stream-logo:${material}`;
  const save = () => { try { localStorage.setItem(STORE, JSON.stringify(settings)); } catch { /* storage unavailable */ } };
  try { mergeSettings(settings, JSON.parse(localStorage.getItem(STORE))); } catch { /* none saved */ }

  let renderer, scene, camera, controls, key, rim, glassMat = null, gui = null;
  let composer = null, aoPass = null, aoLoading = false;
  let raf = 0, visible = true, alive = true, radius = 1, ro = null, io = null;

  // ---- rendering: only when invalidated -------------------------------------------------
  const frame = () => {
    raf = 0;
    if (!alive || !visible || !glassMat) return;
    controls.update();
    if (settings.occlusion.enabled && composer) composer.render(); else renderer.render(scene, camera);
  };
  const invalidate = () => { if (!raf && alive) raf = requestAnimationFrame(frame); };

  const loadAO = async () => {
    aoLoading = true;
    const [{ EffectComposer }, { RenderPass }, { GTAOPass }, { OutputPass }] = await Promise.all([
      import('three/examples/jsm/postprocessing/EffectComposer.js'),
      import('three/examples/jsm/postprocessing/RenderPass.js'),
      import('three/examples/jsm/postprocessing/GTAOPass.js'),
      import('three/examples/jsm/postprocessing/OutputPass.js'),
    ]);
    if (!alive) return;
    const size = renderer.getSize(new THREE.Vector2());
    composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType, samples: 4 }));
    composer.setPixelRatio(renderer.getPixelRatio());
    composer.addPass(new RenderPass(scene, camera));
    aoPass = new GTAOPass(scene, camera, size.x, size.y);
    composer.addPass(aoPass);
    composer.addPass(new OutputPass());
    composer.setSize(size.x, size.y);
    sync();
  };

  function sync() {
    if (!glassMat) return;
    if (settings.occlusion.enabled && !composer && !aoLoading) loadAO(); // chunk fetched on first use
    applySettings(settings, { mat: glassMat, scene, key, rim, ao: aoPass, kind: material });
    save(); invalidate();
  }
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

  const poseCamera = (yw, pt) => {
    const y = THREE.MathUtils.degToRad(yw), p = THREE.MathUtils.degToRad(pt);
    camera.position.set(Math.sin(y) * Math.cos(p), Math.sin(p), Math.cos(y) * Math.cos(p)).multiplyScalar(radius);
    controls.target.set(0, 0, 0); controls.update(); invalidate();
  };
  const setView = (v) => { if (glassMat) poseCamera(...(PRESETS[v] ?? PRESETS.front)); };

  // ---- one-time setup, run when the element is (nearly) visible ---------------------------
  let resolveReady; const ready = new Promise((r) => { resolveReady = r; });

  const init = () => {
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: background === null, powerPreference: 'high-performance' });
    } catch {
      el.dataset.fallback = 'true'; resolveReady(); return; // no WebGL: the poster stays
    }
    renderer.setPixelRatio(Math.min(devicePixelRatio, maxPixelRatio));
    renderer.toneMapping = THREE.NoToneMapping; // keep supplied artwork colours exact
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.style.cssText = 'display:block;width:100%;height:100%;touch-action:none';
    renderer.domElement.addEventListener('webglcontextlost', (e) => { e.preventDefault(); el.dataset.fallback = 'true'; });
    el.appendChild(renderer.domElement);

    scene = new THREE.Scene();
    if (material === 'clear' && background === '#ffffff') scene.add(createStudioBackdrop());
    else if (background !== null) scene.background = new THREE.Color(background);

    // Static lighting: fixed studio environment + two fixed lights.
    const pmrem = new THREE.PMREMGenerator(renderer);
    const room = new RoomEnvironment();
    scene.environment = pmrem.fromScene(room, 0.04).texture;
    room.dispose(); pmrem.dispose(); // free the generator's scratch targets, keep the result
    key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-4, 6, 8); scene.add(key);
    rim = new THREE.DirectionalLight(0xcfeeff, 0.8); rim.position.set(6, -3, 5); scene.add(rim);

    camera = new THREE.PerspectiveCamera(18, 1, 0.1, 500);
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enabled = enableControls; controls.enablePan = false; controls.rotateSpeed = 0.8;
    controls.enableDamping = !matchMedia('(prefers-reduced-motion: reduce)').matches;
    controls.dampingFactor = 0.08;
    controls.addEventListener('change', invalidate);

    const resize = () => {
      const w = el.clientWidth || 1, h = el.clientHeight || 1;
      renderer.setSize(w, h, false); composer?.setSize(w, h);
      camera.aspect = w / h; camera.updateProjectionMatrix(); invalidate();
    };
    ro = new ResizeObserver(resize); ro.observe(el); resize();

    const onLoad = (gltf) => {
      if (!alive) return;
      const logo = gltf.scene.getObjectByName('Currency Stream Logo') ?? gltf.scene;
      glassMat = material === 'clear' ? createClearGlass()
        : createLogoGlass(gltf.scene.getObjectByProperty('isMesh', true).material);
      logo.traverse((m) => { if (m.isMesh) m.material = glassMat; });

      const box = new THREE.Box3().setFromObject(logo);
      const size = box.getSize(new THREE.Vector3());
      logo.position.sub(box.getCenter(new THREE.Vector3()));
      scene.add(logo);

      radius = Math.max(size.x, size.y) * 0.5 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.12;
      controls.minDistance = radius * 0.4; controls.maxDistance = radius * 3;
      poseCamera(yaw, pitch);

      el.style.position ||= 'relative';
      if (panel) buildPanel(el, settings, material, sync, reset, settingsIO).then((g) => { gui = g; if (!alive) g.destroy(); });
      sync();
      requestAnimationFrame(() => { el.style.backgroundImage = ''; }); // drop the poster after the first real frame
      el.dataset.ready = 'true';
      resolveReady();
    };
    const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    if (modelData) loader.parse(modelData, '', onLoad, () => resolveReady());
    else loader.load(modelUrl, onLoad, undefined, () => { el.dataset.fallback = 'true'; resolveReady(); });
  };

  // ---- lazy start + pause while off screen -------------------------------------------------
  let started = false;
  const start = () => { if (!started && alive) { started = true; init(); } };
  if (typeof IntersectionObserver === 'undefined' || !lazy) start();
  io = typeof IntersectionObserver === 'undefined' ? null : new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (visible) { start(); invalidate(); }
  }, { rootMargin: '300px' });
  io?.observe(el);

  return {
    ready, setView, settings, update: sync,
    dispose() {
      alive = false; cancelAnimationFrame(raf); ro?.disconnect(); io?.disconnect();
      controls?.dispose(); gui?.destroy(); composer?.dispose();
      scene?.traverse((n) => { n.geometry?.dispose?.(); n.material?.dispose?.(); });
      renderer?.dispose(); renderer?.domElement.remove();
    },
  };
}
