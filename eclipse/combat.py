def assertEquals(expected, actual):
  if expected != actual:
    raise AssertionError("expected: %s;\tactual: %s" % (expected, actual))

def single_shot_distribution(computer=0, shield=0):
  hit_chance = max(1, min(5, 1 + computer - shield)) # in 1/6ths
  return {0:6-hit_chance, 1:hit_chance}

assertEquals(1, single_shot_distribution()[1])
assertEquals(2, single_shot_distribution(computer=1)[1])
assertEquals(1, single_shot_distribution(shield=1)[1])
assertEquals(1, single_shot_distribution(computer=1, shield=1)[1])
assertEquals(5, single_shot_distribution(computer=10, shield=1)[1])

def cross_counted(args, f=lambda x:x):
    ans = {():1}
    for arg in args:
        ans = dict([(x+(y,), times*t)
                    for (x,t) in ans.iteritems()
                    for (y,times) in arg.iteritems()])
    result = {}
    for x,y in ans.iteritems():
        x = f(x)
        if x not in result:
            result[x] = 0
        result[x] += y
    return result

assertEquals({0:1, 1:2, 2:1}, cross_counted([{0:1, 1:1}] * 2, f=sum))

def multi_shot_distribution(shots=1, computer=0, shield=0):
  return cross_counted([single_shot_distribution(computer, shield)] * shots, f=sum)

assertEquals({0:5, 1:1}, multi_shot_distribution())
assertEquals({0:4, 1:2}, multi_shot_distribution(computer=1))
assertEquals({0:1, 1:5}, multi_shot_distribution(computer=10))
assertEquals({0:25, 1:10, 2:1}, multi_shot_distribution(shots=2))
assertEquals({0:1, 1:10, 2:25}, multi_shot_distribution(shots=2, computer=10))

# note: no-delta rounds can be dropped entirely, so long as there is at least one outcome with a delta

# TODO(durandal): guns with damage values other than 1
# TODO(durandal): missiles
# TODO(durandal): initiative

def ship(hull=0, guns=0, computer=0, shield=0):
  return (hull, guns, computer, shield)

attacker=ship()

state = (ship(), ship())

def combat_round(state):
  

print state
