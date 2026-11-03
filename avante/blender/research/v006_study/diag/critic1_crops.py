import sys; sys.path.insert(0,'.')
from critic1_png import crop
crop('raw2',90,160,195,350,6,'critic1_raw2_shoulder.png',stretch=(0.6,1.0),grid=5)
crop('raw1',135,205,90,230,6,'critic1_raw1_shoulder.png',stretch=(0.55,1.0),grid=5)
crop('raw7',230,360,230,570,3,'critic1_raw7_shoulder.png',grid=10)
crop('raw2',330,370,195,350,6,'critic1_raw2_base.png',stretch=(0.6,1.0),grid=5)
crop('raw1',350,395,90,230,6,'critic1_raw1_base.png',stretch=(0.55,1.0),grid=5)
crop('raw7',720,800,230,570,3,'critic1_raw7_base.png',grid=10)
