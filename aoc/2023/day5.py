from common import assertEqual
from common import submit
import collections
import re
import itertools


def parse_seeds(line):
  return [int(s) for s in line.split(": ")[1].split()]


MAP_HEADER_RE = re.compile('(\\w+)-to-(\\w+) map:')
RangeMap = collections.namedtuple(
    'RangeMap', ['src_range', 'dst_range_start'])


def parse_map(lines):
  m = MAP_HEADER_RE.match(lines[0])
  assert m
  src_name = m.group(1)
  dst_name = m.group(2)
  # print(f'{src_name} -> {dst_name}')
  range_maps = []
  for line in lines[1:]:
    tokens = line.split()
    assertEqual(3, len(tokens))
    dst_range_start = int(tokens[0])
    src_range_start = int(tokens[1])
    range_length = int(tokens[2])

    rm = RangeMap(range(
        src_range_start, src_range_start + range_length), dst_range_start)
    range_maps.append(rm)
    # print(rm)
  return src_name, dst_name, range_maps


def parse_input(input):
  paragraphs = input.split('\n\n')
  seeds = parse_seeds(paragraphs[0])
  # print(seeds)
  maps = [parse_map(p.splitlines()) for p in paragraphs[1:]]
  # print(maps)

  # If these pass, then we can shortcut a lot of tricky naming stuff
  prev_dst_name = 'seed'
  for src_name, dst_name, range_maps in maps:
    assertEqual(prev_dst_name, src_name)
    prev_dst_name = dst_name
  assertEqual('location', dst_name)

  return seeds, [ms for _, _, ms in maps]


def intersect_ranges(r1, r2):
  return range(max(r1.start, r2.start), min(r1.stop, r2.stop))


def range_contains(needle, haystack):
  return needle.start >= haystack.start and needle.stop <= haystack.stop

# TODO(durandal): merge ranges as needed


def assertNonOverlapping(ranges):
  ranges = sorted(ranges, key=lambda r: r.start)
  for r1, r2 in zip(ranges[:-1], ranges[1:]):
    assertEqual(0, len(intersect_ranges(r1, r2)))


def propagate_seeds(seed_ranges, range_map_stages):
  for range_maps in range_map_stages:
    seed_ranges = list(propagate(seed_ranges, range_maps))
  return seed_ranges


def propagate(input_ranges, range_maps):
  print(f'propagate({input_ranges}, {range_maps}')
  input_ranges = sorted(input_ranges, key=lambda r: r.start)
  assertNonOverlapping(input_ranges)
  range_maps = sorted(range_maps, key=lambda rm: rm.src_range.start)
  assertNonOverlapping([rm.src_range for rm in range_maps])
  print(f'propagate(after sorting)({input_ranges}, {range_maps}')

  input_range_idx, range_map_idx = 0, 0
  while input_range_idx < len(input_ranges) and range_map_idx < len(range_maps):
    ir = input_ranges[input_range_idx]
    rm = range_maps[range_map_idx]
    if rm.src_range.stop <= ir.start:
      # range map is entirely off the beginning of the input range
      range_map_idx += 1
      continue
    elif ir.stop <= rm.src_range.start:
      # input range is entirely off the beginning of the range map
      yield ir
      input_range_idx += 1
    elif range_contains(ir, rm.src_range):
      # "easy", map the entire input range, start to stop
      yield range(rm.dst_range_start + (ir.start - rm.src_range.start),
                  rm.dst_range_start + (ir.stop - rm.src_range.start))
      input_range_idx += 1
    elif ir.start < rm.src_range.start:
      # input range starts first, so pass that part through and reduce to easier
      # case
      yield range(ir.start, rm.src_range.start)
      input_ranges[input_range_idx] = range(rm.src_range.start, ir.stop)
      continue
    elif rm.src_range.start < ir.start:
      # range map starts first, so chop off the prefix and reduce to easier case
      range_maps[range_map_idx] = RangeMap(range(ir.start, rm.src_range.stop),
                                           rm.dst_range_start + (ir.start - rm.src_range.start))
      continue
    elif rm.src_range.stop < ir.stop:
      # input range extends past the end of the range map.
      # map what we can, and chop off what was mapped from input range
      yield range(rm.dst_range_start + (ir.start - rm.src_range.start),
                  rm.dst_range_start + (rm.src_range.stop - rm.src_range.start))
      input_ranges[input_range_idx] = range(rm.src_range.stop, ir.stop)
      continue
    else:
      assert False
  # any remaining input ranges are passed along as is
  for ir in input_ranges[input_range_idx:]:
    yield ir

  # for range_map in range_maps:
  #   if v in range(range_map.src_range_start,
  #                 range_map.src_range_start + range_map.range_length):
  #     print(f'found {v} within range {range_map}')
  #     v = range_map.dst_range_start + (v - range_map.src_range_start)
  #     break
  # else:
  #   # "Any source numbers that aren't mapped correspond to the same
  #   # destination number."
  #   # no-op, then!
  #   print(f"didn't find {v} among any ranges: {range_maps}")
  #   pass


def interpret_seed_specification(seed_specification):
  return [range(s, s + 1)
          for s in seed_specification]


def day5(input):
  seed_specification, range_map_stages = parse_input(input)
  final_ranges = propagate_seeds(
      interpret_seed_specification(seed_specification), range_map_stages)
  return min(r.start for r in final_ranges)


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

# part2 complication
test_output = 46


def interpret_seed_specification(seed_specification):
  return [range(start, start + length)
          for start, length in zip(seed_specification[::2],
                                   seed_specification[1::2])]

assertEqual([range(79, 93), range(55, 68)],
            list(interpret_seed_specification([79, 14, 55, 13])))


assertEqual(test_output, day5(test_input))

print('day5 part2 answer:')
submit(day5(open('day5_input.txt', 'r').read()),
       expected=None)
print()
