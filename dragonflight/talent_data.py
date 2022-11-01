import collections
import whtrees

Talent = collections.namedtuple("Talent", "name cell_id points parents required_points")

def convert_wh_tree(wht):
  print(wht)
  tree = []
  for cell_id, cell_variants in wht.items():
    tree.append(Talent(
      name=cell_variants[0]['spells'][0]['name'],
      cell_id=cell_id,
      points=cell_variants[0]['spells'][0]['points'],
      parents=[wht[parent_cell_id][0]['spells'][0]['name']
               for parent_cell_id in cell_variants[0]['requires']],
      required_points=cell_variants[0]['requiredPoints'],
      ))
  
  print(tree)
  return tree

def get_talents(tree_name):
  wht = whtrees.get_tree(tree_name=tree_name)
  if wht: return convert_wh_tree(wht)
  return TALENT_TREES[tree_name]
