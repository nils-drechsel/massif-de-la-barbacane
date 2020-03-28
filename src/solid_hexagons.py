#!/usr/bin/python

import math
import os
import copy

fileName = "../data/hex2.csv"
outfile = "../data/barbican1.pov"


def merge(objs):
  s = "merge{"
  for o in objs:
    s = s + " " + o
  s = s + "}"
  return s

def union(objs):
  s = "union{"
  for o in objs:
    s = s + " " + o
  s = s + "}"
  return s

def hexpoints(radius, lat, lon):
  result = []

  xPrev = 0;
  yPrev = 0;

  for i in range(0, 6):
    angle = (math.pi / 3.0) * i

    x = math.sin(angle) * radius
    y = -math.cos(angle) * radius
    result.append([x + lon, y + lat])
    xPrev = copy.copy(x)
    yPrev = copy.copy(y)

  return result


def hexprism(radius, lat, lon, alt, red, green, blue):
  hex = hexpoints(radius, lat, lon)

  s = """prism {
    linear_sweep
    linear_spline
    -3,
    %f,
    7,
    <%f,%f>, <%f,%f>, <%f,%f>, <%f,%f>, <%f, %f>, <%f,%f>, <%f,%f>
    material{
         texture{
          pigment{ rgb<%f,%f,%f> transmit %f}
          normal { wrinkles 0.35 scale 0.25 turbulence 0.3 translate<-0.05,0,0> rotate<0,-20,0>}
          finish { ambient 0.1
                   diffuse 0.35
                   specular 0.7
                   roughness 0.001
                   phong 0.4
                   phong_size 400
                   reflection { 0.05, 1.0 fresnel on }
                   conserve_energy
                 }
           } // end of texture


        } // end of material
  }""" %(alt, hex[0][0], hex[0][1], hex[1][0], hex[1][1], hex[2][0], hex[2][1], hex[3][0], hex[3][1], hex[4][0], hex[4][1], hex[5][0], hex[5][1], hex[0][0], hex[0][1], red, green, blue, 0.5)
  return s

def hexcap(radius, lat, lon, alt):
  hex = hexpoints(radius, lat, lon)

  cap = []
  cap.append(cylinder(hex[0], hex[1], alt))
  cap.append(cylinder(hex[1], hex[2], alt))
  cap.append(cylinder(hex[2], hex[3], alt))
  cap.append(cylinder(hex[3], hex[4], alt))
  cap.append(cylinder(hex[4], hex[5], alt))
  cap.append(cylinder(hex[5], hex[0], alt))

  cap.append(sphere(hex[0], alt))
  cap.append(sphere(hex[1], alt))
  cap.append(sphere(hex[2], alt))
  cap.append(sphere(hex[3], alt))
  cap.append(sphere(hex[4], alt))
  cap.append(sphere(hex[5], alt))

  return cap

def cylinder(x0, x1, alt):
  s = """cylinder {
    <%f, %f, %f>
    <%f, %f, %f>
    0.005
    pigment { rgb<0,0,0> }
  }""" %(x0[0], alt, x0[1], x1[0], alt, x1[1])
  return s

def sphere(x, alt):
  s = """sphere {
    <%f, %f, %f>
    0.006
    pigment { rgb<0,0,0> }
  }""" %(x[0], alt, x[1])
  return s


prisms = []
caps = []
radius = 0
j = 0
with open(fileName, 'r') as f:
  for line in f:
    line=line.strip()
    c = line.split(",")

    if (j == 1): radius = float(c[0])

    if j>2:
      prisms.append(hexprism(radius, float(c[0]),float(c[1]),float(c[2]),float(c[3]),float(c[4]),float(c[5])))
      caps.extend(hexcap(radius, float(c[0]),float(c[1]),float(c[2])))
    j=j+1




camlength = 6.5

cam = [0, 10.5, 4.8]

l = math.sqrt(cam[0]*cam[0] + cam[1]*cam[1] + cam[2]*cam[2])
cam[0] = cam[0]*camlength/l
cam[1] = cam[1]*camlength/l
cam[2] = cam[2]*camlength/l

o = open(outfile,"w")

o.write("#include \"colors.inc\"\n\n")
s = "camera {\n location <%f, %f, %f>\n look_at  <0, 0.2 ,  0>\n}" %(cam[0],cam[1],cam[2])
o.write(s)
s = "light_source { <%f, %f, %f> color White}\n" %(cam[0],cam[1],cam[2])
o.write(s)

#objs = prisms + caps
objs = prisms
m = merge(objs)

o.write(m)
o.close()

os.system("povray "+outfile+" -W320 -H200 +UA")
#os.system("povray "+outfile+" -W640 -H480 +UA")
#os.system("povray "+outfile+" -W1280 -H1024 +UA")
#os.system("povray "+outfile+" -W1600 -H1280 +UA")
#os.system("povray "+outfile+" -W1920 -H1536 +UA")
#os.system("povray "+outfile+" -W2048 -H1638")
