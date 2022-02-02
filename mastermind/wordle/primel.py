def prime(n):
  if n % 2 == 0: return False
  for k in range(3, n):
    if n % k == 0: return False
    if k*k > n: return True

for n in range(10001, 99999):
  if prime(n):
    print(n)

    
