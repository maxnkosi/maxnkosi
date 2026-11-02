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
