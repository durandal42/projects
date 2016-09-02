import nltk
from nltk.corpus import cmudict 

def nsyl(word, d=cmudict.dict()):
  if word not in d: return None
  return [len(list(y[-1] for y in x if y[-1].isdigit())) for x in d[word.lower()]]

for word in open('TWL06.txt'):
  word = word.lower().strip()
  syl = nsyl(word)
  if syl:
    if syl[0] == 1 and word[-1] == 't':
      print word, syl
