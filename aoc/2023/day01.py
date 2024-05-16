from common import assertEqual
from common import submit


def digits(line):
  for c in line:
    if c.isdigit():
      yield c


def calibration(line):
  d = list(digits(line))
  return int(d[0] + d[-1])


assertEqual(12, calibration('1abc2'))
assertEqual(38, calibration('pqr3stu8vwx'))
assertEqual(15, calibration('a1b2c3d4e5f'))
assertEqual(77, calibration('treb7uchet'))


def day01(input):
  result = 0
  for line in input.splitlines():
    # print(line)
    result += calibration(line)
  return result


test_input = '''1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet
'''
test_output = 142

assertEqual(test_output, day01(test_input))


print('day01 answer:')
submit(day01(open('day01_input.txt', 'r').read()),
       expected=54953)
print()

# part 2 complication:
test_input_2 = '''two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen
'''
test_output_2 = 281


digit_words = ['one', 'two', 'three', 'four',
               'five', 'six', 'seven', 'eight', 'nine']
RECOGNIZED_DIGITS = {}
for i, dw in enumerate(digit_words):
  RECOGNIZED_DIGITS[dw] = str(i + 1)
for i in range(1, 10):
  RECOGNIZED_DIGITS[str(i)] = str(i)

# print(RECOGNIZED_DIGITS)


def digits(line):
  for i in range(len(line)):
    for k, v in RECOGNIZED_DIGITS.items():
      if line[i:].startswith(k):
        yield v


assertEqual(29, calibration('two1nine'))
assertEqual(83, calibration('eightwothree'))
assertEqual(13, calibration('abcone2threexyz'))
assertEqual(24, calibration('xtwone3four'))
assertEqual(42, calibration('4nineeightseven2'))
assertEqual(14, calibration('zoneight234'))
assertEqual(76, calibration('7pqrstsixteen'))
assertEqual(18, calibration('oneight'))  # the sneaky one!


assertEqual(test_output_2, day01(test_input_2))

print('day01 answer, part 2:')
submit(day01(open('day01_input.txt', 'r').read()),
       expected=53868)
