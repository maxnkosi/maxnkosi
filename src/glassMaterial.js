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
    shader.uniforms.uArtwork = { value: 1 };
    shader.uniforms.uFacingMin = { value: 0.88 };
    shader.uniforms.uFacingMax = { value: 0.998 };
    shader.uniforms.uGlossyTint = { value: new THREE.Color(0.65, 0.84, 0.89) };
    mat.userData.uniforms = shader.uniforms; // live-editable from the settings panel

    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec2 vLogoUv;\nvarying vec3 vLogoWorldPos;\nvarying vec3 vLogoWorldN;')
      .replace('#include <begin_vertex>', `#include <begin_vertex>
        vLogoUv = uv;
        vLogoWorldPos = (modelMatrix * vec4(position, 1.0)).xyz;
        vLogoWorldN = normalize(mat3(modelMatrix) * normal);`);

    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
        uniform sampler2D uLogo; uniform float uArtwork; uniform float uFacingMin; uniform float uFacingMax; uniform vec3 uGlossyTint;
        varying vec2 vLogoUv; varying vec3 vLogoWorldPos; varying vec3 vLogoWorldN;`)
      .replace('#include <opaque_fragment>', `#include <opaque_fragment>
        {
          vec3 V = normalize(cameraPosition - vLogoWorldPos);
          vec3 N = normalize(vLogoWorldN);
          if (!gl_FrontFacing) N = -N;
          float facing = clamp((dot(N, V) - uFacingMin) / (uFacingMax - uFacingMin), 0.0, 1.0);
          vec3 art = texture2D(uLogo, vLogoUv).rgb;           // sampler is sRGB-decoded
          vec3 artShader = mix(art, uGlossyTint * art, 0.075); // Emission/Glossy 0.075 mix
          gl_FragColor.rgb = mix(gl_FragColor.rgb, artShader, facing * uArtwork);
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

/**
 * Soft studio backdrop so clear glass has something to refract (flat white hides it).
 * A big inverted sphere rather than scene.background, because a textured
 * background breaks the ambient-occlusion pass. Only +-10deg of it is ever in view.
 */
export function createStudioBackdrop() {
  const H = 1024, c = document.createElement('canvas'); c.width = 8; c.height = H;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, H * 0.38, 0, H * 0.62); // canvas top = sphere top
  grad.addColorStop(0, '#f4f7f9'); grad.addColorStop(0.5, '#c3ced5'); grad.addColorStop(1, '#eef2f4');
  g.fillStyle = '#f4f7f9'; g.fillRect(0, 0, 8, H);
  g.fillStyle = grad; g.fillRect(0, H * 0.38, 8, H * 0.24);
  g.fillStyle = '#eef2f4'; g.fillRect(0, H * 0.62, 8, H * 0.38);
  g.fillStyle = 'rgba(40,60,75,0.18)';           // faint horizon bands -> visible refraction
  for (const f of [0.4655, 0.4745, 0.5255, 0.5345]) g.fillRect(0, H * f, 8, 2);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(80, 48, 32),
    new THREE.MeshBasicMaterial({ map: t, side: THREE.BackSide, fog: false, toneMapped: false }),
  );
  mesh.name = 'Studio backdrop';
  return mesh;
}
