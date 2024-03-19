import wikipedia
import sys
import os
import time
import re
import urllib
import unicodedata

def normalize(s):
  return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()


def lookup_all(titles):
  for title in titles:
    title = title.strip()
    if not title:
      continue
    wiki_text(title)


LAST_LOOKUP_TIME = None

def rate_limit():
  global LAST_LOOKUP_TIME
  if LAST_LOOKUP_TIME is not None:
    now = time.time()
    must_wait = (LAST_LOOKUP_TIME + 2) - now
    if must_wait > 0:
      print(f"Sleeping {must_wait} seconds to respect wikipedia rate limits.")
      time.sleep(must_wait)
  LAST_LOOKUP_TIME = time.time()

def wiki_lookup(title):
  title = urllib.parse.unquote(title)
  print("Looking up wikipedia article (live!):", title)
  rate_limit()
  text = wikipedia.page(title, auto_suggest=False).content
  LAST_LOOKUP_TIME = time.time()
  return text


def wiki_links(title):
  title = urllib.parse.unquote(title)
  print("Looking up links from wikipedia article (live!):", title)
  rate_limit()
  links = wikipedia.page(title, auto_suggest=False).links
  LAST_LOOKUP_TIME = time.time()
  return links


def wiki_text(title):
  # print("Looking up wikipedia article (checking cache first):", title)
  escaped_title = re.sub('[^0-9a-zA-Z ()]', '-', normalize(title))
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


def scrape_from_article_dir(dir_to_scan='vitals/vital 10000/'):
  files = sorted(filter(lambda f: f.endswith(".txt"),
                        os.listdir(dir_to_scan)))
  for f in files:
    print("looking up titles from:", f)
    lookup_all(open(dir_to_scan + f.strip()))


def scrape_from_article(title):
  links = wiki_links(title)
  print("Looking up %d links..." % len(links))
  for link in links:
    wiki_text(link)
  
    
if __name__ == '__main__':
  title = " ".join(sys.argv[1:])
  if title:
    print(wiki_text(title))
    # print(wiki_links(title))
  else:
    vital4_categories = [
      "Wikipedia:Vital_articles/Level/4/People",
      "Wikipedia:Vital_articles/Level/4/History",
      "Wikipedia:Vital_articles/Level/4/Geography",
      "Wikipedia:Vital_articles/Level/4/Arts",
      "Wikipedia:Vital_articles/Level/4/Philosophy_and_religion",
      "Wikipedia:Vital_articles/Level/4/Everyday_life",
      "Wikipedia:Vital_articles/Level/4/Society_and_social_sciences",
      "Wikipedia:Vital_articles/Level/4/Biology_and_health_sciences",
      "Wikipedia:Vital_articles/Level/4/Physical_sciences",
      "Wikipedia:Vital_articles/Level/4/Technology",
      "Wikipedia:Vital_articles/Level/4/Mathematics",
      ]
    vital5_categories = [
      "Wikipedia:Vital_articles/Level/5/Arts",
      "Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Animals",
      "Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Biology",
      "Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Health",
      "Wikipedia:Vital_articles/Level/5/Biological_and_health_sciences/Plants",
      "Wikipedia:Vital_articles/Level/5/Everyday_life",
      "Wikipedia:Vital_articles/Level/5/Everyday_life/Sports,_games_and_recreation",
      "Wikipedia:Vital_articles/Level/5/Geography/Cities",
      "Wikipedia:Vital_articles/Level/5/Geography/Countries",
      "Wikipedia:Vital_articles/Level/5/Geography/Physical",
      "Wikipedia:Vital_articles/Level/5/History",
      "Wikipedia:Vital_articles/Level/5/Mathematics",
      "Wikipedia:Vital_articles/Level/5/People/Artists,_musicians,_and_composers",
      "Wikipedia:Vital_articles/Level/5/People/Entertainers,_directors,_producers,_and_screenwriters",
      "Wikipedia:Vital_articles/Level/5/People/Military_personnel,_revolutionaries,_and_activists",
      "Wikipedia:Vital_articles/Level/5/People/Miscellaneous",
      "Wikipedia:Vital_articles/Level/5/People/Philosophers,_historians,_political_and_social_scientists",
      "Wikipedia:Vital_articles/Level/5/People/Politicians_and_leaders",
      "Wikipedia:Vital_articles/Level/5/People/Religious_figures",
      "Wikipedia:Vital_articles/Level/5/People/Scientists,_inventors,_and_mathematicians",
      "Wikipedia:Vital_articles/Level/5/People/Sports_figures",
      "Wikipedia:Vital_articles/Level/5/People/Writers_and_journalists",
      "Wikipedia:Vital_articles/Level/5/Philosophy_and_religion",
      "Wikipedia:Vital_articles/Level/5/Physical_sciences/Astronomy",
      "Wikipedia:Vital_articles/Level/5/Physical_sciences/Basics_and_measurement",
      "Wikipedia:Vital_articles/Level/5/Physical_sciences/Chemistry",
      "Wikipedia:Vital_articles/Level/5/Physical_sciences/Earth_science",
      "Wikipedia:Vital_articles/Level/5/Physical_sciences/Physics",
      "Wikipedia:Vital_articles/Level/5/Society_and_social_sciences/Culture",
      "Wikipedia:Vital_articles/Level/5/Society_and_social_sciences/Politic_and_economic",
      "Wikipedia:Vital_articles/Level/5/Society_and_social_sciences/Social_studies",
      "Wikipedia:Vital_articles/Level/5/Technology",
      ]
    for c in vital5_categories:
      scrape_from_article(c)
