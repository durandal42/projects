import itertools
import collections

def build_index_map(alpha):
  return collections.defaultdict(int, [(c,i) for i,c in enumerate(alpha)])

def compare_words_by_imap(left, right, imap):
  for cl, cr in itertools.izip(left, right):
    diff = imap[cl.lower()] - imap[cr.lower()]
    if diff: return diff
  return len(left) - len(right)

def cmp_by_alpha(alpha):
  imap = build_index_map(alpha)
  return lambda x, y: compare_words_by_imap(x, y, imap)

def sort_by_alpha(list, alpha):
  list.sort(cmp=cmp_by_alpha(alpha))

import sys
alphabet = len(sys.argv) > 1 and sys.argv[1] or "abcdefghijklmnopqrstuvwxyz"
words = [line.strip() for line in sys.stdin.readlines()]
sort_by_alpha(words, alphabet)
for word in words:
  print word


