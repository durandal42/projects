import csv
import typing
import itertools
import collections
import operator
import functools


class Pokemon(typing.NamedTuple):
  name: str
  habitat: str
  favorites: list[str]


class Roommates(typing.NamedTuple):
  names: tuple[str]
  habitats: set[str]
  favorites: set[str]


POKEMON_DENYLIST = [
    "Tangrowth",  # Professor doesn't want a house
    "Kyogre",  # Legendary whale is too big for a house
    "Hoppip",  # event pokemon who "lives" in the poke center?
]


# Reads data copied from a sheet like https://docs.google.com/spreadsheets/
# d/1EWKSHFuhiYgJLNarlUZFJJm9Ti8bXb_va-FsNpGNdd8/edit?gid=0#gid=0
# Columns needed: 'name', 'ideal habitat', 'favorites (csv)'
def load_pokemon():
  result = []
  with open('pokemon.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for row in reader:
      # exlude header row, and unrecruited pokemon shadows
      if row[0] in ("name", "???"):
        continue

      # exclude explicitly denylisted
      p = Pokemon(name=row[0], habitat=row[1], favorites=row[2].split(","))
      if p.name in POKEMON_DENYLIST:
        continue

      result.append(p)
      # print(p)
  return result


# Writes data to be pasted back into a sheet.
# Columns provided: name(s), habitat(s), favorite(s)
def export_groups(groups):
  with open('groups.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"')
    writer.writerow(['name(s)', 'habitat(s)', 'favorite(s)'])
    for g in groups:
      writer.writerow([
          '\n'.join(g.names),
          '\n'.join(g.habitats),
          '\n'.join(g.favorites),
      ])


# Writes data to be pasted back into a sheet.
# Columns provided: name1-4, habitat1, habitat2, favorite1-6
def export_groups_flat(groups):
  columns = []

  column_groups = {'name': 4, 'habitat': 2, 'favorite': 6}
  for name, mulitplicity in column_groups.items():
    for i in range(mulitplicity):
      columns.append(f"{name}{i+1}")

  with open('groups_flat.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, delimiter='\t',
                            quotechar='"', fieldnames=columns)
    writer.writeheader()

    for g in groups:
      row_dict = {}
      for name, mulitplicity in column_groups.items():
        for i, value in enumerate(getattr(g, name + "s")):
          row_dict[f"{name}{i+1}"] = value

      writer.writerow(row_dict)


def is_sorted(l):
  # return all(x <= y for x, y in itertools.pairwise(l)) # needs python 3.10
  return l == sorted(l)


def compatible_habitats(hs):
  incompatible_pairs = [
      ("Dark", "Bright"),
      ("Humid", "Dry"),
      ("Warm", "Cool"),
  ]
  for h1, h2 in incompatible_pairs:
    if h1 in hs and h2 in hs:
      return False
  return True


def shared_favorites(favorites_lists):
  return functools.reduce(operator.and_, [set(l) for l in favorites_lists])


def roommates(pokemons, group_size,
              min_shared_favorites=2,
              demand_singular_habitat=False):
  print(
      f"finding possible roommate groups of size {group_size}",
      f", with at least {min_shared_favorites} shared favorites",
      (demand_singular_habitat
       and ", with a single desire habitat"
       or ", with non-conflicting habitats"),
      "..."
  )

  result = []
  for rs in itertools.combinations(pokemons, r=group_size):
    names = tuple([r.name for r in rs])
    habitats = set([r.habitat for r in rs])
    if not compatible_habitats(habitats):
      # print(f"excluding {names} because "
      #       f"they have incompatible habitats: {habitats}'")
      continue

    if demand_singular_habitat and len(habitats) > 1:
      # print(f"excluding {names} because "
      #       f"they don't want identical habitats: {habitats}'")
      continue

    favorites = shared_favorites([r.favorites for r in rs])
    if len(favorites) < min_shared_favorites:
      # print(f"excluding {names} because "
      #       "they don't have enough shared favorites "
      #       f"({len(favorites)} < {min_shared_favorites})'")
      continue

    r = Roommates(names=names, habitats=habitats, favorites=favorites)
    print(f"\t{r}")
    result.append(r)

  return result


# A pokemon's popularity is how many eligible groups it appears in.
def popularity(eligible_groups):
  result = collections.Counter()
  for eg in eligible_groups:
    for p in eg.names:
      result[p] += 1
  return result


def score_group(group, popularity):
  # Adding more pokemon to a group is always good.
  # Adding pokemon who are unpopular is even better.
  return sum(1/popularity[n] for n in group.names)


def partition_into_roommate_groups(pokemons, max_group_size=4):
  eligible_groups = []
  # Consider all group sizes up to cap,
  # because a partial group is better than leaving someone alone.
  # (and considering size=1 allows us to express solo housing at all!)
  for group_size in range(1, max_group_size+1):
    eligible_groups += roommates(
        pokemons, group_size=group_size, min_shared_favorites=2)

  results = []
  while eligible_groups:
    pop = popularity(eligible_groups)
    print("\npopularity of available pokemon:")
    for name, num_groups in popularity(eligible_groups).most_common():
      print(f"\t{name}: {num_groups}")

    scored_groups = [(score_group(eg, pop), eg) for eg in eligible_groups]
    print("\nscore for each group:")
    for score, eg in sorted(scored_groups)[-10:]:
      print("\t", score, eg)

    # Greedily pick the best group available in the current iteration.
    best_group = max(scored_groups)[1]
    print("\nbest_group:", best_group)
    results.append(best_group)

    # Remove all groups containing newly-grouped pokemon from eligibility.
    eligible_groups = list(filter(
        lambda eg: len(set(eg.names) & set(best_group.names)) == 0,
        eligible_groups))

  return results


def main():
  pokemon = load_pokemon()
  best_groups = partition_into_roommate_groups(pokemon)
  print("\nbest groups:")
  for g in best_groups:
    print(g)

  export_groups(best_groups)
  export_groups_flat(best_groups)


if __name__ == "__main__":
  main()
