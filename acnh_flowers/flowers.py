import csv
import re
import collections
import itertools
from pprint import pprint

Flower = collections.namedtuple('Flower', ['genotype', 'phenotype'])


def parse_color_data(family):
  with open(f'{family}.csv', newline='') as raw_data:
    reader = csv.reader(raw_data)

    colors = {}
    seed_buyables = []
    for row in reader:
      # print(', '.join(row))

      if row[0] == 'Hex':
        continue  # header
      index = int(row[0], 16)

      color = row[8]

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


def genes_offered(f, choices):
  return "".join((f.genotype & (1 << (7 - 2*i - choices[i])) and "1" or "0" for i in range(4)))


assert(genes_offered(Flower(genotype=255, phenotype=''), [0, 0, 0, 0]) == '1111')
assert(genes_offered(Flower(genotype=255, phenotype=''), [1, 1, 1, 1]) == '1111')
assert(genes_offered(Flower(genotype=0, phenotype=''), [0, 0, 0, 0]) == '0000')
assert(genes_offered(Flower(genotype=0, phenotype=''), [1, 1, 1, 1]) == '0000')


def breed(f1, f2):
  result = collections.Counter()

  print("breeding", f1, "x", f2)
  # print("parent genotypes:", format_genotype(f1.genotype), format_genotype(f2.genotype))
  for f1_gene_choices in itertools.product(range(2), repeat=4):
    # print("f1 choices:", f1_gene_choices)
    f1_genes_offered = genes_offered(f1, f1_gene_choices)
    # print("f1 offered:", f1_genes_offered)
    for f2_gene_choices in itertools.product(range(2), repeat=4):
      # print("\tf2 choices:", f2_gene_choices)
      f2_genes_offered = genes_offered(f2, f2_gene_choices)
      # print("\tf2 offered:", f2_genes_offered)

      child_gene_pairs = ["".join(sorted([f1g, f2g]))
                          for f1g, f2g in zip(f1_genes_offered, f2_genes_offered)]
      # print("\tchild gene pairs:", child_gene_pairs)
      child_genotype = int("".join(child_gene_pairs), 2)
      # print("\tchild genotype:", format_genotype(child_genotype))

      # print()
      result[child_genotype] += 1

  # print(result)
  return result


def find_reachable_colors(all_colors, starting_genotypes):
  reachable = {}
  for g in starting_genotypes:
    reachable[g] = 0
  num_reachable = 0
  pairs_tried = set()

  while len(reachable) > num_reachable:
    num_reachable = len(reachable)
    for g1, g2 in itertools.combinations_with_replacement(reachable.keys(), 2):
      if (g1, g2) in pairs_tried:
        continue
      pairs_tried.add((g1, g2))

      child_possibilities = breed(all_colors[g1], all_colors[g2])
      # TODO(durandal): complexity penalty when child genotype can't be determined from phenotype
      for child_genotype, byte_prob in child_possibilities.items():
        newly_reached = child_genotype not in reachable
        if newly_reached:
          reachable[child_genotype] = 1 + max(reachable[g1], reachable[g2])
        print(f'\t{all_colors[child_genotype]}: {byte_prob} / 256{newly_reached and " new!" or ""}')
    print("reachable genotypes:", len(reachable), reachable)

  generations = collections.defaultdict(list)
  for genotype, generation in reachable.items():
    generations[generation].append(genotype)
  print("reachable flowers, by min generations from store seeds:")
  for generation, genotypes in generations.items():
    print(generation)
    pprint([all_colors[g] for g in sorted(genotypes)])
    print()

  print("unreachable flowers:")
  pprint([all_colors[g] for g in sorted(set(all_colors.keys()) - set(reachable.keys()))])


if __name__ == '__main__':
  colors, buyables = parse_color_data('roses')
  print('loaded color data:')
  pprint(list(colors.values()))
  print()

  print("buyable as seeds:", buyables)
  print()

  find_reachable_colors(colors, buyables)
