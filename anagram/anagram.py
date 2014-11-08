import collections

'''
Given a string target, find a pair of names which anagram to it.
'''
def find_anagram(target, names):
  target_count = collections.Counter(target)

  names_counts = [(n, collections.Counter(n)) for n in names]

  # Filter names that contain letters not in the target:
  names_counts = filter(lambda nc: target_count | collections.Counter(nc[0]) == target_count,
                        names_counts)

  for i, (name1, name1_count) in enumerate(names_counts):
    # Zero and negative counts are dropped when subtracting.
    # Because we pre-filtered names, counts can't be negative.
    remaining = target_count - name1_count


    for name2, name2_count in names_counts[i:]:
      if name2_count == remaining:
        yield name1, name2

assert (list(find_anagram('HEBUGSGORE',
                          ['GEORGE', 'BUSH', 'RALPH', 'NADER'])) ==
        [('GEORGE', 'BUSH')])

# someone on OKC said this was an anagram of her first and middle names. :P
for n1, n2 in find_anagram('ARMYAIRLINE', [line.strip().upper() for line in open('names.txt')]):
  print n1, n2
