from common import assertEqual
from common import submit


def first_digit(line):
  for c in line:
    if c.isdigit():
      return c


def last_digit(line):
  return first_digit(line[::-1])


def calibration(line):
  return int(first_digit(line) + last_digit(line))


assertEqual(12, calibration('1abc2'))
assertEqual(38, calibration('pqr3stu8vwx'))
assertEqual(15, calibration('a1b2c3d4e5f'))
assertEqual(77, calibration('treb7uchet'))


def day1(input):
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

assertEqual(test_output, day1(test_input))


print('day1 answer:')
submit(day1(open('day1_input.txt', 'r').read()),
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


def first_digit(line):
  while line:
    for k, v in RECOGNIZED_DIGITS.items():
      if line.startswith(k):
        return v
    else:
      line = line[1:]


def last_digit(line):
  while line:
    for k, v in RECOGNIZED_DIGITS.items():
      if line.endswith(k):
        return v
    else:
      line = line[:-1]

assertEqual(29, calibration('two1nine'))
assertEqual(83, calibration('eightwothree'))
assertEqual(13, calibration('abcone2threexyz'))
assertEqual(24, calibration('xtwone3four'))
assertEqual(42, calibration('4nineeightseven2'))
assertEqual(14, calibration('zoneight234'))
assertEqual(76, calibration('7pqrstsixteen'))
assertEqual(18, calibration('oneight'))  # the sneaky one!


assertEqual(test_output_2, day1(test_input_2))

print('day1 answer, part 2:')
submit(day1(open('day1_input.txt', 'r').read()),
       expected=53868)
