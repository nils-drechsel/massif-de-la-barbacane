import re
from subprocess import check_output
from glob import glob


def getAverageColour(colour, text):
  m = re.search(r"Channel statistics:\s*Pixels: \d*\s*.*" + colour + r":\s*min: \d*\.*\d* \(\d*\.*\d*\)\s*max: \d*\.*\d* \(\d*\.*\d*\)\s*mean: \d*\.*\d* \((\d*\.*\d*)\)", text, re.DOTALL)
  return m.group(1)

def getAltitude(text):
  m = re.search(r"GPSAltitude: (\d*)/(\d*)", text)

  if (m is None or len(m.groups()) < 2): return None
  return float(m.group(1)) / float(m.group(2))

def getCoord(tag, text):
  m = re.search(r"GPS" + tag + r": (\d*)/(\d*), (\d*)/(\d*), (\d*)/(\d*)", text)

  if (m is None or len(m.groups()) < 6): return None
  h = float(m.group(1)) / float(m.group(2))
  min = float(m.group(3)) / float(m.group(4))
  sec = float(m.group(5)) / float(m.group(6))
  return h + min/60.0 + sec/3600.0

def getClusterCol(text):
    m = re.search(r"cluster 0 n \d* f 0.\d* rgb (\d*) (\d*) (\d*)", text, re.DOTALL)
    if (m is None or len(m.groups()) < 3): return None
    return [float(m.group(1)) / 256.0, float(m.group(2)) / 256.0, float(m.group(3)) / 256.0]

def getData(f):
  print(f)
  out = check_output(["identify", "-verbose" ,f]).decode("UTF-8")
  cluster = check_output(" ".join(["../bin/summariser/bin/colorsummarizer", "-image" ,f, "-stats", "-clusters 3"]), shell=True).decode("UTF-8")
  cCol = getClusterCol(cluster)
  red = getAverageColour("Red", out)
  green = getAverageColour("Green", out)
  blue = getAverageColour("Blue", out)
  alt = getAltitude(out)
  lat = getCoord("Latitude", out)
  lon = getCoord("Longitude", out)

  if (alt is None or lat is None or lon is None): return None

  #return [str(red), str(green), str(blue), str(cCol[0]), str(cCol[1]), str(cCol[2]), str(alt), str(lat), str(lon)]
  return [str(cCol[0]), str(cCol[1]), str(cCol[2]), str(alt), str(lat), str(lon)]

files = glob("../img/*.JPG")

o = open ("../data/data.csv", "w")
#o.write("red,green,blue,cluster_red, cluster_green, cluster_blue, alt,lat,lon\n")
o.write("red,green,blue,alt,lat,lon\n")
for f in files:
  data = getData(f)
  if (data is None): continue
  o.write(",".join(data) + "\n")

o.close()
