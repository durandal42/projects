ranks = {}

rank = 0
print('Loading word ranks...')
for line in open('en_full.txt'):
  tokens = line.split(' ')
  word, frequency = tokens[0], int(tokens[1])
  if len(word) != 5:
    continue
  ranks[word.upper()] = rank
  rank += 1

print('loaded %d 5-letter words' % len(ranks))

for word in open('legal-targets.txt'):
  word = word.strip().upper()
  f = ranks[word]
  print(f'{word}\t{f}\tTARGET')

for word in open('legal-guesses.txt'):
  word = word.strip().upper()
  if word in ranks:
    f = ranks[word]
  else:
    # print(f'Word not found in frequency data: {word}')
    f = float('inf')
  print(f'{word}\t{f}\tGUESS')
