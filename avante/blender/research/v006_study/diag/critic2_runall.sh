#!/bin/zsh
# critic prototype batch (study only). Sequential so the GPU is not shared.
cd /Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag
BL=/Applications/Blender.app/Contents/MacOS/Blender
run() { $BL -b --factory-startup --python critic2_proto.py -- "$@" 2>&1 | grep -E "CRITIC|CHECK|Traceback|Error" ; }
run 4 plane glass34,glasshero,full34,fullhero,shoulder,glassshoulder,neck,heel 64 r4_plane
run 3 plane glassshoulder,shoulder 64 r3_plane
run v006 plane glass34,glasshero,glassshoulder,shoulder,neck,heel 64 v006base
run 4 wrap shoulder 64 r4_wrap
CRIT_R0=47.38 CRIT_M=1.6 CRIT_RHON=18 run 4 plane glass34,full34,shoulder 64 r4_high
echo ALLDONE
