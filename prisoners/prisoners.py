NUM_PRISONERS = 100

import random

def prepare_boxes():
  result = list(range(NUM_PRISONERS))
  random.shuffle(result)
  return result

def open_random(prisoner):
  for box in random.sample(range(NUM_PRISONERS), NUM_PRISONERS/2):
    yield box

def open_pointer(prisoner):
  last_box_contents = None
  for _ in range(NUM_PRISONERS/2):
    if last_box_contents is None:
      last_box_contents = yield prisoner
    else:
      last_box_contents = yield last_box_contents
    
def apply_strategy(boxes, strategy):
  # print 'applying strategy %s' % strategy
  for prisoner in range(NUM_PRISONERS):
    # print 'prisoner %d\'s turn:' % prisoner
    opener = strategy(prisoner)
    found = False
    opened_box = None
    for _ in range(NUM_PRISONERS/2):
      if opened_box is None:
        opened_box = opener.send(None)
      else:
        opened_box = opener.send(boxes[opened_box])
      # print 'opened box %d -> %d' % (opened_box, boxes[opened_box])
      if boxes[opened_box] == prisoner:
        # print 'prisoner found self! strategy can continue.'
        found = True
        break
    if not found:
      # print 'prisoner did not find self. strategy fails. :('
      return False
  # print 'all prisoners found selves. strategy succeeds! :)'
  return True

def run_once(strategy):
  boxes = prepare_boxes()
  return apply_strategy(boxes, s)

def run(iterations=10000):
  strategies = [open_random, open_pointer]
  num_successes_by_strategy = [0] * len(strategies)
  for _ in range(iterations):
    boxes = prepare_boxes()
    # print 'boxes:', boxes
    for i,s in enumerate(strategies):
      if apply_strategy(boxes, s):
        num_successes_by_strategy[i] += 1
      
  for i,s in enumerate(strategies):
    num_successes = num_successes_by_strategy[i]
    print "%s:\t%f (%d/%d)" % (s, float(num_successes) / float(iterations),
                               num_successes, iterations)

run()
