import collections
import queue
from trie import Trie

BAD_WORDS = set([
    'FIXT',
    'TREF',
    'PLEX',
])


def filter_bad_words(words):
  for w in words:
    if len(w) < 3:
      continue
    if w in BAD_WORDS:
      continue
    yield w

# WORDS = [word.lower().strip() for word in open('../TWL06.txt')]
WORDS = Trie(filter_bad_words(
    (line.strip().upper() for line in open('../TWL06.txt'))))


State = collections.namedtuple(
    "State", ['progress', 'index', 'unused_letters', 'terminal'])


def num_unused_letters(s):
  return sum(len(letters) for letters in s.unused_letters)


def legal_successors(s, available_letters):
  for i in range(len(available_letters)):
    if i == s.index:
      continue
    for l in available_letters[i]:
      tn = WORDS.root
      for c in s.progress[-1]:
        tn = tn[c]
      is_prefix = (l in tn)
      is_full_word = is_prefix and (' ' in tn[l])

      if not is_prefix:
        continue

      new_letters = s.unused_letters[:]
      new_letters[i] = ''.join(c for c in new_letters[i] if c != l)
      new_word = s.progress[-1] + l
      new_progress = s.progress[:-1] + [new_word]

      if is_prefix:
        # this is a valid prefix, so we can keep building
        yield State(new_progress, i, new_letters, is_full_word)

      if is_full_word:
        # this is a valid word, so we can start a new one
        yield State(new_progress + [l], i, new_letters, False)


def find_solutions(letters):
  q = queue.PriorityQueue()
  start = State([''], None, letters, False)
  q.put((0, num_unused_letters(start), start))

  states_seen = 0
  best_solution_length = None
  while q and states_seen < 1000000:
    words_used, _, s = q.get()
    if best_solution_length is not None and words_used > best_solution_length:
      break
    states_seen += 1
    for successor in legal_successors(s, letters):
      remaining = num_unused_letters(successor)
      if successor.terminal and remaining == 0:
        print("SOLUTION:", successor.progress)
        best_solution_length = len(successor.progress)
        yield successor.progress
      else:
        print(states_seen, successor)
        q.put((len(successor.progress), remaining, successor))


def print_best_solutions(letters):
  for solution in sorted(find_solutions(letters), key=lambda s: -len(s))[-10:]:
    print(solution)

LETTERS = [  # 2024-04-30
    'RPI',
    'GXF',
    'UET',
    'VLA',
]

# LETTERS = [  # 2024-04-29
#     'NLO',
#     'DAR',
#     'PHI',
#     'UWT',
# ]


print_best_solutions(LETTERS)
