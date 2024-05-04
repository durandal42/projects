from distribution import *
from functools import reduce


def nat1():
  # could just say 'return d == 1' but we're gonna want the count
  return die(20).map(lambda x: 1 if x == 1 else 0)


def nat1s(n):
  return pow(nat1(), n)

print(nat1())


'''
Our Half-Elf Warlock rolled 713 times, with an average of 11, 47 nat 1's and 89 nat 20's

Our Human Fighter rolled 935 times with an average of 8, 82 nat 1's and 53 nat 20's

Our Gnome Bard rolled 822 times with an average of 14, with 63 nat 1's and 52 nat 20's

Our Goliath Barbarian rolled 853 times with an avwrage of 14 as well! but with a much better 57 nat 1's and 98 nat 20's

And I, the Tiefling Rogue, rolled 813 times with an average of 6, with 102 nat 1's and 37 nat 20's
'''

OBSERVATIONS = [
    ("target dummy", 20, 10, 1, 1),
    # with an average of 10
    # odds of at least 200: 0.6569974906137718
    # odds of at most 200: 0.35727500853293476
    # odds of exactly 200: 0.014272499146706526
    # 1 nat 1's
    # odds of at least 1: 0.6415140775914577
    # odds of at most 1: 0.7358395249438499
    # odds of exactly 1: 0.37735360253530764
    # 1 nat 20's
    # odds of at least 1: 0.6415140775914577
    # odds of at most 1: 0.7358395249438499
    # odds of exactly 1: 0.37735360253530764
    ("Half-Elf Warlock", 713, 11, 47, 89),
    # with an average of 11
    # odds of at least 7843: 0.010375024114665937
    # odds of at most 7843: 0.9898025490773474
    # odds of exactly 7843: 0.0001775731920133367
    # 47 nat 1's
    # odds of at least 47: 0.03520713099739973
    # odds of at most 47: 0.975380659791054
    # odds of exactly 47: 0.010587790788453816
    # 89 nat 20's
    # odds of at least 89: 5.247835238560209e-15
    # odds of at most 89: 0.9999999999999981
    # odds of exactly 89: 3.346215982113803e-15
    ("Human Fighter", 935, 8, 82, 53),
    # with an average of 8
    # odds of at least 7480: 1.0
    # odds of at most 7480: 3.860225950672171e-41
    # odds of exactly 7480: 2.9185023392676396e-42
    # 82 nat 1's
    # odds of at least 82: 9.655411906490973e-07
    # odds of at most 82: 0.9999994851319814
    # odds of exactly 82: 4.5067317206028266e-07
    # 53 nat 20's
    # odds of at least 53: 0.1924398859433571
    # odds of at most 53: 0.844486053944597
    # odds of exactly 53: 0.0369259398879541
    ("Gnome Bard", 822, 14, 63, 52),
    # with an average of 14
    # odds of at least 11508: 9.892644261198873e-71
    # odds of at most 11508: 1.0
    # odds of exactly 11508: 1.0695306481384844e-71
    # 63 nat 1's
    # odds of at least 63: 0.0006549842209468153
    # odds of at most 63: 0.9996008595712533
    # odds of exactly 63: 0.0002558437922001767
    # 52 nat 20's
    # odds of at least 52: 0.051851267629441575
    # odds of at most 52: 0.96210014085585
    # odds of exactly 52: 0.013951408485291677
    ("Goliath Barbarian", 853, 14, 57, 98),
    # with an average of 14
    # odds of at least 11942: 2.5558157499816997e-73
    # odds of at most 11942: 1.0
    # odds of exactly 11942: 2.7629288258398246e-74
    # 57 nat 1's
    # odds of at least 57: 0.01787932336642043
    # odds of at most 57: 0.9875467742811506
    # odds of exactly 57: 0.005426097647570998
    # 98 nat 20's
    # odds of at least 98: 4.3848180805068895e-14
    # odds of at most 98: 0.9999999999999826
    # odds of exactly 98: 2.6376998204274368e-14
    ("Tiefling Rogue", 813, 6, 102, 37),
    # with an average of 6
    # odds of at least 4878: 1.0
    # odds of at most 4878: 1.6217504527035154e-117
    # odds of exactly 4878: 2.3451728110787168e-118
    # 102 nat 1's
    # odds of at least 102: 4.202004724517394e-17
    # odds of at most 102: 1.0
    # odds of exactly 102: 2.6846828196707717e-17
    # 37 nat 20's
    # odds of at least 37: 0.7435637748147186
    # odds of at most 37: 0.31251587876985504
    # odds of exactly 37: 0.056079653584573584

]
OBSERVATIONS = sorted(OBSERVATIONS, key=lambda o: o[1])
print(OBSERVATIONS)

d = constant(0)
prev_n = 0
for o in OBSERVATIONS:
  name, rolls, avg, ones, twenties = o[0], o[1], o[2], o[3], o[4]
  print(f"Our {name} rolled {rolls} times")
  d += dice(rolls - prev_n, 20)
  prev_n = rolls
  print(f"with an average of {avg}")
  plausibility(d, rolls * avg, exact=False)
  n1 = nat1s(rolls)
  print(f"{ones} nat 1's")
  plausibility(n1, ones, exact=False)
  print(f"{twenties} nat 20's")
  plausibility(n1, twenties, exact=False)
