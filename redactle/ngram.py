import collections
import re
import itertools
import os
import functools
import multiprocessing
import heapq
import pickle
import unicodedata
from statsmodels.stats.weightstats import DescrStatsW

COMMON_WORDS = set(['a', 'aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'an', 'and', 'around', 'as', 'at', 'because', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'following', 'for', 'from', 'if', 'in', 'inside', 'into', 'is', 'it', 'like', 'minus', 'near', 'next', 'of', 'off', 'on', 'onto', 'opposite', 'or', 'out', 'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'the', 'through', 'till', 'to', 'toward', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'was', 'with', 'within', 'without'])

def normalize(s):
  return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()


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
      for w in re.split(r"(\D+)", word):
        if w:
          yield w


def words_from_file(filename):
  print("Loading text from file:", filename)
  for line in open(filename):
    line = normalize(line.strip())
    if "== Further reading ==" in line: break
    if "=== External links ===" in line: break
    if line.startswith("{") and line.endswith("}"): continue
    if len(line) < 3: continue
    for word in words_from_line(line):
      yield word

#for w in words_from_file('wiki-cache/Foam.txt'):
#  print(w, end=' ')

      
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
  awc_pickle_file = "article-word-counts.pickle"
  if os.path.exists(awc_pickle_file):
    print("Loading pickled word counts...")
    article_word_counts = pickle.load(open(awc_pickle_file, "rb"))
  else:
    for i, f in enumerate(files):
      # if i > 10: break
      print("%s/%d\t" % (str(i).zfill(len(str(len(files)))), len(files)), end='')
      words = list(words_from_file('wiki-cache/' + f))
      title = " ".join(words[:5])
      article_word_counts[title] = collections.Counter(words)
    print("Pickling word counts...")
    pickle.dump(article_word_counts, open(awc_pickle_file, "wb"))

  # watchword = 'foam'
    
  THRESHOLD = 10
  MARGIN = 5
  while len(article_word_counts) > 1:
    print("Remaining articles:", len(article_word_counts))
    if len(article_word_counts) < 30:
      for title in article_word_counts:
        print(f"\t{title}")
    present = collections.defaultdict(collections.Counter)
    words = set()
    for title, word_counts in article_word_counts.items():
      #      if watchword in title:
      #        print(f'"{watchword}" is in still-possible title "{title}"')
      #        print("Word counts:", word_counts)
      for word, count in word_counts.items():
        if word in COMMON_WORDS: continue
        present[word][count] += 1
        words.add(word)
    print("Number of words appearing in remaining articles:", len(words))
        
    buckets = {}
    for word in words:
      buckets[word] = len(present[word]) + 1
        
    decisive_words = heapq.nlargest(10, words, key=lambda w: buckets[w])
    for w in decisive_words:
      print("%d: %s" % (buckets[w], w))
    dw = input("Select a word, perhaps from the suggestions above: ").strip()
    appears = int(input(f"How many times does {dw} appear in the article? "))

    threshold = max(1, appears/5)
    article_word_counts = dict(filter(lambda e: abs(e[1][dw] - appears) < threshold,
                                      article_word_counts.items()))

  print("Remaining articles: ")
  for title, word_counts in article_word_counts.items():
    print(title)
    for word, count in collections.Counter(word_counts).most_common(50):
      print(f"\t{count}:\t{word}")
        
if __name__ == '__main__':
  main()
