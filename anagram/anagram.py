from utils import count

names = set()
for line in open('names.txt'):
  name = line.strip().upper().split(',')[0]
  names.add(name)
  #  print name


'''
Given two maps of element->count, return the difference.

If any value in the result would be negative, instead return None.
'''
def subtract_counts(left, right):
  result = {}
  for k,v in right.iteritems():
    if k not in left:
      return None
  for k,v in left.iteritems():
    if k in right:
      if left[k] > right[k]:
        result[k] = left[k] - right[k]
      elif left[k] < right[k]:
        return None
    else:
      result[k] = left[k]
  return result

# print subtract_counts(count(target),count('MIRIAM'))

'''
Given a string target, find a pair of names which anagram to it.
'''
def find_anagram(target):
  target_counts = count(target)
  for name1 in names:
    name1_counts = count(name1)
    remaining = subtract_counts(target_counts, name1_counts)
    if not remaining: continue
    for name2 in names:
      if count(name2) == remaining:
        print name1,name2

# someone on OKC said this was an anagram of her first and middle names. :P
find_anagram("ARMYAIRLINE")
