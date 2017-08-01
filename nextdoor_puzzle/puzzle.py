def verify_solution(solution):
  for i in range(1, len(solution)+1):
    x = int(solution[:i])
    if x%i: return False
  return True
verify_solution('3816547290')

def base_n_to_int(d, base):
  if len(d) == 0: return 0
  if len(d) == 1: return d[0]
  return d[-1] + base * base_n_to_int(d[:-1], base)

assert base_n_to_int([1,2,3], 10) == 123
assert base_n_to_int([1,0,1], 2) == 5
assert base_n_to_int([15,15], 16) == 255


def find_special_number(base):
  digits = set(range(base))

  branches_explored = 0
  branches_abandoned = 0
  partial_solutions = [([], digits)]
  for i in range(1, len(digits)+1):
    still_partial_solutions = []
    for s,remaining in partial_solutions:
      branch_still_alive = False
      for d in remaining:
        if (d == 0) != (i == base): continue  # have to use 0 last for %base
        if base % 2 == 0:
          # even/odd can only be determined from the final digit in an even base:
          if (d % 2) != (i % 2): continue  # need evens for evens, so need odds for odds
        if base == 10:  # base10-specific deductions:
          if (d == 5) != (i == 5): continue  # must be in {0,5} but 0 is reserved
          if (i in [4,8]) != (d in [2,6]): continue  # %3 is odd, so %4 must be 2,6; same for %7 and %8
        potential = s + [d]
        if base_n_to_int(potential, base) % i: continue
        branch_still_alive = True
        still_partial_solutions.append((potential, remaining - set([d])))
      if not branch_still_alive:
        #print 'abandoned branch:', s, remaining
        branches_abandoned += 1
    partial_solutions = still_partial_solutions
    #print i, len(partial_solutions), partial_solutions #[s for s,_ in partial_solutions]
    branches_explored += len(partial_solutions)

  print '\tbranches explored:', branches_explored
  print '\tbranches abandoned:', branches_abandoned
  return partial_solutions

for base in range(2, 101):
  print 'base %d:' % base
  results = find_special_number(base)
  print '\tfound %d solution(s):' % len(results)
  for s,_ in results:
    print '\t\t',s

