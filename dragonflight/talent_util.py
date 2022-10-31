import multiprocessing
import functools

def how_many_builds_pick_this_talent(ti, builds):
  result = 0
  t_bit = 1 << ti
  for b in builds:
    if b & t_bit > 0:
      result += 1
  return result

def talent_appearances(talents, builds):
  with multiprocessing.Pool(5) as p:
      return p.map(functools.partial(how_many_builds_pick_this_talent,
                                     builds=builds),
                   talents)
  #  return list(map(functools.partial(how_many_builds_pick_this_talent, builds=builds),
  #                                talents))

