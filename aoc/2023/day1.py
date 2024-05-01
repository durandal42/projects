from common import assertEqual


def first_digit(line):
  for c in line:
    if c.isdigit():
      return c


def last_digit(line):
  return first_digit(line[::-1])


def calibration(line):
  return int(first_digit(line) + last_digit(line))


assertEqual(calibration('1abc2'),  12)
assertEqual(calibration('pqr3stu8vwx'),  38)
assertEqual(calibration('a1b2c3d4e5f'),  15)
assertEqual(calibration('treb7uchet'),  77)


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

assertEqual(day1(test_input), test_output)


print('day1 answer:', day1(open('day1_input.txt', 'r').read()))
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

assertEqual(calibration('two1nine'), 29)
assertEqual(calibration('eightwothree'), 83)
assertEqual(calibration('abcone2threexyz'), 13)
assertEqual(calibration('xtwone3four'), 24)
assertEqual(calibration('4nineeightseven2'), 42)
assertEqual(calibration('zoneight234'), 14)
assertEqual(calibration('7pqrstsixteen'), 76)
assertEqual(calibration('oneight'), 18)  # the sneaky one!


assertEqual(day1(test_input_2), test_output_2)

print('day1 answer, part 2:', day1(open('day1_input.txt', 'r').read()))
