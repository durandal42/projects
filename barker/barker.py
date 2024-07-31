import itertools
from fractions import Fraction

def find_abcd(N):
  ints = [None] * (N+1)
  running_sums = [0] + [None] * N
  reciprocals = [None] * (N+1)
  remaining_targets = [1] + [None] * N

  ints[1] = 0
  depth = 1
  while depth > 0:
    ints[depth] += 1
    reciprocals[depth] = Fraction(1, ints[depth])
    running_sums[depth] = running_sums[depth-1] + reciprocals[depth]
    remaining_targets[depth] = remaining_targets[depth-1] - reciprocals[depth]
    # print(f'{depth=}, {ints=}, {reciprocals=}, {running_sums=}, {remaining_targets=}')
    print("considering: sum(%s) = %s (%s remaining) (approx 1/%s)" % (
      ", ".join(str(r) for r in reciprocals[1:depth+1]),
      running_sums[depth],
      remaining_targets[depth],
      remaining_targets[depth] == 0 and "inf" or int(1/remaining_targets[depth]),
    ))
    if depth == N and remaining_targets[depth] == 0:
      yield ints[1:]
      depth -= 1  # "break"
      continue
    if remaining_targets[depth] <= 0:
      print("exceeded target")
      continue  # "continue"
    if remaining_targets[depth] - sum(Fraction(1, x) for x in range(ints[depth]+1, ints[depth]+(1+N-depth))) > 0:
      print("target unreachable")
      depth -= 1  # "break"
      continue
    if depth == N - 1:
      final_target = remaining_targets[depth]
      if final_target.numerator == 1:
        if final_target.denominator > ints[depth]:
          sol = ints[1:-1] + [final_target.denominator]
          yield sol
          continue  # "continue"
        else:
          print("final target is 1/x, but too low an x")
      else:
        print("final target is not 1/x")
        continue  # continue
    depth += 1  # recurse
    # ints[depth] = ints[depth-1]
    ints[depth] = max(ints[depth-1], int(1/remaining_targets[depth-1]))

if __name__ == '__main__':
  for n in range(1,10):
    for solution in find_abcd(n):
      print("solution(%d) found!" % n, solution)
      print(solution)
