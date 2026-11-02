import * as THREE from 'three';
import GUI from 'three/examples/jsm/libs/lil-gui.module.min.js';

/** Default settings per material. All values are live-editable from the panel. */
export function defaultSettings(kind) {
  const clear = kind === 'clear';
  return {
    glass: {
      ior: 1.5,                 // index of refraction (1 = none, 1.5 = glass, 2.4 = diamond)
      thickness: 0.64,          // optical depth the refraction ray travels (model units)
      transmission: 1,          // 1 = fully see-through
      roughness: clear ? 0 : 0.055, // >0 frosts the refraction
      dispersion: 0,            // chromatic split of the refraction
      internalFaces: true,      // render back faces too -> internal refractions/reflections
      absorption: clear ? 0 : 0.35, // 0 = none, 1 = strong tint with depth
      tint: clear ? '#ffffff' : '#c7f0f7',
    },
    reflections: {
      specular: 1, envIntensity: clear ? 1.6 : 1.1,
      clearcoat: 0, iridescence: 0,
    },
    artwork: { strength: 1, frontalMin: 0.88 }, // branded only
    lighting: { keyLight: 1.4, rimLight: 0.8 },
    occlusion: { enabled: false, intensity: 1, radius: 0.25, distanceExponent: 1, thickness: 1, scale: 1 },
  };
}

/** Push settings onto the material, lights and AO pass. Safe to call every change. */
export function applySettings(s, { mat, scene, key, rim, ao, kind }) {
  const g = s.glass, r = s.reflections;
  mat.ior = g.ior; mat.thickness = g.thickness; mat.transmission = g.transmission;
  mat.roughness = g.roughness; mat.dispersion = g.dispersion;
  mat.side = g.internalFaces ? THREE.DoubleSide : THREE.FrontSide;
  mat.attenuationDistance = g.absorption <= 0 ? Infinity : THREE.MathUtils.lerp(8, 0.15, g.absorption);
  mat.attenuationColor.set(g.tint);
  mat.color.set(kind === 'clear' ? '#ffffff' : g.tint);
  mat.specularIntensity = r.specular; mat.envMapIntensity = r.envIntensity;
  mat.clearcoat = r.clearcoat; mat.iridescence = r.iridescence;
  mat.needsUpdate = true;
  const u = mat.userData.uniforms;
  if (u) { u.uArtwork.value = s.artwork.strength; u.uFacingMin.value = Math.min(s.artwork.frontalMin, 0.997); }
  key.intensity = s.lighting.keyLight; rim.intensity = s.lighting.rimLight;
  if (ao) {
    const o = s.occlusion;
    ao.blendIntensity = o.intensity;
    ao.updateGtaoMaterial({ radius: o.radius, distanceExponent: o.distanceExponent, thickness: o.thickness, scale: o.scale });
    ao.updatePdMaterial({ radius: o.radius * 8 });
  }
}

/** Build the lil-gui panel inside `host`; `onChange` fires after every edit. */
export function buildPanel(host, s, kind, onChange, onReset) {
  const gui = new GUI({ container: host, title: 'Glass settings', width: 260 });
  Object.assign(gui.domElement.style, { position: 'absolute', top: '8px', right: '8px', zIndex: 5 });
  const ch = () => onChange();

  const f = gui.addFolder('Refraction');
  f.add(s.glass, 'ior', 1, 2.4, 0.01).name('IOR').onChange(ch);
  f.add(s.glass, 'thickness', 0, 2, 0.01).name('Depth').onChange(ch);
  f.add(s.glass, 'transmission', 0, 1, 0.01).name('Transmission').onChange(ch);
  f.add(s.glass, 'roughness', 0, 0.6, 0.005).name('Frosting').onChange(ch);
  f.add(s.glass, 'dispersion', 0, 5, 0.05).name('Dispersion').onChange(ch);
  f.add(s.glass, 'internalFaces').name('Internal back faces').onChange(ch);

  const t = gui.addFolder('Absorption / tint');
  t.add(s.glass, 'absorption', 0, 1, 0.01).name('Absorption').onChange(ch);
  t.addColor(s.glass, 'tint').name('Tint').onChange(ch);

  const rf = gui.addFolder('Reflections');
  rf.add(s.reflections, 'specular', 0, 1, 0.01).name('Specular').onChange(ch);
  rf.add(s.reflections, 'envIntensity', 0, 4, 0.05).name('Environment').onChange(ch);
  rf.add(s.reflections, 'clearcoat', 0, 1, 0.01).name('Clearcoat').onChange(ch);
  rf.add(s.reflections, 'iridescence', 0, 1, 0.01).name('Iridescence').onChange(ch);

  if (kind !== 'clear') {
    const a = gui.addFolder('Logo artwork');
    a.add(s.artwork, 'strength', 0, 1, 0.01).name('Artwork').onChange(ch);
    a.add(s.artwork, 'frontalMin', 0.3, 0.99, 0.005).name('Frontal range').onChange(ch);
  }

  const l = gui.addFolder('Lighting (static)');
  l.add(s.lighting, 'keyLight', 0, 4, 0.05).name('Key light').onChange(ch);
  l.add(s.lighting, 'rimLight', 0, 4, 0.05).name('Rim light').onChange(ch);

  const o = gui.addFolder('Occlusion (AO)');
  o.add(s.occlusion, 'enabled').name('Enabled').onChange(ch);
  o.add(s.occlusion, 'intensity', 0, 2, 0.01).name('Intensity').onChange(ch);
  o.add(s.occlusion, 'radius', 0.02, 1.5, 0.01).name('Radius').onChange(ch);
  o.add(s.occlusion, 'distanceExponent', 0.5, 4, 0.05).name('Falloff').onChange(ch);
  o.add(s.occlusion, 'thickness', 0.1, 4, 0.05).name('Thickness').onChange(ch);
  o.add(s.occlusion, 'scale', 0.2, 3, 0.05).name('Scale').onChange(ch);

  gui.add({ reset: onReset }, 'reset').name('Reset to defaults');
  ['Absorption / tint', 'Reflections', 'Logo artwork', 'Lighting (static)', 'Occlusion (AO)'].forEach((n) => gui.folders.find((x) => x._title === n)?.close());
  return gui;
}
