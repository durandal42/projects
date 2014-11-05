import pstats
p = pstats.Stats('solve_everything_profile')

p.sort_stats('cumulative').print_stats(40)
