import sys
import csv
import re
import collections
import itertools
from pprint import pprint
from fractions import Fraction

Flower = collections.namedtuple('Flower', ['genotype', 'phenotype'])


def shortname(f):
  return f'{f.phenotype}{f.genotype}'


def parse_color_data(family):
  with open(f'{family}.csv', newline='') as raw_data:
    reader = csv.reader(raw_data)

    colors = {}
    seed_buyables = []
    for row in reader:
      # print(', '.join(row))

      if row[0] == 'Hex':  # header
        color_column = row.index("Color")
        continue
      index = int(row[0], 16)

      color = row[color_column]

      m = re.fullmatch(r'(\w+)( \(seed\))?', color)
      if not m:
        print(f"couldn't get color + seed status from: '{color}'")
        exit(-1)

      color = m.group(1)
      seed = (m.group(2) is not None)

      # print(hex(index), bin(index), color, seed)
      fc = Flower(genotype=index, phenotype=color)
      # print(fc, "seed buyable!" if seed else "")

      colors[index] = fc
      if seed:
        seed_buyables.append(index)
    # print()

    return colors, seed_buyables


def format_genotype(g):
  return format(g, '#010b')[2:]


assert format_genotype(0) == '00000000'
assert format_genotype(31) == '00011111'
assert format_genotype(255) == '11111111'


def nth_bit(i, n):
  return (i >> n) & 1


assert nth_bit(1, 0) == 1
assert nth_bit(0, 0) == 0
assert nth_bit(255, 7) == 1
assert nth_bit(127, 7) == 0


def gene_bit_index(group_index, bit_index):
  # Genes have four groups of two bits.
  # Given a group index [0..4] and a bit index [0,1], get the overall bit index.
  # Read bits left to right, so display stuff lines up.
  return 7 - (2*group_index + bit_index)


assert gene_bit_index(0, 0) == 7
assert gene_bit_index(0, 1) == 6
assert gene_bit_index(1, 0) == 5
assert gene_bit_index(1, 1) == 4
assert gene_bit_index(2, 0) == 3
assert gene_bit_index(2, 1) == 2
assert gene_bit_index(3, 0) == 1
assert gene_bit_index(3, 1) == 0


def genes_offered(f, choices):
  return [nth_bit(f.genotype, gene_bit_index(i, choices[i])) for i in range(4)]


assert(genes_offered(Flower(genotype=0b11111111, phenotype=''), [0, 0, 0, 0]) == [1, 1, 1, 1])
assert(genes_offered(Flower(genotype=0b11111111, phenotype=''), [1, 1, 1, 1]) == [1, 1, 1, 1])
assert(genes_offered(Flower(genotype=0b00000000, phenotype=''), [0, 0, 0, 0]) == [0, 0, 0, 0])
assert(genes_offered(Flower(genotype=0b00000000, phenotype=''), [1, 1, 1, 1]) == [0, 0, 0, 0])
assert(genes_offered(Flower(genotype=0b10101010, phenotype=''), [1, 1, 1, 1]) == [0, 0, 0, 0])
assert(genes_offered(Flower(genotype=0b10101010, phenotype=''), [0, 0, 0, 0]) == [1, 1, 1, 1])
assert(genes_offered(Flower(genotype=0b11110000, phenotype=''), [0, 0, 0, 0]) == [1, 1, 0, 0])
assert(genes_offered(Flower(genotype=0b11110000, phenotype=''), [1, 1, 1, 1]) == [1, 1, 0, 0])


def bitlist_to_integer(bitlist):
  out = 0
  for bit in bitlist:
    out = (out << 1) | bit
  return out


assert bitlist_to_integer([1, 1, 1]) == 7
assert bitlist_to_integer([1, 0, 0]) == 4


def sort_gene_pair(g1, g2):
  if g1 == 1 and g2 == 0:
    return 0, 1
  return g1, g2


def splice(half_genes1, half_genes2):
  # Given two parent half-genotypes, produce one child genotype
  child_gene_pairs = [
      sort_gene_pair(g1, g2)
      for g1, g2 in zip(half_genes1, half_genes2)]
  return bitlist_to_integer(itertools.chain.from_iterable(child_gene_pairs))


# print(splice((1, 1, 1, 1), (0, 0, 0, 0)))
assert splice((1, 1, 1, 1), (0, 0, 0, 0)) == 0b01010101
assert splice((0, 0, 0, 0), (1, 1, 1, 1)) == 0b01010101
assert splice((0, 0, 1, 1), (0, 1, 0, 1)) == 0b00010111


