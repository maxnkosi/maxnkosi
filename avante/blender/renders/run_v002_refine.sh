#!/bin/zsh
# v002 refinement re-render (4 Nov): light-linked label fills (C07/C10) + C05 R24 backlight. Pre-refine copies in renders/photography/FINAL_pre_labelfill/.
cd "$(dirname $0)/.."
B=/Applications/Blender.app/Contents/MacOS/Blender
$B -b avante_variants_master_v002.blend --python render_photography.py -- FINAL PHOTO_C05_R24,PHOTO_C07_R25,PHOTO_C07_R24,PHOTO_C07_R22,PHOTO_C10_R25,PHOTO_C10_R21,PHOTO_C10_R23 100 256 2>&1 | grep -E "PHOTO_DONE|Error: [^N]"
$B -b avante_variants_master_v002.blend --python render_variants.py -- v002_diag/variants_v002 lineup_hero,lineup_threequarter 0.5 2>&1 | grep -E "VARIANT_DONE|Error: [^N]"
echo REFINE_DONE
