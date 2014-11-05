import re
import collections
import sys
import heapq

def snippet(query, text):
  snippet = snippet_from_locations([i[0] for i in tokenize(query)], tokenize(text))

  if not snippet: return None
  return text[snippet[0]:snippet[1]]

def snippet_via_index(query, text):
  query_words = [i[0] for i in tokenize(query)]

  index = create_index(text)
  query_specific_index = {}
  for word in query_words:
    query_specific_index[word] = index[word]

  snippet = snippet_from_locations(query_words, [i for i in merge_indices(query_specific_index)])

  if not snippet: return None
  return text[snippet[0]:snippet[1]]


def create_index(text):
  index = collections.defaultdict(list)
  for word, location in tokenize(text):
    index[word].append(location)
  return index

def tokenize(s):
  return [(m.group(0), m.start()) for m in re.finditer(r"\w+", s.lower())]

def merge_indices(word_indices):
  h = [(locations[0], word, locations[1:]) for word, locations in word_indices.iteritems()]
  heapq.heapify(h)
  while h:
    next_location, word, remaining_locations = heapq.heappop(h)
    yield (word, next_location)
    if remaining_locations:
      heapq.heappush(h, (remaining_locations[0], word, remaining_locations[1:]))

def length(snippet):
  if snippet is None: return sys.maxint
  if len(snippet) == 0: return 0
  return snippet[-1][1] - snippet[0][1] + len(snippet[-1][0])

def snippet_from_locations(query_words, text_word_locations):
  needed_word_count = collections.defaultdict(int)
  for word in query_words:
    needed_word_count[word] += 1
  unsatisfied_words = len(needed_word_count)

  best_snippet = None
  current_snippet = []
  locations_start, locations_end = 0, 0
  snippet_start, snippet_end = 0, 0
  while locations_end < len(text_word_locations) or not unsatisfied_words:
    if not unsatisfied_words:
      removed_word, location = text_word_locations[locations_start]
      locations_start += 1
      current_snippet = current_snippet[1:]
      if removed_word in needed_word_count:
        needed_word_count[removed_word] += 1
        if needed_word_count[removed_word] == 1:
          unsatisfied_words += 1
    else:
      added_word, location = text_word_locations[locations_end]      
      locations_end += 1    
      current_snippet.append((added_word, location))
      if added_word in needed_word_count:
        needed_word_count[added_word] -= 1
        if needed_word_count[added_word] == 0:
          unsatisfied_words -= 1
    if not unsatisfied_words and length(current_snippet) < length(best_snippet):
        best_snippet = current_snippet

  if not best_snippet: return None
  return best_snippet[0][1], best_snippet[-1][1] + len(best_snippet[-1][0])

print 'expected: page in the results needs a short snippet'
print 'actual:', snippet_via_index('snippet page',
                         '''Say you're a search engine, and you're serving search results for a
                  given query. Each page in the results needs a short snippet; a
                  paragraph or so of text from the document. You'd like this snippet to
                  be as short as possible while still containing (in any order) all the
                  words from the query. page supercalifragilisticexpialidocious snippet''')


