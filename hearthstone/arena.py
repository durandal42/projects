import random
import collections

def new_challenger():
  return (0,0)

def finished(player):
  return player[0] >= 12 or player[1] >= 3

def play_round(pop):
  pop.sort()
  for i in range(0, len(pop), 2):
    pop[i], pop[i+1] = play_game(pop[i], pop[i+1])

def play_game(p1, p2):
  if random.choice([True, False]):
    return (p1[0]+1, p1[1]), (p2[0], p2[1]+1)
  else:
    return (p1[0], p1[1]+1), (p2[0]+1, p2[1])

def replace_players(pop):
  for i,p in enumerate(pop):
    if finished(p):
      report(p)
      pop[i] = new_challenger()

histogram = collections.defaultdict(int)
def report(player):
  # print 'finished:', player
  histogram[player] += 1

POP_SIZE = 10000
ROUNDS = 1000

population = [new_challenger() for i in range(POP_SIZE)]
for i in range(ROUNDS):
  #print population
  play_round(population)
  replace_players(population)

print '%d players completed their runs' % sum(histogram.values())
for score in sorted(histogram.keys()):
  print score, histogram[score]
