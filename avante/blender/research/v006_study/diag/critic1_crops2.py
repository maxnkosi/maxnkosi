import sys; sys.path.insert(0,'.')
from critic1_png import crop
crop('raw5',250,420,120,380,3,'critic1_raw5_shoulder.png',stretch=(0.0,0.45))
crop('v006hero',1150,1200,270,360,6,'critic1_v006hero_edge.png',stretch=(0.0,0.9))
