def all_length_n_strings(n, alphabet):
  if n == 0:
    yield ''
  if n > 0:
    for string in all_length_n_strings(n-1, alphabet):
      for a in alphabet:
        yield a + string

for n in range(0,5):
  print "length %d strings:" % n
  for s in all_length_n_strings(n, '01'): print s

def all_strings_from_alphabets(alphabets):
  if not alphabets:
    yield ''
  else:
    for string in all_strings_from_alphabets(alphabets[1:]):
      for a in alphabets[0]:
        yield a + string

print "strings from alphabets"
for s in all_strings_from_alphabets(['01', 'AB', 'xy']): print s
