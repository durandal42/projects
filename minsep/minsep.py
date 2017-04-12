import collections
import Queue

# Canonical Map+Heap+Queue implementation.
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

# Fancy O(N) implementation using inverted map.
def separate_linear(input, d):
  # Basic map of counts:
  counts = collections.Counter(input)

  # Inverted map of count:[items]
  inverted_map = collections.defaultdict(Queue.Queue)
  for item,count in counts.iteritems():
    inverted_map[count].put(item)

  # Distinct counts of elements, sorted ascending:
  distinct_counts = sorted(inverted_map.keys())

  output = []
  while True:
    # Pop top k by count from inverted map.
    batch = []
    while len(batch) < d and inverted_map:
      max_count = distinct_counts[-1]  # Max count is always at the end of distinct_counts
      item = inverted_map[max_count].get(block=False)
      batch.append(item)
      counts[item] -= 1

      # We might have exhausted the queue of elements which had this count.
      if inverted_map[max_count].empty():
        del inverted_map[max_count]
        distinct_counts.pop()

    output += batch

    # We might be done:
    if len(output) == len(input): return output
    # If we're not done, we might be stuck:
    if len(batch) < d: return None

    # If we're not done and not stuck, we have more work to do.
    # Push batched elements back into map, with new counts.
    new_counts = []
    for item in batch:
      if counts[item] == 0: continue
      if counts[item] not in inverted_map:
        new_counts.append(counts[item])
      # Elements returned to their per-count queues in the same order we got them out!
      inverted_map[counts[item]].put(item)

    # new_counts is now in descending order, and the lowest might be one lower than the highest remaining in distinct_counts.
    # In other words, distinct_counts + reversed(new_counts) is very nearly sorted, but the middle two elements might be out of order.
    # ... so tidy up those two elements before appending!
    if distinct_counts and new_counts and distinct_counts[-1] > new_counts[-1]:
      distinct_counts[-1], new_counts[-1] = new_counts[-1], distinct_counts[-1]
    # ... and then append.
    distinct_counts += reversed(new_counts)

    # All of this bookeeping was to avoid sorting the entire keyset again; check that it worked.
    # assert distinct_counts == sorted(inverted_map.keys())  # ... only if we're debugging though :)

# "Functional" implementation which never mutates anything.
# Instead, copy our entire state into the recursive call, and then blow our recursion limit. Wheee!
def separate_functional(input, d):
  return separate_functional_helper(collections.Counter(input), d, [])
def separate_functional_helper(remaining_counts, d, output_so_far):
  # "base case"
  if remaining_counts == {}: return output_so_far
  
  # All currently-eligible elements, and their remaining counts, sorted by remaining count (descending):
  eligible = sorted([(count,item) for item,count in remaining_counts.iteritems()], reverse=True)
  # Just the top d elemnts, still sorted by remaining count (descending):
  chosen = [item for count,item in eligible[:d]]

  new_counts = remaining_counts - collections.Counter(chosen)

  if len(chosen) < d and new_counts != {}:
    return None  # Partial batch, and elements still remain; we're stuck.

  # Recursive call! Too bad Python's not tail-recursive...
  return separate_functional_helper(new_counts, d, output_so_far + chosen) 

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

def test(f, input, d, solveable=True):
  print input,d,'->',
  output = f(input,d)
  print output
  if solveable:
    assert verify(input, output, d)
  else:
    assert output is None

for f in [separate, separate_linear, separate_functional]:
  # Starter examples:
  test(f, [1,2,2], 1)
  test(f, [1,2,2], 2)
  test(f, [1,2,2], 3, solveable=False)

  # Hint examples:
  test(f, [1,2,2,3,3,3,3], 2)
  test(f, [1,1,2,2,3,3], 2)

  test(f, [1,1,2,2,3,3], 3)

  # Tail-recursion test:
  #test(f, [1,2]*1000, 2)
