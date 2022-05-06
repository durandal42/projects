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
  for word in re.sub("[\W_]", ' ', line.lower()).split(' '):
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


def ngram_analysis():
  files = sorted(filter(lambda f: f.endswith(".txt"),
                        os.listdir('wiki-cache')))
  # print(files)
  ns = [1]
  ng = None
  seen_in_articles = collections.Counter()
  for i, f in enumerate(files):
    print("%s/%d\t" % (str(i).zfill(len(str(len(files)))), len(files)), end='')
    words = list(words_from_file('wiki-cache/' + f))
    ng = build_ngrams(words, ns, ng)
    for w in set(words):
      seen_in_articles[w] += 1
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

    
def main():
  files = sorted(filter(lambda f: f.endswith(".txt"),
                        os.listdir('wiki-cache')))#[:10]
  article_word_counts = {}
  for i, f in enumerate(files):
    print("%s/%d\t" % (str(i).zfill(len(str(len(files)))), len(files)), end='')
    words = list(words_from_file('wiki-cache/' + f))
    title = " ".join(words[:5])
    article_word_counts[title] = collections.Counter(words)
            
  while len(article_word_counts) > 1:
    print("There are %d remaining articles." % len(article_word_counts))
    if len(article_word_counts) < 10:
      for title in article_word_counts:
        print(f"\t{title}")
    present = collections.Counter()
    absent = collections.Counter()
    words = set()
    for title, word_counts in article_word_counts.items():
      for word, count in word_counts.items():
        if word in COMMON_WORDS: continue
        if count >= 15:
          present[word] += 1
          words.add(word)
        if count <= 5:
          absent[word] += 1
          words.add(word)

    decisive_words = sorted(
        words, key=lambda w: -1 * present.get(w, 0) * absent.get(w, 0))
    for w in decisive_words[:10]:
      print("%d,%d: %s" % (present[w], absent[w], w))
    dw = input("Select a word, perhaps from the suggestions above: ")
    appears = {'y':True, 'n':False}[input(f"Does {dw} appear 10+ times in the article? [y/n] ")]

    article_word_counts = dict(filter(lambda e: (e[1][dw] >= 10) == appears,
                                      article_word_counts.items()))

  print("Remaining articles: ")
  for title, word_counts in article_word_counts.items():
    print(title)
    for word, count in collections.Counter(word_counts).most_common(50):
      print(f"\t{count}:\t{word}")
        
if __name__ == '__main__':
  main()
