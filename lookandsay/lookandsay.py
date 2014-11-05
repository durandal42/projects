'''
prints lines of the "look-and-say sequence":
1
11
21
1211
...

see http://en.wikipedia.org/wiki/Look-and-say_sequence
'''

def next(line):
  previous = None
  count = 0
  result = ''
  for c in line:
    if c == previous:
      count += 1
    else:
      if previous:
        result += str(count)
        result += previous
      previous = c
      count = 1
  result += str(count)
  result += previous
  return result

line = '1'
while True:
  print line
  line = next(line)
