'''
If I give you a bunch of tuples that represent ranges
They're ints, for simplicity, but you can imagine they represent datetimes or something
They represent times when stuff was happening
And I want you to tell me what time was busiest
Or in the case of a tie, any of the busiest times
When the most things were happening


Q: are the intervals open, closed, half-open?
A: Closed
'''

from collections import deque

def busiest_interval(intervals):
  for start, end in intervals:
    assert start <= end

  start_q = deque(sorted(i[0] for i in intervals))
  end_q = deque(sorted(i[1] for i in intervals))

  best = (0, None)
  current_time, current_business = None, 0
  while start_q and end_q:
    # Closed intervals: if a start and an end happen at the same time, handle the starts first.
    if start_q[0] <= end_q[0]:
      current_time = start_q.popleft()
      current_business += 1
    else:
      current_time = end_q.popleft()
      current_business -= 1
    best = max(best, (current_business, current_time))
  return best[1]

def assertEquals(expected, actual):
  if expected != actual:
    raise AssertionError("expected: %s;\tactual: %s" % (expected, actual))

assertEquals(None, busiest_interval([]))
assertEquals(0, busiest_interval([(0,1)]))
assertEquals(1, busiest_interval([(0,1), (1,2)]))
assertEquals(2, busiest_interval([(0,1), (1,2), (2,3), (1,3)]))
