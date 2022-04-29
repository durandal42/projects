import collections
import re
import itertools
import os
import functools
import multiprocessing
import heapq


COMMON_WORDS = set(['a', 'aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'an', 'and', 'around', 'as', 'at', 'because', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'following', 'for', 'from', 'if', 'in', 'inside', 'into', 'is', 'it', 'like', 'minus', 'near', 'next', 'of', 'off', 'on', 'onto', 'opposite', 'or', 'out', 'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'the', 'through', 'till', 'to', 'toward', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'was', 'with', 'within', 'without'])

def build_ngrams(text, ns, ng=None):
  if ng is None:
    ng = collections.defaultdict(collections.Counter)
  pasts = [()] * len(ns)
  for word in text:
    for i, past_n in enumerate(zip(pasts, ns)):
      past, n = past_n
      if len(past) == n:
        ng[past][word] += 1
        past = past[1:]
      pasts[i] = past + (word,)
  return ng


def words_from_line(line):
  for word in re.sub("[^a-z0-9_']", ' ', line.lower()).split(' '):
    if word:
      yield word


def words_from_file(filename):
  print("Loading text from file:", filename)
  for line in open(filename):
    for word in words_from_line(line):
      yield word


def get_past_from_user():
  input_string = input(f'past words: ')
  past = tuple(words_from_line(input_string))
  return past


def predict_next_word(ng, past):
  total = sum(y[1] for y in ng[past].items())
  print("total appearance count:", total)
  top_guesses = ng[past].most_common(10)
  for k, v in top_guesses:
    width = int(100 * v / total)
    print("\t", k,
          " " * (10 - len(k)),
          "*" * width,
          " " * (100 - width),
          )
  if top_guesses:
    return top_guesses[0][0]


def input_loop(ng):
  while True:
    past = get_past_from_user()
    predict_next_word(ng, past)


def main():
  files = sorted(filter(lambda f: f.endswith(".txt"),
                        os.listdir('wiki-cache')))
  # print(files)
  ns = [1]
  ng = None
  for i, f in enumerate(files):
    print("%s/%d\t" % (str(i).zfill(len(str(len(files)))), len(files)), end='')
    ng = build_ngrams(words_from_file('wiki-cache/' + f), ns, ng)
  print("Size of ngram corpus:", len(ng))
  for n in ns:
    print(f"Most common ngrams of length {n}:")
    for count,past in heapq.nlargest(100,
        map(lambda kv: (sum(y[1] for y in kv[1].items()), kv[0]),
          filter(lambda kv: len(kv[0]) == n,
                   ng.items()))):
      past = " ".join(past)
      prefix = ""
      if past in COMMON_WORDS:
        prefix = " *"
      print(prefix, "\t", count,":", past)
  # print(ng)
  input_loop(ng)


if __name__ == '__main__':
  main()
