import wikipedia
import sys
import os
import time
import re
import urllib


def lookup_all(titles):
  for title in titles:
    title = title.strip()
    if not title:
      continue
    wiki_text(title)


LAST_LOOKUP_TIME = None


def wiki_lookup(title):
  title = urllib.parse.unquote(title)
  print("Looking up wikipedia article (live!):", title)
  global LAST_LOOKUP_TIME
  if LAST_LOOKUP_TIME is not None:
    now = time.time()
    must_wait = (LAST_LOOKUP_TIME + 2) - now
    if must_wait > 0:
      print(f"Sleeping {must_wait} seconds to respect wikipedia rate limits.")
      time.sleep(must_wait)
  LAST_LOOKUP_TIME = time.time()
  # results = wikipedia.search(title)
  # print("search results:", results)
  text = wikipedia.page(title, auto_suggest=False).content
  LAST_LOOKUP_TIME = time.time()
  return text


def wiki_text(title):
  # print("Looking up wikipedia article (checking cache first):", title)
  escaped_title = re.sub('[^0-9a-zA-Z ()]', '-', title)
  # if title != escaped_title:
  #   print(title, "->", escaped_title)

  filename = f'wiki-cache/{escaped_title}.txt'
  if os.path.exists(filename):
    # print("reading cached text:", filename)
    return open(filename, "r").read()
  try:
    text = wiki_lookup(title)
  except wikipedia.exceptions.DisambiguationError as err:
    print("need disambiguation for:", title)
    print()
    return None
  except wikipedia.exceptions.PageError as err:
    print("no article found for:", title)
    print()
    return None
  print("writing text to cache:", filename)
  f = open(filename, "w")
  f.write(text)
  return text


if __name__ == '__main__':
  title = " ".join(sys.argv[1:])
  if title:
    print(wiki_text(title))
  else:
    dir_to_scan = 'vitals/vital 10000/'
    # dir_to_scan = 'vitals/'
    files = sorted(filter(lambda f: f.endswith(".txt"),
                          os.listdir(dir_to_scan)))
    for f in files:
      print("looking up titles from:", f)
      lookup_all(open(dir_to_scan + f.strip()))
