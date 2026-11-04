#!/bin/zsh
# v002 render queue: rebuild rigs, 10 diagnostics (256 spp), 15 final photographs (256 spp, denoised)
cd "$(dirname "$0")/.."
BL=/Applications/Blender.app/Contents/MacOS/Blender
: rigs already rebuilt
$BL -b avante_variants_master_v002.blend --python render_variants.py -- v002_diag/variants_v002 C01_hero,C01_threequarter,C05_hero,C05_threequarter,C06_hero,C06_threequarter,C07_hero,C07_threequarter,C10_hero,C10_threequarter 0.5 2>&1 | grep --line-buffered -E "VARIANT_DONE|Error: [^N]"
$BL -b avante_variants_master_v002.blend --python render_photography.py -- FINAL all 100 256 2>&1 | grep --line-buffered -E "PHOTO_DONE|Error: [^N]"
echo QUEUE_DONE
