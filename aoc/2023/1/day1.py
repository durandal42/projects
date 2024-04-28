test_input = '''1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet
'''
test_output = 142


def day1(input):
  result = 0
  for line in input.splitlines():
    # print(line)
    line_digits = [c for c in line if c.isdigit()]
    # print(line_digits)
    result += int(line_digits[0] + line_digits[-1])
  return result

assert day1(test_input) == test_output

print(day1(open("input.txt", "r").read()))
