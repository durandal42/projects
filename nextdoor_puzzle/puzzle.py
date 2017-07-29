def verify_solution(solution):
  for i in range(1, len(solution)+1):
    x = int(solution[:i])
    if x%i: return False
  return True
verify_solution('3816547290')

digits = '1234567890'

branches_explored = 0
branches_abandoned = 0
partial_solutions = [('', set(digits))]
for i in digits:
  still_partial_solutions = []
  for s,remaining in partial_solutions:
    branch_still_alive = False
    for d in remaining:
      if (d == '0') != (i == '0'): continue  # have to use 0 last for %10
      if (d == '5') != (i == '5'): continue  # therefore, have to use 5 for %5
      if (int(d) % 2) != (int(i) % 2): continue  # need evens for evens, so need odds for odds
      if (i in '48') != (d in '26'): continue  # %3 is odd, so %4 must be 2,6; same for %7 and %8
      potential = s + str(d)
      if int(potential) % (int(i) or 10): continue
      branch_still_alive = True
      still_partial_solutions.append((potential, remaining - set(d)))
    if not branch_still_alive:
      print 'abandoned branch:', s, remaining
      branches_abandoned += 1
  partial_solutions = still_partial_solutions
  print i, len(partial_solutions), partial_solutions #[s for s,_ in partial_solutions]
  branches_explored += len(partial_solutions)

print 'branches explored:', branches_explored
print 'branches abandoned:', branches_abandoned
print partial_solutions
for s,_ in partial_solutions:
  if sorted(s) == sorted(digits): print s
