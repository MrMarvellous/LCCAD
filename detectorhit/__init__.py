import sys
import platform
pltf = platform.platform()
if "Windows" in pltf:
    sys.path.append('D:/lung_cancer/LCCAD/detectorhit')
else:
    sys.path.append('/home/cuiyang/workspace/lung_cancer/LCCAD/detectorhit')
