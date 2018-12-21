import collections
import itertools
import operator

def reduce_word(w):
  return ''.join(c for c in w if c not in 'aeiou')

def load_words(filename):
  print 'loading words...',
  words = set(line.lower().strip() for line in open(filename))
  print 'loaded %d words.' % len(words)
  return words

def reduce_words(words):
  reduced_words = collections.defaultdict(list)
  for w in words:
    reduced_word = reduce_word(w)
    if reduced_word == '': continue
    # if len(reduced_word) < 2: continue  # skip unfunny single-consonant words
    reduced_words[reduced_word].append(w)
  print '... which reduce into %d distinct consonant bones.' % len(reduced_words)

  return reduced_words

def alternate_reduction_skeleton(reduced_target, reduced_words):
  for reduced_word, words in reduced_words.iteritems():
    if not reduced_target.startswith(reduced_word): continue
    remaining_reduced_target = reduced_target[len(reduced_word):]
    if remaining_reduced_target == '': yield [reduced_word]
    else:
      for phrase in alternate_reduction_skeleton(remaining_reduced_target, reduced_words):
        yield [reduced_word] + phrase

def load_word_ranks():
  combined_word_freqs = collections.Counter()
  print 'loading word frequencies...'
  for line in itertools.chain(itertools.islice(open('../parlance/words.txt'), 1, None),
                              itertools.islice(open('../parlance/words2.txt'), 1, None),
                              ):
    rank, word, _, freq, _ = (word.strip() for word in line.strip().split('\t'))
    if not rank or not freq:
      # print line
      continue
    combined_word_freqs[word] += int(freq)
  print 'loading frequencies for %d words.' % len(combined_word_freqs)
  print 'top 10:', combined_word_freqs.most_common(10)

  word_ranks = {}
  for i,(word,freq) in enumerate(combined_word_freqs.most_common()):
    word_ranks[word] = i
  return word_ranks

def score(partition, word_ranks, reduced_words):
  # score by commonly-used:
  # score = 1
  # for w in partition:
  #   score *= word_ranks[w]

  # score by length
  # score = len('.'.join(partition))

  # score by fanout:
  score = 1
  for w in partition:
    score *= len(reduced_words[w])

  return score

def analyze(target, reduced_words):
  reduced_target = reduce_word(target)
  print target, '->', reduced_target

  skeletons = {}
  bones = {}
  for i, skeleton in enumerate(alternate_reduction_skeleton(reduced_target, reduced_words)):
    for bone in skeleton:
      bones[bone] = len(reduced_words[bone])
    phrases_from_skeleton = reduce(operator.mul, (len(reduced_words[bone]) for bone in skeleton), 1)
    # print i, skeleton, phrases_from_skeleton
    skeletons['.'.join(skeleton)] = phrases_from_skeleton
  print 'skeletons by number of flesh options:'
  for skeleton, num_flesh_options in sorted(skeletons.iteritems(), key=operator.itemgetter(1)):
    print '\t%s : %d' % (skeleton, num_flesh_options)

  print 'total phrases:', sum(fanout for skeleton,fanout in skeletons.iteritems())
  print 'bones by number of flesh options:'
  for bone, num_flesh_options in sorted(bones.iteritems(), key=operator.itemgetter(1)):
    print '\t%s : %d' % (bone, num_flesh_options)
  for bone, num_flesh_options in sorted(bones.iteritems()):
    print 'flesh options (%d) for bone: %s' % (num_flesh_options, bone)
    for word in sorted(reduced_words[bone]):
      print '\t', word


#analyze('durandal')

import sys
if len(sys.argv) < 2:
  print 'usage: python direnoodle.py <target>'
else:
  # reduced_words = reduce_words(load_words('/usr/share/dict/words'))
  reduced_words = reduce_words(load_words('../alphabears/TWL06.txt'))
  # word_ranks = load_word_ranks()
  # reduced_words = reduce_words(word_ranks.keys())

  analyze(sys.argv[1], reduced_words)
