import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { createLogoGlass } from './glassMaterial.js';

const MODEL_URL = '/models/currency-stream-logo.glb';

// ?view=front (default) | oblique | custom ?yaw=deg&pitch=deg
const q = new URLSearchParams(location.search);
const presets = { front: [0, 0], oblique: [38, 14] };
const [yaw, pitch] = q.has('yaw')
  ? [Number(q.get('yaw')), Number(q.get('pitch') ?? 0)]
  : presets[q.get('view') ?? 'front'] ?? presets.front;

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.NoToneMapping; // keep the supplied artwork colours exact
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// Static lighting: fixed studio environment + two fixed key lights (never animated).
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-4, 6, 8); scene.add(key);
const rim = new THREE.DirectionalLight(0xcfeeff, 0.8); rim.position.set(6, -3, 5); scene.add(rim);

const camera = new THREE.PerspectiveCamera(18, innerWidth / innerHeight, 0.1, 500);

// Drag = orbit, wheel/pinch = zoom, right-drag = pan. Lights stay fixed in the scene.
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.rotateSpeed = 0.8;

new GLTFLoader().load(MODEL_URL, (gltf) => {
  const logo = gltf.scene.getObjectByName('Currency Stream Logo') ?? gltf.scene;
  const glass = createLogoGlass(gltf.scene.getObjectByProperty('isMesh', true).material);
  logo.traverse((o) => { if (o.isMesh) o.material = glass; });

  // Centre by bounding box on a wrapper so the GLB's relative layout is untouched.
  const box = new THREE.Box3().setFromObject(logo);
  const centre = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const pivot = new THREE.Group();
  logo.position.sub(centre);
  pivot.add(logo);
  scene.add(pivot);

  // Camera is orbited (static pose), the model and lights never move.
  const radius = Math.max(size.x, size.y) * 0.5 / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.12;
  const y = THREE.MathUtils.degToRad(yaw), p = THREE.MathUtils.degToRad(pitch);
  camera.position.set(Math.sin(y) * Math.cos(p), Math.sin(p), Math.cos(y) * Math.cos(p)).multiplyScalar(radius);
  camera.lookAt(0, 0, 0);
  controls.target.set(0, 0, 0);
  controls.minDistance = radius * 0.4;
  controls.maxDistance = radius * 3;
  controls.update();

  renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
  window.__logoReady = true;
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
