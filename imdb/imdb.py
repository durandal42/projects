'''
IMDb Datasets
Subsets of IMDb data are available for access to customers for personal and non-commercial use. You can hold local copies of this data, and it is subject to our terms and conditions. Please refer to the Non-Commercial Licensing and copyright/license and verify compliance.

Data Location

The dataset files can be accessed and downloaded from https://datasets.imdbws.com/. The data is refreshed daily.

IMDb Dataset Details

Each dataset is contained in a gzipped, tab-separated-values (TSV) formatted file in the UTF-8 character set. The first line in each file contains headers that describe what is in each column. A ‘\\N’ is used to denote that a particular field is missing or null for that title/name. The available datasets are as follows:

title.akas.tsv.gz - Contains the following information for titles:

titleId (string) - a tconst, an alphanumeric unique identifier of the title
ordering (integer) – a number to uniquely identify rows for a given titleId
title (string) – the localized title
region (string) - the region for this version of the title
language (string) - the language of the title
types (array) - Enumerated set of attributes for this alternative title. One or more of the following: "alternative", "dvd", "festival", "tv", "video", "working", "original", "imdbDisplay". New values may be added in the future without warning
attributes (array) - Additional terms to describe this alternative title, not enumerated
isOriginalTitle (boolean) – 0: not original title; 1: original title

title.basics.tsv.gz - Contains the following information for titles:
tconst (string) - alphanumeric unique identifier of the title
titleType (string) – the type/format of the title (e.g. movie, short, tvseries, tvepisode, video, etc)
primaryTitle (string) – the more popular title / the title used by the filmmakers on promotional materials at the point of release
originalTitle (string) - original title, in the original language
isAdult (boolean) - 0: non-adult title; 1: adult title
startYear (YYYY) – represents the release year of a title. In the case of TV Series, it is the series start year
endYear (YYYY) – TV Series end year. ‘\\N’ for all other title types
runtimeMinutes – primary runtime of the title, in minutes
genres (string array) – includes up to three genres associated with the title

title.crew.tsv.gz – Contains the director and writer information for all the titles in IMDb. Fields include:
tconst (string) - alphanumeric unique identifier of the title
directors (array of nconsts) - director(s) of the given title
writers (array of nconsts) – writer(s) of the given title

title.episode.tsv.gz – Contains the tv episode information. Fields include:
tconst (string) - alphanumeric identifier of episode
parentTconst (string) - alphanumeric identifier of the parent TV Series
seasonNumber (integer) – season number the episode belongs to
episodeNumber (integer) – episode number of the tconst in the TV series

title.principals.tsv.gz – Contains the principal cast/crew for titles
tconst (string) - alphanumeric unique identifier of the title
ordering (integer) – a number to uniquely identify rows for a given titleId
nconst (string) - alphanumeric unique identifier of the name/person
category (string) - the category of job that person was in
job (string) - the specific job title if applicable, else '\\N'
characters (string) - the name of the character played if applicable, else '\\N'

title.ratings.tsv.gz – Contains the IMDb rating and votes information for titles
tconst (string) - alphanumeric unique identifier of the title
averageRating – weighted average of all the individual user ratings
numVotes - number of votes the title has received

name.basics.tsv.gz – Contains the following information for names:
nconst (string) - alphanumeric unique identifier of the name/person
primaryName (string)– name by which the person is most often credited
birthYear – in YYYY format
deathYear – in YYYY format if applicable, else '\\N'
primaryProfession (array of strings)– the top-3 professions of the person
knownForTitles (array of tconsts) – titles the person is known for
'''

import gzip
import csv
import collections


def load_names():
  f = gzip.open('name.basics.tsv.gz', mode='rt')
  tsv_d_f = csv.DictReader(f, delimiter='\t')

  rows_seen = 0
  next_update = 1
  names = {}
  for row in tsv_d_f:
    rows_seen += 1
    if rows_seen >= next_update:
      print("Loading names; rows seen:", rows_seen)
      next_update *= 2
    names[row['nconst']] = row['primaryName']
    if len(names) > 1000000:
      break
  print("Loaded %d names." % len(names))
  return names


def load_titles():
  f = gzip.open('title.basics.tsv.gz', mode='rt')
  tsv_d_f = csv.DictReader(f, delimiter='\t')

  rows_seen = 0
  next_update = 1
  titles = {}
  for row in tsv_d_f:
    rows_seen += 1
    if rows_seen >= next_update:
      print(f"Loading titles; rows seen: {rows_seen}; movies seen: {len(titles)}")
      next_update *= 2
    if row['titleType'] not in ['movie', 'tvseries']:
      continue
    if row['startYear'] == '\\N' or int(row['startYear']) < 2000:
      continue
    titles[row['tconst']] = row['primaryTitle']
    if len(titles) > 1000000:
      break
  print("Loaded %d titles." % len(titles))
  return titles


def load_ratings():
  f = gzip.open('title.ratings.tsv.gz', mode='rt')
  tsv_d_f = csv.DictReader(f, delimiter='\t')

  rows_seen = 0
  next_update = 1
  ratings = {}
  for row in tsv_d_f:
    rows_seen += 1
    if rows_seen >= next_update:
      print(f"Loading ratings; rows seen: {rows_seen}; titles kept: {len(ratings)}")
      next_update *= 2
    votes = row['numVotes']
    if votes == '\\N' or int(votes) < 1000:
      continue
    ratings[row['tconst']] = votes
    if len(ratings) > 1000000:
      break
  print("Loaded %d ratings." % len(ratings))
  return ratings


def find_frequent_leading_pairs(relevant_titles):
  f = gzip.open('title.principals.tsv.gz', mode='rt')
  tsv_d_f = csv.DictReader(f, delimiter='\t')

  rows_seen = 0
  next_update = 1

  num_appearances = collections.Counter()
  titles = collections.defaultdict(list)
  leads = []
  for row in tsv_d_f:
    rows_seen += 1
    if rows_seen >= next_update:
      print(f"Loading principals; rows seen: {rows_seen}; pairs seen: {len(num_appearances)}")
      next_update *= 2
    if row['tconst'] not in relevant_titles:
      continue
    order = int(row['ordering'])
    if order == 1:
      leads = []
    if row['category'] not in ['actor', 'actress']:
      continue
    leads.append(row['nconst'])
    if len(leads) == 2:
      p = tuple(sorted(leads))
      num_appearances[p] += 1
      titles[p].append(row['tconst'])
    if len(titles) > 1000000:
      break
  print(f"Loaded principals from {len(titles)} movies.")
  return [(p, titles[p])
          for p, c in num_appearances.most_common(10)]


def gzip_demo():
  f = gzip.open('title.principals.tsv.gz', mode='rt')
  # tsv_f = csv.reader(f, delimiter='\t')
  # for line in tsv_f:
  #   print(line)
  tsv_d_f = csv.DictReader(f, delimiter='\t')
  for row in tsv_d_f:
    print(row)


if __name__ == '__main__':
  ratings_d = load_ratings()
  title_d = load_titles()
  relevant_titles = title_d.keys() & ratings_d.keys()
  print(f"Kept {len(relevant_titles)} relevant movies.")

  flp = find_frequent_leading_pairs(relevant_titles)
  name_d = load_names()
  for p, titles in flp:
    a1, a2 = p
    a1, a2 = name_d.get(a1, a1), name_d.get(a2, a2)
    print(f"{a1} + {a2} appeared in {len(titles)} title(s):")
    for t in titles[:10]:
      print("\t", title_d.get(t, t))
