cache = {}
def ack(m, n):
  if (m, n) in cache: return cache[(m,n)]
  result = None
  if not m: result = n+1
  elif not n: result = ack(m-1, 1)
  else: result = ack(m-1, ack(m, n-1))
  cache[(m,n)] = result
  return result

for i in range(6):
  for j in range(6):
    print 'ack(%d, %d) = %d' % (i, j, ack(i, j))
