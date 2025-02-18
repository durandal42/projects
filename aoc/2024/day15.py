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
    if x == "O":
      r, c = loc
      total += 100*r + c
  return total


def day15(input):
  paragraphs = input.split("\n\n")
  grid = parse_grid(paragraphs[0])
  commands = list(paragraphs[1].replace("\n", ""))
  print(grid)
  print(render_grid(grid))
  assertEqual(paragraphs[0], render_grid(grid))
  print(commands)

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
       expected=None)
print()
