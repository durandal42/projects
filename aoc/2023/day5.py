from common import assertEqual
from common import submit
import collections
import re


def parse_seeds(line):
  return [int(s) for s in line.split(": ")[1].split()]


MAP_HEADER_RE = re.compile('(\\w+)-to-(\\w+) map:')
RangeMap = collections.namedtuple(
    'RangeMap', ['dst_range_start', 'src_range_start', 'range_length'])


def parse_map(lines):
  m = MAP_HEADER_RE.match(lines[0])
  assert m
  src_name = m.group(1)
  dst_name = m.group(2)
  print(f'{src_name} -> {dst_name}')
  range_maps = []
  for line in lines[1:]:
    tokens = line.split()
    assertEqual(3, len(tokens))
    rm = RangeMap(int(tokens[0]), int(tokens[1]), int(tokens[2]))
    range_maps.append(rm)
    print(rm)
  return src_name, dst_name, range_maps


def parse_input(input):
  paragraphs = input.split('\n\n')
  seeds = parse_seeds(paragraphs[0])
  print(seeds)
  maps = [parse_map(p.splitlines()) for p in paragraphs[1:]]
  print(maps)

  # If these pass, then we can shortcut a lot of tricky naming stuff
  prev_dst_name = 'seed'
  for src_name, dst_name, range_maps in maps:
    assertEqual(prev_dst_name, src_name)
    prev_dst_name = dst_name
  assertEqual('location', dst_name)

  return seeds, [ms for _, _, ms in maps]


def day5(input):
  seeds, range_map_stages = parse_input(input)
  final_locations = []
  for v in seeds:
    for range_maps in range_map_stages:
      for range_map in range_maps:
        if v in range(range_map.src_range_start,
                      range_map.src_range_start + range_map.range_length):
          print(f'found {v} within range {range_map}')
          v = range_map.dst_range_start + (v - range_map.src_range_start)
          break
      else:
        # "Any source numbers that aren't mapped correspond to the same
        # destination number."
        # no-op, then!
        print(f"didn't find {v} among any ranges: {range_maps}")
    final_locations.append(v)

  return min(final_locations)

test_input = '''seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4'''
test_output = 35

assertEqual(test_output, day5(test_input))


print('day5 answer:')
submit(day5(open('day5_input.txt', 'r').read()),
       expected=226172555)
print()
