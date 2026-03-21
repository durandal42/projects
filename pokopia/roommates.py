import csv
import typing
import itertools
import collections


class Pokemon(typing.NamedTuple):
  name: str
  habitat: str
  favorites: list[str]


class Roommates(typing.NamedTuple):
  names: tuple[str]
  habitats: set[str]
  favorites: set[str]


POKEMON_DENYLIST = ["Tangrowth", "Kyogre"]


def load_pokemon():
  result = []
  with open('pokemon.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for row in reader:
      if row[0] in ("name", "???"):
        continue
      p = Pokemon(name=row[0], habitat=row[1], favorites=row[2].split("\n"))
      if p.name in POKEMON_DENYLIST:
        continue
      result.append(p)
      # print(p)
  return result


# for p in load_pokemon():
#   print(p)
# print()


def is_sorted(l):
  # return all(x <= y for x, y in itertools.pairwise(l))  # needs python 3.10
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
  shared = set(favorites_lists[0])
  for favorites in favorites_lists[1:]:
    shared = shared & set(favorites)
  return shared


def roommates(pokemons, group_size=2,
              min_shared_favorites=2, demand_singular_habitat=False):
  print(
      f"finding possible roommate groups of size {group_size}",
      f", with at least {min_shared_favorites} shared favorites",
      (demand_singular_habitat
       and ", with a single desire habitat"
       or ", with non-conflicting habitats"),
      "..."
  )
  dex = {}
  for i, p in enumerate(pokemons):
    dex[p.name] = i

  result = []
  for rs in itertools.product(pokemons, repeat=group_size):
    names = tuple([r.name for r in rs])
    if len(set(names)) != group_size:
      # print(f"excluding {names} because it has duplicates")
      continue
    if not is_sorted([dex[n] for n in names]):
      # print(f"excluding {names} because it's not the canonical order'")
      continue

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


def popularity(eligible_groups):
  result = collections.Counter()
  for eg in eligible_groups:
    for p in eg.names:
      result[p] += 1
  return result


def score_group(group, popularity):
  return sum(1/popularity[n] for n in group.names)


def partition_into_roommate_groups(pokemons):
  eligible_groups = []
  for group_size in range(1, 5):
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

    best_group = max(scored_groups)[1]
    print("\nbest_group:", best_group)
    results.append(best_group)

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


if __name__ == "__main__":
  main()
