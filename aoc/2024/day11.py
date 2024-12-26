from common import assertEqual
from common import submit

import functools


def day11(input, n=25):
  stones = [int(s) for s in input.split(" ")]

  return sum(blink(s, n) for s in stones)


@functools.cache
def blink(s, n):
  if n == 0:
    return 1
  if s == 0:
    return blink(1, n-1)
  elif len(str(s)) % 2 == 0:
    s_str = str(s)
    return (blink(int(s_str[:len(s_str)//2]), n-1) +
            blink(int(s_str[len(s_str)//2:]), n-1))
  else:
    return blink(s * 2024, n-1)


assertEqual(3, day11("125 17", 1))
assertEqual(4, day11("253000 1 7", 1))


test_input = '125 17'
test_output = 55312

assertEqual(test_output, day11(test_input))


print('day11 answer:')
submit(day11(open('day11_input.txt', 'r').read()),
       expected=197157)
print()

# part 2 complication

print('day11, part 2 answer:')
submit(day11(open('day11_input.txt', 'r').read(), n=75),
       expected=234430066982597)
print()
