level1 = """7
`
  _
623
75
`
  6
23_
57
"""

def parse_state(state_string):
  result = {}
  for x, line in enumerate(state_string.splitlines()):
    for y, char in enumerate(line):
      if char in '0123456789':
        result[(x,y)] = int(char)
      elif char != ' ':
        result[(x,y)] = char
  # print "parsed:", result
  return result

def print_state(state, swap=None):
  result = ""
  current_line = 0
  current_char = 0
  for x,y in sorted(state.keys()):
    while x > current_line:
      result += "\n"
      current_line += 1
      current_char = 0
    while y > current_char:
      result += "   "
      current_char += 1
    if (swap and (x,y) in swap) or (not swap):
      result += "[%s]" % state[(x,y)]
    else:
      result += " %s " % state[(x,y)]
    current_char += 1
  print result
  print

def parse_level(level_string):
  chunks = level_string.split("`\n")
  limit = int(chunks[0])
  start = parse_state(chunks[1])
  goal = parse_state(chunks[2])
  return start, goal, limit

def potential_swaps(state):
  for x,y in state.keys():
    if (x+1,y) in state: yield ((x,y),(x+1,y))
    if (x,y+1) in state: yield ((x,y),(x,y+1))

class IllegalSwap(Exception):
  pass

def swap_tiles(left, right):
  if right is '+' and isinstance(left, int):
    left += 1
    if left > 9: raise IllegalSwap()
  if right is '-' and isinstance(left, int):
    left -= 1
    if left < 1: raise IllegalSwap()
  if left is '+' and isinstance(right, int):
    right += 1
    if right > 9: raise IllegalSwap()
  if left is '-' and isinstance(right, int):
    right -= 1
    if left < 1: raise IllegalSwap()
  # as of level 21, swapping [+][+] becomes [-][-]
  if left == '+' and right == '+': return '-', '-'
  if left == '-' and right == '-': return '+', '+'
  return right, left

def perform_swap(swap, state):
  new_state = state.copy()
  new_state[swap[0]], new_state[swap[1]] = swap_tiles(state[swap[0]], state[swap[1]])
  return new_state

from collections import deque
def find_solution(start, goal, limit):
  horizon = deque([(start, [])])
  seen = set()
  highwater = 0
  while horizon:
    state, swaps = horizon.popleft()
    depth = len(swaps)
    if depth > limit: continue
    if depth > highwater:
      print "reached depth %d, considering %d states..." % (depth, len(horizon))
      highwater = depth

    for swap in potential_swaps(state):
      try:
        new_state = perform_swap(swap, state)
      except IllegalSwap:
        continue
      if not new_state: continue
      if new_state == goal: return swaps + [swap]
      if frozenset(new_state.items()) in seen: continue
      horizon.append((new_state, swaps + [swap]))
      seen.add(frozenset(new_state.items()))

  return None

def display_solution(state, swaps):
  if not swaps:
    print_state(state)
    print "NO SOLUTION"
  else:
    for swap in swaps:
      #print "[%s] <-> [%s]\t\t%s" % (state[swap[0]], state[swap[1]], swap)
      print_state(state, swap)
      state = perform_swap(swap, state)
    print_state(state)
    print "SOLVED in %d moves" % len(swaps)

def solve(start, goal, limit=10):
  display_solution(start, find_solution(start, goal, limit))

def process(level_string):
  start, goal, limit = parse_level(level_string)
  solve(start, goal, limit-3)  # assume: always actually solveable in target-3

def process_file(level_id):
  level_file = open("levels/%03d.txt" % level_id)
  process(level_file.read())

import sys
if len(sys.argv) > 1:
  process(open(sys.argv[1]).read())