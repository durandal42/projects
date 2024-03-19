START = (2,3,5,14,25,15)
TARGET = 69
OPS = '+-*/'

def solve(target, start):
  reachable = [(start, ())]
  solutions = []
  while reachable:
    old_reachable = reachable
    reachable = []
    for state, path in old_reachable:
#      print("Considering state:", state)
      for i,j,op,result,newstate in moves(state):
        step = "%d %s %d = %d" % (state[i],op,state[j],result)
        newpath = path + (step,)
        if result == target:
          solutions.append(newpath)
#          return newpath
        reachable.append((newstate, newpath))
    if solutions: return solutions

def moves(digits):
  for i in range(len(digits)):
    for j in range(len(digits)):
      if i == j: continue
      x,y = digits[i], digits[j]
      for op in OPS:
        if op in '+*' and i > j: continue
        if op == '/' and y == 0: continue
        if op == '+':
          if i > j: continue
          result = x + y
        elif op == '-':
          if y > x: continue
          result = x - y
        elif op == '*':
          if i > j: continue
          result = x * y
        elif op == '/':
          if x % y > 0: continue
          result = x // y

        newstate = sorted([x for k,x in enumerate(digits) if k not in [i,j]] + [result])
        yield i,j,op,result,newstate
        
# print(solve(TARGET, START))

# print(solve(81, (1,2,3,4,10,25)))

def ask_for_input():
  input_string = input('space-separated digits, starting with the target: ')
  numbers = [int(x) for x in input_string.split(' ')]
  return numbers[0], numbers[1:]

import sys

def main():
  if len(sys.argv) > 1:
    return do_daily_puzzle(int(sys.argv[1]))
  
  while True:
    target, start = ask_for_input()
    solutions = solve(target, start)
#    print(solutions)
    for solution in solutions:
      print(solution)
    print(f"({len(solutions)} solutions found.)")

import puzzlesFor2023Beta
    
def do_daily_puzzle(d):
  targets, numbers = puzzlesFor2023Beta.get_daily_puzzle(d)
  puzzle_solutions = []
  for target, start in zip(targets, numbers):
    print("Solving:", target, start)
    solutions = dedup_solutions(solve(target, start))
    for s in solutions:
      print("\t", s)
    puzzle_solutions.append(solutions)
  pretty_print_solutions(d, targets, puzzle_solutions)

def dedup_solutions(sols):
  sorted_sols_set = set()
  result = []
  for s in sols:
    sorted_sol = tuple(sorted(s))
    if sorted_sol in sorted_sols_set: continue
    sorted_sols_set.add(sorted_sol)
    result.append(s)
  return result

def pretty_print_solutions(day, targets, solutions):
  figure_space = ' '
  f_ops_map = {
    '+': '➕',
    '-': '➖',
    '*': '✖',
    '/': '➗',
  }

  print()
  print(f"Digits #{day} (15/15⭐)")
  total_ops = 0
  for t, solution in zip(targets, solutions):
    f_t = f"{t} ({t})"
    f_t_p = f_t + figure_space * (9 - len(f_t))
    f_ops = "".join([f_ops_map.get(op, '') for op in "".join(solution[0])])
    total_ops += len(f_ops)
    print(f"{f_t_p} {f_ops} ({len(solution)} solutions)")
  print()
  print(f"({total_ops} operations)")
    
main()
