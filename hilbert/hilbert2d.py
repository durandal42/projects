# return a list of visited coordinates to draw a 2-d hilbert curve
# centered at 'center'
# recursion level 'level'
# visit 4 corners in order specified by v0..v3
def hilbert2D(center, level, v0=0, v1=1, v2=2, v3=3):
  if level == 0:
    return [center]  # level 0 is just a point

  # calculate center points of each quadrant
  x, y = center
  radius = 2**(level-1)
  quadrant_centers = [ (x - radius, y - radius),
                       (x - radius, y + radius),
                       (x + radius, y + radius),
                       (x + radius, y - radius),
                     ]

  result = []
  result.extend(hilbert2D(quadrant_centers[v0], level-1, v0, v3, v2, v1))
  result.extend(hilbert2D(quadrant_centers[v1], level-1, v0, v1, v2, v3))
  result.extend(hilbert2D(quadrant_centers[v2], level-1, v0, v1, v2, v3))
  result.extend(hilbert2D(quadrant_centers[v3], level-1, v2, v1, v0, v3))
  return result

def write(a, x, y):
  # hack to rotate cube to match orientation of handmade cubes
  # easier done here than recomputing v0..v7 permutations above
  a[x][y] = 1

def line(a, start, end):
  x,y = start
  endx,endy = end
  dx,dy = cmp(endx,x),cmp(endy,y)
  write(a, x, y)
  while x != endx or y != endy:
    x += dx
    y += dy
    write(a, x, y)

def hilbert2(size):
  dim = 2**(size+1)-1

  arr = [[0 for y in range(dim)] for x in range(dim)]

  # compute visits around center point
  visits = hilbert2D((dim/2,dim/2), size)

  # connect the dots...
  for i in range(len(visits)-1):
    line(arr, visits[i], visits[i+1])

  return arr

def print_square(a):
  for line in a:
    print ' '.join(['X' if e else '_' for e in line])

import sys

print_square(hilbert2(int(sys.argv[1])))
