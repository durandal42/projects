import collections
import Queue

def separate(input, d):
  # Count input elements:
  counts = collections.Counter(input)

  # Prioritize elements by highest-count.
  eligible = Queue.PriorityQueue()  # Lowest priority element is returned first...
  for item,count in counts.iteritems():
    eligible.put((-count, item))  # ... so use negative counts.

  # Hold currently-ineligible items aside.
  ineligible = Queue.Queue(maxsize=d)

  output = []

  # Output until we can't anymore.
  while not eligible.empty():
    count, item = eligible.get()
    output.append(item)
    ineligible.put((count + 1, item))  # Counts are negative; decrement by adding.
    
    if ineligible.full():  # Oldest ineligible element is eligible now.
      count, item = ineligible.get()
      if count != 0:  # Drop exhausted elements.
        eligible.put((count, item))

  # See if we produced enough output.
  if len(output) < len(input):
    return None  # Got stuck before completing output.

  return output

def verify(input, output, d):
  if collections.Counter(input) != collections.Counter(output):
    return False  # Output not a permutation of input.

  last_seen = {}
  for i,e in enumerate(output):
    if e in last_seen and last_seen[e] > i - d:
      return False  # Collision found.
    last_seen[e] = i

  return True

assert not verify([1,1,1], [1,2,3], 1)
assert not verify([1,2,2], [1,2,2], 2)
assert verify([1,2,2], [2,1,2], 2)

def test(input, d, solveable=True):
  print input,d,'->',
  output = separate(input,d)
  print output
  if solveable:
    assert verify(input, output, d)
  else:
    assert output is None

# Starter examples:
test([1,2,2], 1)
test([1,2,2], 2)
test([1,2,2], 3, False)

# Hint examples:
test([1,2,2,3,3,3,3], 2)
test([1,1,2,2,3,3], 2)
