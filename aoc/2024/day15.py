from common import assertEqual
from common import submit


def parse_grid(input):
  return dict(((r, c), x)
              for r, row in enumerate(input.splitlines())
              for c, x in enumerate(row)
              if x != ".")


def render_grid(g):
  max_r = max(r for r, c in g.keys())
  max_c = max(c for r, c in g.keys())
  result = []
  for r in range(max_r+1):
    row = []
    for c in range(max_c+1):
      x = g.get((r, c), ".")
      row.append(x)
    result.append("".join(row))
  return "\n".join(result)


def find_robot(g):
  for loc, x in g.items():
    if x == "@":
      return loc


COMMAND_DIRECTIONS = {
    '^': (-1, 0),
    'v':  (1, 0),
    '>': (0, 1),
    '<': (0, -1),
}


def execute_command(grid, robot_loc, command):
  assert command in COMMAND_DIRECTIONS
  dr, dc = COMMAND_DIRECTIONS[command]
  r, c = robot_loc

  while grid.get((r, c), ".") not in "#.":
    r += dr
    c += dc
  end = grid.get((r, c), ".")
  if end == ".":  # empty space! push boxes!
    grid[(r, c)] = "O"
    del grid[robot_loc]
    robot_loc = robot_loc[0] + dr, robot_loc[1] + dc
    grid[robot_loc] = "@"
  if end == "#":  # wall! blocked!
    pass

  return grid, robot_loc


def total_gps(grid):
  total = 0
  for loc, x in grid.items():
    if x in "O[":
      r, c = loc
      total += 100*r + c
  return total


def day15(input):
  paragraphs = input.split("\n\n")
  grid = parse_grid(paragraphs[0])
  commands = list(paragraphs[1].replace("\n", ""))
  print(render_grid(grid))
  print()

  robot_loc = find_robot(grid)
  for command in commands:
    grid, robot_loc = execute_command(grid, robot_loc, command)

  print(render_grid(grid))

  return total_gps(grid)


test_input = '''\
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
'''
test_output = 10092

assertEqual(test_output, day15(test_input))


print('day15 answer:')
submit(day15(open('day15_input.txt', 'r').read()),
       expected=1563092)
print()

# part 2 complication


def parse_grid(input):
  result = {}
  for r, row in enumerate(input.splitlines()):
    for c, x in enumerate(row):
      if x == ".":
        continue
      if x == "O":
        result[(r, c*2)] = "["
        result[(r, c*2 + 1)] = "]"
      if x == "@":
        result[(r, c*2)] = "@"
      if x == "#":
        result[(r, c*2)] = "#"
        result[(r, c*2 + 1)] = "#"
  return result


def vertical_push(grid, robot_loc, dr, commit=False):
  r, c = robot_loc
  push_frontier = {c: "@"}
  prev_push_frontier = {}
  while True:
    # print(push_frontier, commit)
    r += dr
    next_push_frontier = {}
    for c in push_frontier:
      x = grid.get((r, c), ".")
      if x == "#":  # something we're pushing into is a wall; entire push fails
        return False
      elif x == ".":  # pushing into empty space; succeeds, but doesn't push onward
        continue
      elif x == "[":  # pushing one side of a box; pushes the whole box onward
        next_push_frontier[c] = "["
        next_push_frontier[c+1] = "]"
      elif x == "]":
        next_push_frontier[c-1] = "["
        next_push_frontier[c] = "]"
      else:
        assert False
    if commit:
      # print("committing push:", push_frontier)
      for c, x in push_frontier.items():
        grid[(r, c)] = x
        if c not in prev_push_frontier:
          del grid[(r-dr, c)]
    if not next_push_frontier:  # no further pushing; we've succeeded, and need to commit the whole move!
      if commit:
        return grid
      else:
        return True
    prev_push_frontier = push_frontier
    push_frontier = next_push_frontier


def execute_command(grid, robot_loc, command):
  # print()
  # print(render_grid(grid), robot_loc, command)
  assert command in COMMAND_DIRECTIONS
  dr, dc = COMMAND_DIRECTIONS[command]
  r, c = robot_loc

  if dr == 0:  # horizontal move; simple
    while grid.get((r, c), ".") not in "#.":
      r += dr
      c += dc
    end = grid.get((r, c), ".")
    if end == ".":  # empty space! push boxes!
      for backtrack_c in range(c, robot_loc[1], -dc):
        grid[(r, backtrack_c)] = grid[(r, backtrack_c - dc)]
      del grid[robot_loc]
      robot_loc = robot_loc[0] + dr, robot_loc[1] + dc
    if end == "#":  # wall! blocked!
      pass
  else:  # vertical move: harder
    if vertical_push(grid, robot_loc, dr):
      grid = vertical_push(grid, robot_loc, dr, commit=True)
      robot_loc = robot_loc[0] + dr, robot_loc[1] + dc

  return grid, robot_loc


test_output = 9021

assertEqual(test_output, day15(test_input))

print('day15, part 2 answer:')
submit(day15(open('day15_input.txt', 'r').read()),
       expected=None)
print()
