from utils import count

def count_fancy(word, board_status):
  result = {}
  for letter,tile_status in zip(word, board_status):
    if letter not in result: result[letter] = []
    result[letter].append(score_tile(int(tile_status)))
  return result

def is_subset(needle, haystack):
  for k,v in needle.iteritems():
    if k not in haystack or v > len(haystack[k]): return False
  return True

def score_tile(raw_score):
  return {0:1, 1:10, 2:5, 3:1, 4:1}[raw_score]

def score_play(word, available):
  available = available.copy()
  result = 0
  for letter in word:
    result += available[letter][0]
    available[letter] = available[letter][1:]
  return result

print 'loading words...'
words = [line.strip().upper() for line in open('TWL06.txt')]
print 'done.'


'''
Looks like this expects you to tell it who owns each tile, after loading the board.
TODO(durandal): document this?
'''
import sys
board = None
while True:
  print '$ ',
  line = sys.stdin.readline()
  if not line: break
  line = line.strip()
  if line[0] is '`':
    board = open('games/%s.txt' % line[1:]).readline().strip().upper()
    print '"%s"' % board
    continue
  available = count_fancy(board,line)
  for k,v in available.iteritems():
    available[k].sort()
    available[k].reverse()
  print available
  legal = [(score_play(word,available), word) for word in words if is_subset(count(word), available)]
  if len(legal) == 0: print 'no legal moves'
  for score,word in sorted(legal):
    print score,word
