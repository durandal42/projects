# return a list of visited coordinates to draw a 3-d hilbert curve
# centered at 'center'
# recursion level 'level'
# visit 8 corners in order specified by v0..v7
def hilbert3D(center, level, v0=0, v1=1, v2=2, v3=3, v4=4, v5=5, v6=6, v7=7):
  if level == 0:
    return [center]  # level 0 is just a point

  # calculate center points of each octant
  x, y, z = center
  radius = 2**(level-1)
  octant_centers = [ (x - radius, y + radius, z - radius),  # -+-
                     (x - radius, y + radius, z + radius),  # -++
                     (x - radius, y - radius, z + radius),  # --+
                     (x - radius, y - radius, z - radius),  # ---
                     (x + radius, y - radius, z - radius),  # +--
                     (x + radius, y - radius, z + radius),  # +-+
                     (x + radius, y + radius, z + radius),  # +++
                     (x + radius, y + radius, z - radius),  # ++-
                     ]

  result = []
  result.extend(hilbert3D(octant_centers[v0], level-1, v0, v3, v4, v7, v6, v5, v2, v1))
  result.extend(hilbert3D(octant_centers[v1], level-1, v0, v7, v6, v1, v2, v5, v4, v3))
  result.extend(hilbert3D(octant_centers[v2], level-1, v0, v7, v6, v1, v2, v5, v4, v3))
  result.extend(hilbert3D(octant_centers[v3], level-1, v2, v3, v0, v1, v6, v7, v4, v5))
  result.extend(hilbert3D(octant_centers[v4], level-1, v2, v3, v0, v1, v6, v7, v4, v5))
  result.extend(hilbert3D(octant_centers[v5], level-1, v4, v3, v2, v5, v6, v1, v0, v7))
  result.extend(hilbert3D(octant_centers[v6], level-1, v4, v3, v2, v5, v6, v1, v0, v7))
  result.extend(hilbert3D(octant_centers[v7], level-1, v6, v5, v2, v1, v0, v3, v4, v7))
  return result

def write(a, x, y, z):
  # hack to rotate cube to match orientation of handmade cubes
  # easier done here than recomputing v0..v7 permutations above
  a[z][-1-y][x] = 1

def line(a, start, end):
  x,y,z = start
  endx,endy,endz = end
  dx,dy,dz = cmp(endx,x),cmp(endy,y),cmp(endz,z)
  write(a, x, y, z)
  while x != endx or y != endy or z != endz:
    x += dx
    y += dy
    z += dz
    write(a, x, y, z)

def hilbert3(size):
  dim = 2**(size+1)-1

  arr = [[[0 for z in range(dim)] for y in range(dim)] for x in range(dim)]

  # compute visits around center point
  visits = hilbert3D((dim/2,dim/2,dim/2), size)

  # connect the dots...
  for i in range(len(visits)-1):
    line(arr, visits[i], visits[i+1])

  return arr

def print_cube(a):
  for z in range(len(a)):
    plane = a[z]
    print '+'*(2*len(plane[0])-1), z+1, '/', len(a)
    for line in plane:
      print ' '.join(['X' if e else '_' for e in line])

def print_pymclevel(h):
  print "hilbert"
  size = len(h)

  # fill target area with air
  print "fill %d (Player), (%d, %d, %d)" % (0,
                                            size+2, size+2, size+2)
  for x in range(len(h)):
    plane = h[x]
    for y in range(len(plane)):
      line = plane[y]
      for z in range(len(line)):
        point = line[z]
        if point:
          print "fill %d (Player delta %d %d %d), (1, 1, 1)" % (1,
                                                                x+1, y+1, z+1)

  print "save"
  print "quit"
  print "yes"

import sys

# print_cube(hilbert3(int(sys.argv[1])))
print_pymclevel(hilbert3(int(sys.argv[1])))
