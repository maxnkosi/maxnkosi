import * as THREE from 'three';

/**
 * Re-creates the Blender "Optical glass • calibrated frontal finish" material.
 *
 * Blender graph (inspected from the .blend):
 *   Mix( Principled glass , Mix(Emission(logo JPEG), Glossy, 0.075) , fac )
 *   fac = MapRange(view·surface facing, 0.88 → 0.998 → 0..1)
 * i.e. surfaces that look straight at the viewer show the supplied logo
 * artwork; bevels and oblique views fall through to refractive glass.
 *
 * The glTF exporter only keeps the Principled part (+ the JPEG as an emissive
 * texture), so the blend is rebuilt here on top of MeshPhysicalMaterial.
 */
export function createLogoGlass(exportedMaterial) {
  const logoTex = exportedMaterial.emissiveMap; // JPEG, UVs/colour space as exported
  logoTex.colorSpace = THREE.SRGBColorSpace;
  logoTex.anisotropy = 8;

  const mat = new THREE.MeshPhysicalMaterial({
    name: exportedMaterial.name,
    color: new THREE.Color(0.78, 0.94, 0.97), // Blender base colour (linear)
    metalness: 0,
    roughness: 0.055,
    ior: 1.5,
    transmission: 1,
    thickness: 0.64, // slab depth in the model (2x the original 0.32)
    attenuationColor: new THREE.Color(0.55, 0.85, 0.9),
    attenuationDistance: 1.2,
    specularIntensity: 1,
    envMapIntensity: 1.1,
    side: THREE.DoubleSide,
  });

  mat.onBeforeCompile = (shader) => {
    shader.uniforms.uLogo = { value: logoTex };
    shader.uniforms.uFacingMin = { value: 0.88 };
    shader.uniforms.uFacingMax = { value: 0.998 };
    shader.uniforms.uGlossyTint = { value: new THREE.Color(0.65, 0.84, 0.89) };

    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec2 vLogoUv;\nvarying vec3 vLogoWorldPos;\nvarying vec3 vLogoWorldN;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        vLogoUv = uv;
        vLogoWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        vLogoWorldN = normalize(mat3(modelMatrix) * normal);`);

    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
        uniform sampler2D uLogo; uniform float uFacingMin; uniform float uFacingMax; uniform vec3 uGlossyTint;
        varying vec2 vLogoUv; varying vec3 vLogoWorldPos; varying vec3 vLogoWorldN;`)
      .replace('#include <opaque_fragment>', `#include <opaque_fragment>
        {
          vec3 V = normalize(cameraPosition - vLogoWorldPos);
          vec3 N = normalize(vLogoWorldN);
          if (!gl_FrontFacing) N = -N;
          float facing = clamp((dot(N, V) - uFacingMin) / (uFacingMax - uFacingMin), 0.0, 1.0);
          vec3 art = texture2D(uLogo, vLogoUv).rgb;           // sampler is sRGB-decoded
          vec3 artShader = mix(art, uGlossyTint * art, 0.075); // Emission/Glossy 0.075 mix
          gl_FragColor.rgb = mix(gl_FragColor.rgb, artShader, facing);
          gl_FragColor.a = 1.0;
        }`);
  };
  mat.customProgramCacheKey = () => 'currency-stream-glass';
  return mat;
}

/**
 * Fully clear glass: no tint, no logo artwork, no absorption.
 * Only refraction (IOR 1.5), reflections and the bevel highlights show.
 */
export function createClearGlass() {
  return new THREE.MeshPhysicalMaterial({
    name: 'Clear glass',
    color: 0xffffff,
    metalness: 0,
    roughness: 0,
    ior: 1.5,
    transmission: 1,
    thickness: 0.64,            // slab depth in the model
    attenuationColor: new THREE.Color(0xffffff),
    attenuationDistance: Infinity, // no absorption = no colour cast
    specularIntensity: 1,
    envMapIntensity: 1.6,
    side: THREE.DoubleSide,
  });
}

/** Soft studio backdrop so clear glass has something to refract (flat white hides it). */
export function createStudioBackdrop() {
  const c = document.createElement('canvas'); c.width = 16; c.height = 512;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0, '#f4f7f9'); grad.addColorStop(0.5, '#cfd8de'); grad.addColorStop(1, '#eef2f4');
  g.fillStyle = grad; g.fillRect(0, 0, 16, 512);
  g.fillStyle = 'rgba(40,60,75,0.10)';           // faint horizon bands -> visible refraction
  for (const y of [150, 170, 330, 352]) g.fillRect(0, y, 16, 8);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
