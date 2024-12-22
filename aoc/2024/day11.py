from common import assertEqual
from common import submit


def day11(input):
  stones = [int(s) for s in input.split(" ")]

  for _ in range(25):
    stones = blink(stones)

  return len(stones)


def blink(stones):
  new_stones = []
  for s in stones:
    if s == 0:
      new_stones.append(1)
    elif len(str(s)) % 2 == 0:
      s_str = str(s)
      new_stones.append(int(s_str[:len(s_str)//2]))
      new_stones.append(int(s_str[len(s_str)//2:]))
    else:
      new_stones.append(s * 2024)
  return new_stones


assertEqual([253000, 1, 7], blink([125, 17]))
assertEqual([253, 0, 2024, 14168], blink([253000, 1, 7]))


test_input = '125 17'
test_output = 55312

assertEqual(test_output, day11(test_input))


print('day11 answer:')
submit(day11(open('day11_input.txt', 'r').read()),
       expected=197157)
print()
