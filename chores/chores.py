import itertools
import collections
import random

NUM_ROOMMATES = 5

'''
In a chore assignment a, a[i] is the roommate assigned to chore[i].
assumption: equally many chores as roommates
assumption: each roommate assigned at most one chore
Therefore, a chore assignment is a permutation of roommate indexes.
'''

def is_valid(a):
    '''Returns whether an assignment obeys whatever validity testing you care to implement.'''
    # chore[0] (Bathroom A) can only be performed by the two roommates who use that bathroom: [0,1]
    # similarly for chore[1] (Bathroom B) and roommates [2,3,4]
    return a[0] in [0,1] and a[1] in [2,3,4]

def all_valid():
    '''Returns a list of all valid chore assignments.'''
    return [a for a in itertools.permutations(range(NUM_ROOMMATES)) if is_valid(a)]

print 'number of valid assignments:\n', len(all_valid())

def times_assigned(assignments, past=None):
    '''
    Counts the number of times each roommate is assigned each chore, over a list of assignments.

    Input:
      assignments: a list of chore assignments
      past (optional): an existing frequency report, to be appended to.
    Output:
      a list of lists of ints; such that result[r][c] is the number of times roommate[r] was assigned to chore[c]
    '''
    if past is None:
        past = [[0]*NUM_ROOMMATES for i in range(NUM_ROOMMATES)]
    for a in assignments:
        for c,r in enumerate(a):
            past[r][c] += 1
    return past

print 'total workload over all valid assignments:\n', times_assigned(all_valid())

def score(assignment, past):
    '''Scores an assignment, given past assignment distribution as context.'''
    # Penalize assigning chores to roommates who have done them a lot already.
    return -sum(past[r][c] for c,r in enumerate(assignment))


def smart_assign(assignments):
    '''Given a list of possible chore assignments, repeatedly yield assignments that maximize score.'''
    past = times_assigned([])
    while True:
        scored_assignments = [(score(a, past), a) for a in assignments]
        list.sort(scored_assignments)
        next_assignment = scored_assignments[-1][1]
        yield next_assignment
        past = times_assigned([next_assignment], past)
        print past

print 'smart assignment stream:'
for month,assignment in enumerate(smart_assign(all_valid())):
    print '%d:\t%s' % (month, assignment)
