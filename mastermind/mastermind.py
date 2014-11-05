import random
import collections

WORD_LENGTH = 5

def load_words():
    legal_words = []
    print 'loading words...',
    for word in open('wordList.txt'): # 'TWL06.txt'):
        word = word.strip().upper()
        if len(word) != WORD_LENGTH: continue
        if max(count(word).values()) > 1: continue
        legal_words.append(word)
    print 'finished loading', len(legal_words), 'legal words.'
    return legal_words

def count(list):
    result = collections.defaultdict(int)
    for element in list:
        result[element] += 1
    return result

def auto_scorer(guess, target, r=range(WORD_LENGTH)):
    guess_count = count(guess)
    target_count = count(target)
    correct_letters = sum([min(guess_count[k], target_count[k])
                           for k in guess_count if k in target_count])

    correct_locations = sum([1 for i in r if guess[i] == target[i]])

    return correct_letters, correct_locations

def no_dupes_scorer(guess, target, r=range(WORD_LENGTH)):
    letters,locations = 0,0
#    for i,guess_letter in enumerate(guess):
#        for j,target_letter in enumerate(target):
    for i in r:
        guess_letter = guess[i]
        for j in r:
            target_letter = target[j]
            if guess_letter == target_letter:
                letters += 1
                if i == j:
                    locations += 1
    return letters, locations

def user_scorer(word, target):
    tokens = raw_input('score %s, please: ' % word).strip().split(' ')
    return int(tokens[0]), int(tokens[1])

def user_choice(prev_guess, prev_score):
    if prev_guess:
        print 'score for guess "%s": %s' % (prev_guess, prev_score)
    return raw_input('guess a word: ').strip().upper()

global all_words
all_words = load_words()
global remaining_targets
remaining_targets = all_words[:]
def random_choice(prev_guesses=None, prev_scores=None):
    guess = random.choice([w for w in remaining_targets])
    print guess, '(randomly chosen)'
    return guess

def restrict(targets, prev_guess, prev_score, scorer=no_dupes_scorer):
    return [w for w in targets if scorer(prev_guess, w) == prev_score]

def restrict_targets(prev_guess, prev_score, scorer=no_dupes_scorer):
    if prev_guess:
        global remaining_targets
        remaining_targets = restrict(remaining_targets, prev_guess, prev_score, scorer)
#        print 'still %d potential targets remaining' % len(remaining_targets)    

def random_restricted_choice(prev_guesses, prev_scores):
    restrict_targets(prev_guesses[-1], prev_score[-1])
    return random_choice()

if WORD_LENGTH == 5:
    cache = {
        ():  ('HARES', 922),
        (0, 0):('DUNGY', 54),
        (1, 0):('ALONE', 158),
        (1, 1):('COINS', 112),
        (2, 0):('SCALE', 162),
        (2, 1):('DOATS', 151),
        (2, 2):('AILED', 107),
        (3, 0):('TRADE', 49),
        (3, 1):('TRIMS', 63),
        (3, 2):('COPER', 49),
        (3, 3):('NORTH', 57),
        (4, 0):('CRAKE', 8),
        (4, 1):('BEARD', 9),
        (4, 2):('SAVOR', 7),
        (4, 3):('ALTER', 8),
        (4, 4):('BIRTH', 8),
        }
cache = {
    ():  ('HARES', 922),
}
def conservative_restricted_choice(prev_guesses, prev_scores, scorer=auto_scorer):
    prev_guess = prev_guesses and prev_guesses[-1] or None
    prev_score = prev_scores and prev_scores[-1] or None
    if prev_guess and prev_score:
        restrict_targets(prev_guess, prev_score, scorer)
    else:
        global remaining_targets
        remaining_targets = all_words[:]

    print '%d possible targets remain' % len(remaining_targets)

    cache_key = ()
    for score in prev_scores:
        cache_key = cache_key + score
    if cache_key in cache:
        print '(precomputed) worst case for guess %s: %d remaining possibilities' % cache[cache_key]
        return cache[cache_key][0]

    if len(remaining_targets) <= 2:
        print 'remaining targets down to %s; guessing %s' % (remaining_targets, remaining_targets[0])
        return remaining_targets[0]
    worst_case_by_guess = {}
    best_worst_case_so_far = len(remaining_targets)
    for guess in remaining_targets: # sorted(all_words):
        score_counts = collections.defaultdict(int)
        for target in remaining_targets:
            score = scorer(guess, target)
            score_counts[score] += 1
            if score_counts[score] > best_worst_case_so_far:
#                print 'potential guess %s has large bucket %s, with %d possibilities' % (
#                    guess, score, score_counts[score])
                break
        else:
            worst_score, worst_case = max(score_counts.iteritems(), key=lambda x:x[1])
            worst_case_by_guess[guess] = worst_case
            best_worst_case_so_far = min(best_worst_case_so_far, worst_case)
#            print 'potential guess %s has largest bucket %s, with %d possibilities' % (
#                guess, worst_score, worst_case)
    best_guess,best_worst_case = min(worst_case_by_guess.iteritems(), key=lambda x:x[1])
    print 'worst case for guess %s: %d remaining possibilities' % (best_guess, best_worst_case)
#    print 'updating cache: %s:%s' % (cache_key, (best_guess, best_worst_case))
#    cache[cache_key] = (best_guess, best_worst_case)
    return best_guess

def random_target():
    target = random.choice([w for w in all_words])
    print 'spoiler: the target word is %s' % target
    return target

def user_target():
    return raw_input('choose a target: ').strip().upper()

def no_target():
    return None

def play(targeter=random_target, guesser=user_choice, scorer=no_dupes_scorer):
    target = targeter()

    num_guesses = 0
    guesses = []
    scores = []
    while not scores or scores[-1] != (WORD_LENGTH,WORD_LENGTH):
        guesses.append(guesser(guesses, scores))
        num_guesses += 1
        scores.append(scorer(guesses[-1], target))
    print 'it took you %d guesses' % num_guesses
    return num_guesses


def human_guesser(): play(targeter=random_target, guesser=user_choice)
def ai_guesser(): play(targeter=no_target, guesser=conservative_restricted_choice, scorer=user_score)
def test_mode(): play(targeter=user_target, guesser=conservative_restricted_choice)
def random_test_mode(): play(targeter=random_target, guesser=conservative_restricted_choice)
#ai_guesser()
#test_mode()

def solve_everything():
    meta_score = collections.defaultdict(int)
    for word in sorted(all_words)[:10]:
        print word
        guesses_needed = play(targeter=lambda: word, guesser=conservative_restricted_choice)
        meta_score[guesses_needed] += 1
    print sorted(meta_score.iteritems())

#solve_everything()
import cProfile
if __name__ == '__main__':
    cProfile.run('solve_everything()', 'solve_everything_profile')

#print auto_scorer('xxxxx', '00x00'), auto_scorer('00x00','xxxxx')
