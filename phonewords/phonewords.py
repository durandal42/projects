import collections
import itertools

WORDS = set(line.strip().upper() for line in open('/usr/share/dict/words'))
BUTTONS = {            '2':'ABC', '3':'DEF',
           '4':'GHI',  '5':'JKL', '6':'MNO',
           '7':'PQRS', '8':'TUV', '9':'WXYZ'}

NUMBER = '2476'

def phonewords(number, buttons, dictionary, prefix=''):
  if not number:  # no more digits to append; check for wordiness
    if prefix in dictionary: yield prefix
    return
  for letter in buttons[number[0]]:
    for word in phonewords(number[1:], buttons, dictionary, prefix+letter):
      yield word

# uncached result:
print [word for word in phonewords(NUMBER, BUTTONS, WORDS)]


def phonewords_simple(number, buttons, dictionary):
  words = ['']
  for digit in number:
    words = [word + letter for word in words for letter in buttons[digit]]
  words = filter(lambda w: w in dictionary, words)
  return words

print phonewords_simple(NUMBER, BUTTONS, WORDS)


def phonewords_queue(number, buttons, dictionary):
  words = ['']
  while words:
    word = words.pop()
    if len(word) == len(number):
      if word in dictionary:
        yield word
    else:
      for letter in buttons[number[len(word)]]:
        words.append(word + letter)

print [word for word in phonewords_queue(NUMBER, BUTTONS, WORDS)]


def phonewords_counting(number, buttons, dictionary):
  count = [0] * len(number)  # count in variable-base
  while True:
    word = ''.join(buttons[digit][choice] for digit,choice in zip(number, count))
    if word in dictionary: yield word

    # add one to the count:
    for i in itertools.count():
      if i == len(number): return  # carried off the end of the range
      count[i] += 1  # add one to this place
      if count[i] < len(buttons[number[i]]):
        break  # no carry
      else:
        count[i] = 0  # carry

print [word for word in phonewords_counting(NUMBER, BUTTONS, WORDS)]



def all_phonewords(buttons, dictionary):
  reverse_buttons = collections.defaultdict(str)
  for digit, letters in buttons.iteritems():
    for letter in letters:
      reverse_buttons[letter] = digit
  
  phonewords = collections.defaultdict(list)
  for word in dictionary:
    number = ''.join(reverse_buttons[letter] for letter in word)
    phonewords[number].append(word)
  
  return phonewords

ALL_PHONEWORDS = all_phonewords(BUTTONS, WORDS)

# cached result:
print ALL_PHONEWORDS[NUMBER]


# curiosity: which numbers of each length map onto the most possible words?
for length in range(1, max(len(number) for number in ALL_PHONEWORDS)):
  print length, max((len(words), number, words)
                    for number, words in ALL_PHONEWORDS.iteritems()
                    if len(number) == length)
