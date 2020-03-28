#!/usr/bin/python

import math
import os
import copy

height_field = "../data/heightfield.png"
outfile = "../data/barbican_heightfield2.pov"

def get_height_field(height_field):
    s = "height_field{\n"
    s = s + "png \"%s\" \n" %(height_field)
    #s = s + "texture {gradient_forest_snow}\n"

    s = s + """texture{
        pigment{
             image_map{ png "heightfield_texture.png"
                 map_type 0
                 interpolate 2
              }
        }
        finish { diffuse 0.9 phong 1 ambient 0.3}
    }"""

    s = s + "translate -0.5\n"
    s = s + "scale <1.77, 1, 1>\n"
    s = s + "}"
    return s


def get_rock_texture():
    s = """#declare forest_color_density=1.2; // Optional. Default value is 1.0, which is adequate in a gradient, but looks too dark when the texture is used alone as here

        #declare forest_normal=1.0; // Optional. Increase to emphasize the bumps, decrease to smooth them
        #declare forest_normal_scale=1.0;  // Optional. Relative size of the bumps.
        #declare UseGranite=1.0 ; // Set to 1.0 for using a granite pattern instead of bumps, for a "sharper" look
        #include "slope_patterns.inc"
        """
    return s

camlength = 1.5

cam = [0, 10.5, 2.8]

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
#o.write(get_rock_texture())
o.write(get_height_field(height_field))

o.close()

#os.system("povray "+outfile+" -W320 -H200 +UA")
#os.system("povray "+outfile+" -W640 -H480 +UA")
#os.system("povray "+outfile+" -W1280 -H1024 +UA")
os.system("povray "+outfile+" -W1600 -H1280 +UA +WT8")
#os.system("povray "+outfile+" -W1920 -H1536 +UA")
#os.system("povray "+outfile+" -W2048 -H1638")
