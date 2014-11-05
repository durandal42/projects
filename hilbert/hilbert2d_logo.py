# logo-style implementation of 2-d hilbert curve

def reset():
  global x,y,dx,dy
  x,y,dx,dy = 0,0,1,0

def left(t):
  global dx,dy
  dx,dy = -t*dy,t*dx

def right(t):
  global dx,dy
  dx,dy = t*dy,-t*dx

def forward(a, d=2):
  global x,y,dx,dy
  for steps in range(d):
    a[x][y] = 1
    x = x+dx
    y = y+dy
    a[x][y] = 1

def hilbert2_line(a, r, t):
  global x,y,dx,dy
  if r == 0: return
  left(t)
  hilbert2_line(a, r-1, -t)
  forward(a)
  right(t)
  hilbert2_line(a, r-1, t)
  forward(a)
  hilbert2_line(a, r-1, t)
  right(t)
  forward(a)
  hilbert2_line(a, r-1, -t)
  left(t)

def hilbert2(size):
  dim = 2**(size+1)-1
  arr = [[0 for y in range(dim)] for x in range(dim)]
  reset()
  hilbert2_line(arr, size, 1);

  return arr

def print_square(a):
  for line in a:
    print ' '.join([('X' if e else '_') for e in line])

import sys

print_square(hilbert2(int(sys.argv[1])))