def breed(f1, f2):
  # Given a pair of flowers, return a distribution of all possible children they could spawn.
  result = collections.Counter()

  print("breeding", f1, "x", f2)
  # print("parent genotypes:", format_genotype(f1.genotype), format_genotype(f2.genotype))
  for f1_gene_choices in itertools.product(range(2), repeat=4):
    f1_genes_offered = genes_offered(f1, f1_gene_choices)

    for f2_gene_choices in itertools.product(range(2), repeat=4):
      f2_genes_offered = genes_offered(f2, f2_gene_choices)

      child_genotype = splice(f1_genes_offered, f2_genes_offered)

      result[child_genotype] += 1

  # print(result)
  return result


Lineage = collections.namedtuple('Lineage', ['generation', 'tree', 'duration'])
Pairing = collections.namedtuple('Pairing', ['generation', 'child', 'instruction', 'probability'])


def find_reachable_colors(all_colors, starting_genotypes):
  # Given a starting set of genotypes, find everything reachable via breeding.
  # Also detmerine the family tree depth required to get to each possible target.
  reachable = {}
  for g in starting_genotypes:
    reachable[g] = Lineage(generation=0, duration=0,
                           tree=set([Pairing(generation=0,
                                             child=shortname(all_colors[g]),
                                             instruction="seed",
                                             probability=1)]))
  pairs_tried = set()
  making_progress = True

  while making_progress:
    making_progress = False
    for g1, g2 in itertools.combinations_with_replacement(reachable.keys(), 2):
      if (g1, g2) in pairs_tried:
        continue
      pairs_tried.add((g1, g2))

      child_possibilities = breed(all_colors[g1], all_colors[g2])
      # TODO(durandal): complexity penalty when child genotype can't be determined from phenotype
      genotypes_per_phenotype = collections.Counter(all_colors[g].phenotype for g in child_possibilities.keys())
      # print(genotypes_per_phenotype)
      for child_genotype, byte_prob in child_possibilities.items():
        suffix = ""
        probability = Fraction(byte_prob, 256)
        lineage1 = reachable[g1]
        lineage2 = reachable[g2]
        duration = 1 / probability + max(lineage1.duration, lineage2.duration)
        if genotypes_per_phenotype[all_colors[child_genotype].phenotype] > 1:
          suffix += " ambiguous :("
        elif child_genotype not in reachable or reachable[child_genotype].duration > duration:
          generation = 1 + max(lineage1[0], lineage2[0])
          target_name = shortname(all_colors[child_genotype])
          p1_name = shortname(all_colors[g1])
          p2_name = shortname(all_colors[g2])

          tree = set()
          tree.add(Pairing(generation=generation,
                           child=target_name,
                           instruction=f'{p1_name} + {p2_name}',
                           probability=probability))
          tree = tree.union(lineage1[1], lineage2[1])
          reachable[child_genotype] = Lineage(generation, tree, duration)
          suffix += " new!"
          making_progress = True
        print(f'\t{all_colors[child_genotype]}: {byte_prob} / 256{suffix}')
    # print("reachable genotypes:", len(reachable), reachable)

  print()
  print()
  print("reachable flowers, by duration, earliest per phenotype only:")
  print()
  seen_phenotypes = set()
  for g, lineage in sorted(reachable.items(), key=lambda gl: gl[1].duration):
    f = all_colors[g]
    if f.phenotype in seen_phenotypes:
      continue
    seen_phenotypes.add(f.phenotype)
    print(shortname(f))
    print("\tgeneration:", lineage.generation)
    print("\tduration:", lineage.duration)
    print("\ttree:")
    for p in sorted(lineage.tree, key=lambda p: p.generation):
      print(f'\t\t{p.generation}: {p.child}: {p.instruction} ({p.probability})')
    print()

  # print("unreachable flowers:")
  # pprint([shortname(all_colors[g]) for g in sorted(set(all_colors.keys()) - set(reachable.keys()))])
  print("unreachable phenotypes:")
  pprint(set(f.phenotype for f in all_colors.values()) -
         set(all_colors[g].phenotype for g in reachable.keys()))


if __name__ == '__main__':
  colors, buyables = parse_color_data(sys.argv[1])
  print('loaded color data:')
  pprint(list(colors.values()))
  print()

  print("buyable as seeds:", buyables)
  print()

  find_reachable_colors(colors, buyables)
