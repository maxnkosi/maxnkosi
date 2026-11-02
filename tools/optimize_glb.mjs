// Shrink the exported GLB for the web: weld, quantize, meshopt-compress, downsize texture.
// Usage: node tools/optimize_glb.mjs <in.glb> <out.glb> [textureSize=1536]
import { NodeIO } from '@gltf-transform/core';
import { EXTMeshoptCompression, KHRMeshQuantization } from '@gltf-transform/extensions';
import { weld, quantize, meshopt, dedup, prune, textureCompress } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import sharp from 'sharp';

const [inp, out, size = '1536'] = process.argv.slice(2);
await MeshoptEncoder.ready; await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions([EXTMeshoptCompression, KHRMeshQuantization])
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });
const doc = await io.read(inp);
await doc.transform(
  dedup(), prune(),
  weld({ tolerance: 0 }),                  // exact duplicates only: keeps the bevel shading untouched
  quantize({ quantizePosition: 14, quantizeNormal: 10, quantizeTexcoord: 14 }),
  textureCompress({ encoder: sharp, targetFormat: 'jpeg', resize: [+size, +size], quality: 85 }),
  meshopt({ encoder: MeshoptEncoder, level: 'high' }),
);
await io.write(out, doc);
console.log('wrote', out);
