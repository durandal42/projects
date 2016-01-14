def build_index_map(alpha):
  return dict((c,i) for i,c in enumerate(alpha))

def sort_by_alpha(list, alpha):
  imap = build_index_map(alpha.lower())
  list.sort(key=lambda word: tuple([imap[letter] for letter in word.lower()]))

import sys
alphabet = len(sys.argv) > 1 and sys.argv[1] or "abcdefghijklmnopqrstuvwxyz"
words = [line.strip() for line in sys.stdin.readlines()]
sort_by_alpha(words, alphabet)
for word in words:
  print word


