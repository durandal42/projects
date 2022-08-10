import collections


def load_words(length=5):
  target_file = '../TWL06.txt'
  print('loading words...')
  return list(filter(lambda w: (len(w) == length) and len(set(w)) == length,
                     [word.strip().upper()
                      for word in open(target_file)]))


def word_to_bitmask(w):
  result = 0
  for c in w:
    result |= (1 << (ord(c) - ord('A')))
  return result


def print_bitmask(b):
  return "".join(b & (1 << i) and "1" or "0" for i in reversed(range(26)))


assert "0" * 21 + "1"*5 == print_bitmask(word_to_bitmask("ABCDE"))


print("Useful words:", len(load_words()))


def print_all_useful_words():
  for w in load_words():
    print(w, print_bitmask(word_to_bitmask(w)))

# print_all_useful_words()


def word_buckets(words):
  buckets = collections.defaultdict(list)
  for w in words:
    buckets[word_to_bitmask(w)].append(w)
  return buckets


def maximize_coverage(words, target_length):
  buckets = word_buckets(words)
  print("Number of buckets:", len(buckets))

  reachable = {0: []}
  for n in range(target_length):
    now_reachable = {}
    next_update = 1
    for i, b1 in enumerate(reachable):
      if i >= next_update:
        print("%d/%d" % (i, len(reachable)))
        next_update = i * 2
      for b2 in buckets:
        if b1 & b2 > 0:
          continue
        now_reachable[b1 | b2] = reachable[b1] + [buckets[b2][0]]
    reachable = now_reachable
    print("There are %d reachable maximum-length bitmasks using %d words" %
          (len(reachable), n+1))
  return reachable

  # print()
  # for w in words:


for b, ws in maximize_coverage(load_words(), 5).items():
  print(print_bitmask(b), ws)
