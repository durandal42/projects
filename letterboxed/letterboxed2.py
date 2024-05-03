import collections
import queue

BAD_WORDS = set([
    'FIXT',
    'TREF',
    'PLEX',
])


print('loading words...')
ALL_WORDS = [line.strip().upper() for line in open('../TWL06.txt')]
print(f'loaded {len(ALL_WORDS)} words.')


def word_uses_only_available_letters(word, letters):
  for c in word:
    if not any(c in side for side in letters):
      return False
  return True


def word_repeats_side(word, letters):
  for c1, c2 in zip(word[:-2], word[1:]):
    for side in letters:
      if c1 in side and c2 in side:
        return True
  return False


def filter_words(words, letters):
  for w in words:
    if len(w) < 3:
      continue
    if w in BAD_WORDS:
      continue
    if not word_uses_only_available_letters(w, letters):
      continue
    if word_repeats_side(w, letters):
      continue
    yield w


def find_solutions(letters):
  words = list(filter_words(ALL_WORDS, letters))
  print(f'reduced to {len(words)} usable words.')
  words_by_first_letter = collections.defaultdict(list)
  for w in words:
    words_by_first_letter[w[0]].append(w)

  for c, ws in words_by_first_letter.items():
    print(f'{c}: {len(ws)}')

  letters_needed = set(''.join(letters))
  print('letters_needed:', ''.join(sorted(letters_needed)))

  q = queue.PriorityQueue()
  start = []
  q.put((len(start), start))

  best_solution_length = None
  while not q.empty():
    num_words_used, words_used = q.get()
    # print(num_words_used, words_used)
    if best_solution_length and num_words_used >= best_solution_length:
      continue
    letters_used_so_far = set(''.join(words_used))
    if not words_used:
      next_words = words
    else:
      next_words = words_by_first_letter[words_used[-1][-1]]
    for next_word in next_words:
      new_words = words_used + [next_word]
      if letters_used_so_far.union(set(next_word)) == letters_needed:
        best_solution_length = len(new_words)
        yield new_words
      else:
        q.put((len(new_words), new_words))


def print_best_solutions(puzzle):
  for solution in sorted(find_solutions(puzzle.split('-')),
                         key=lambda s: -sum(len(w) for w in s))[-10:]:
    print(solution)


PUZZLES = [
    'NLO-DAR-PHI-UWT',  # 2024-04-29
    'RPI-GXF-UET-VLA',  # 2024-04-30
    'RPJ-CIT-OWL-AKS',  # 2024-05-01
    'NPR-OCI-DYS-ATB',  # 2024-05-02
]

print_best_solutions(PUZZLES[-1])
