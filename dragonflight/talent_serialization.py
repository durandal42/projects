# -- WoW 10.0 Class Talent Tree Import/Export 
# -- File Format Specifications

# -- The import/export string for Class Talent is created in two steps:
# -- 1. Create a variable sized byte arry using a bit stream to represent the state of the tree
# -- 2. Convert the binary data to a base64 string

# -- HEADER (fixed-size)
# --  Serialization Version, 8 bits. 
# --  The version of the serialization method.
#  If the client updates the export algorithm, the version will be incremented,
#    and loadouts exported with older serialization version will fail to import and need to be re-exported.
#  Currently set to 1, as defined in the constant LOADOUT_SERIALIZATION_VERSION.

# --  Specialization ID, 16 bits.  
# --  The class specialization for this loadout.
#  Uses the player's currently assigned specialization.
#  Attempting to import a loadout for a different class specialization will result in a failure.

# --  Tree Hash, 128 bits, optional.  
# --  A hash of the content of the tree to compare against the current tree when importing a loadout.
#  For third-party sites that want to generate loadout strings, this can be ommitted and zero-filled,
#    which will ignore the extra validation on import.
#  If the tree has changed and treehash is zero-filled, it will attempt to import the loadout
#    but may result in incomplete or incorrect nodes getting selected.

# -- FILE CONTENT (variable-size)
# --  Is Node Selected, 1 bit
# --    Is Partially Ranked, 1 bit
# --      Ranks Purchased, 6 bits
# --    Is Choice Node, 1 bit
# --      Choice Entry Index, 2 bits

# -- The content section uses single bits for boolean values for various node states (0=false, 1=true).
#  If the boolean is true, additional information is written to the file.

# -- Is Node Selected, 1 bit.
# -- Specifies if the node is selected in the loadout.
# If it is unselected, the 0 bit is the only information written for that node,
# and the next bit in the stream will contain the selected value for the next node in the tree. 

# -- Is Partially Ranked, 1 bit.
# -- (Only written if isNodeSelected is true). Indicates if the node is partially ranked.
# For example, if a node has 3 ranks, and the player only puts 2 ranks into that node,
#   it is marked as partially ranked and the number of ranks is written to the stream.
# If it is not partially ranked, the max number of ranks is assumed.

# -- Ranks Purchased, 6 bits.
# -- (Only written if IsPartiallyRanked is true).
# The number of ranks a player put into this node, between 1 (inclusive) and max ranks for that node (exclusive). 

# -- Is Choice Node, 1 bit
# -- (Only written if isNodeSelected is true).
# Specifies if this node is a choice node, where a player must choose one out of the available options. 

# -- Choice Entry Index, 2 bits.
# -- (Only written if isChoiceNode is true).
# The index of selected entry for the choice node. Zero-based index (first entry is index 0).

import collections
import re
import whtrees
import whnodes

def make_base64_mapping():
  bits_to_base64 = []
  for i in range(26):
    bits_to_base64.append(chr(ord('A') + i))
  for i in range(26):
    bits_to_base64.append(chr(ord('a') + i))
  for i in range(10):
    bits_to_base64.append(chr(ord('0') + i))
  bits_to_base64.append('+')
  bits_to_base64.append('/')

  base64_to_bits = {}
  for i,b in enumerate(bits_to_base64):
    base64_to_bits[b] = i
  
  return bits_to_base64, base64_to_bits

BITS_TO_BASE64, BASE64_TO_BITS = make_base64_mapping()

def blizzard_convert_to_base64(data):
  exportString = ""
  currentValue = 0
  currentReservedBits = 0
  totalBits = 0
  for remainingValue, remainingRequiredBits in data:
    maxValue = 1 << remainingRequiredBits
    if remainingValue >= maxValue:
      print("Data entry has higher value than storable in bitWidth. (%d in %d bits)"
            % (remainingValue, remainingRequiredBits))
      return None

    totalBits += remainingRequiredBits
    while remainingRequiredBits > 0:
      spaceInCurrentValue = (6 - currentReservedBits)
      maxStorableValue = 1 << spaceInCurrentValue
      remainder = remainingValue % maxStorableValue
      remainingValue = remainingValue >> spaceInCurrentValue
      currentValue += remainder << currentReservedBits

      if spaceInCurrentValue > remainingRequiredBits:
        currentReservedBits = (currentReservedBits + remainingRequiredBits) % 6;
        remainingRequiredBits = 0
      else:
        exportString += BITS_TO_BASE64[currentValue];
        currentValue = 0
        currentReservedBits = 0
        remainingRequiredBits -= spaceInCurrentValue

  if currentReservedBits > 0:
    exportString += BITS_TO_BASE64[currentValue];

  return exportString

assert blizzard_convert_to_base64([(1,8)]) == 'BA'
assert blizzard_convert_to_base64([(1,8), (251, 16)]) == 'BsPA'

# produces a list of values which still need to have data extracted from them

class blizzard_convert_from_base64:
  def __init__(self, exportString):
    self.dataValues = [BASE64_TO_BITS[c] for c in exportString]
    self.currentIndex = 0;
    self.currentExtractedBits = 0;
    self.currentRemainingValue = self.dataValues[0];

    print("dataValues converted from base64:", self.dataValues)

  def extract_value(self, bitWidth):
    if self.currentIndex >= len(self.dataValues): return None

    value = 0
    bitsNeeded = bitWidth
    extractedBits = 0
    while bitsNeeded > 0:
      remainingBits = 6 - self.currentExtractedBits;
      bitsToExtract = min(remainingBits, bitsNeeded);
      self.currentExtractedBits += bitsToExtract;
      maxStorableValue = 1 << bitsToExtract;
      remainder = self.currentRemainingValue % maxStorableValue;
      self.currentRemainingValue = self.currentRemainingValue >> bitsToExtract;
      value += remainder << extractedBits;
      extractedBits += bitsToExtract;
      bitsNeeded -= bitsToExtract;

      if bitsToExtract < remainingBits:
        break
      elif bitsToExtract >= remainingBits:
        self.currentIndex = self.currentIndex + 1
        self.currentExtractedBits = 0
        self.currentRemainingValue = self.dataValues[self.currentIndex]

    return value

SerializableTalentSelection = collections.namedtuple(
  "SerializableTalentSelection",
  "selected partially_ranked ranks_purchased choice_node choice_index",
  defaults=[False, False, 0, False, 0])

def parse_blizzard_import_string(s):
  bits = blizzard_convert_from_base64(s)

  # -- HEADER (fixed-size)
  # --  Serialization Version, 8 bits. 
  # --  The version of the serialization method.
  #  If the client updates the export algorithm, the version will be incremented,
  #    and loadouts exported with older serialization version will fail to import and need to be re-exported.
  #  Currently set to 1, as defined in the constant LOADOUT_SERIALIZATION_VERSION.
  serialization_version = bits.extract_value(8)
  print("serialization_version:", serialization_version)
  assert serialization_version == 1

  # --  Specialization ID, 16 bits.  
  # --  The class specialization for this loadout.
  #  Uses the player's currently assigned specialization.
  #  Attempting to import a loadout for a different class specialization will result in a failure.
  spec_id = bits.extract_value(16)
  print("spec_id:", spec_id)

  # --  Tree Hash, 128 bits, optional.  
  # --  A hash of the content of the tree to compare against the current tree when importing a loadout.
  #  For third-party sites that want to generate loadout strings, this can be ommitted and zero-filled,
  #    which will ignore the extra validation on import.
  #  If the tree has changed and treehash is zero-filled, it will attempt to import the loadout
  #    but may result in incomplete or incorrect nodes getting selected.
  tree_hash = bits.extract_value(128)
  print("tree_hash:", tree_hash)

  points_spent = 0
  i = 0
  sts_list = []
  sts = None
  while True:
    try:
      # -- FILE CONTENT (variable-size)
      # --  Is Node Selected, 1 bit
      # --    Is Partially Ranked, 1 bit
      # --      Ranks Purchased, 6 bits
      # --    Is Choice Node, 1 bit
      # --      Choice Entry Index, 2 bits
      node_selected = bool(bits.extract_value(1))
      sts = SerializableTalentSelection(node_selected)
      # print("node_selected:", node_selected)
      if node_selected:
        # print("node_selected:", len(sts_list))
        partially_ranked = bool(bits.extract_value(1))
        # print("  partially_ranked:", partially_ranked)
        if partially_ranked:
          ranks_purchased = bits.extract_value(6)
          # print("    ranks_purchased:", ranks_purchased)
          points_spent += ranks_purchased
          sts = sts._replace(
            partially_ranked=partially_ranked,
            ranks_purchased=ranks_purchased)
        else:
          points_spent += 1
        choice_node = bool(bits.extract_value(1))
        # print("  choice_node:", choice_node)
        if choice_node:
          choice_index = bits.extract_value(2)
          # print("    choice_index:", choice_index)
          sts = sts._replace(
            choice_node=choice_node,
            choice_index=choice_index)
      sts_list.append(sts)
      sts = None
    except IndexError:
      break

  if sts is not None:
    print("WARNING: ran out of bits while decoding a node!")

  # print("sts_list:", sts_list)
  print("Points spent:", points_spent)
  return sts_list, spec_id

def generate_blizzard_import_string(sts_list, tree_id):
  data = []

  # header
  # -- HEADER (fixed-size)
  # --  Serialization Version, 8 bits. 
  # --  The version of the serialization method.
  #  If the client updates the export algorithm, the version will be incremented,
  #    and loadouts exported with older serialization version will fail to import and need to be re-exported.
  #  Currently set to 1, as defined in the constant LOADOUT_SERIALIZATION_VERSION.
  data.append((1,8))

  # --  Specialization ID, 16 bits.  
  # --  The class specialization for this loadout.
  #  Uses the player's currently assigned specialization.
  #  Attempting to import a loadout for a different class specialization will result in a failure.
  data.append((tree_id,16))

  # --  Tree Hash, 128 bits, optional.  
  # --  A hash of the content of the tree to compare against the current tree when importing a loadout.
  #  For third-party sites that want to generate loadout strings, this can be ommitted and zero-filled,
  #    which will ignore the extra validation on import.
  #  If the tree has changed and treehash is zero-filled, it will attempt to import the loadout
  #    but may result in incomplete or incorrect nodes getting selected.
  data.append((0,128))

  for sts in sts_list:
    # TODO(dsloan): flesh this out
    # -- FILE CONTENT (variable-size)
    # --  Is Node Selected, 1 bit
    # --    Is Partially Ranked, 1 bit
    # --      Ranks Purchased, 6 bits
    # --    Is Choice Node, 1 bit
    # --      Choice Entry Index, 2 bits
    if not sts.selected:
      data.append((0, 1))
    else:
      data.append((1, 1))
      if not sts.partially_ranked:
        data.append((0, 1))
      else:
        data.append((1, 1))
        data.append((sts.ranks_purchased, 6))
      if not sts.choice_node:
        data.append((0,1))
      else:
        data.append((1, 1))
        data.append((sts.choice_index, 2))
  return blizzard_convert_to_base64(data)

blizzard_string = 'BIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAkkkEJJIRLlAIEA'

def get_spells_in_node_order(tree_id):
  wht_spec = whtrees.get_tree(tree_id)
  # print("Specialization whtree has %d cells." % len(wht_spec))
  tree_name = whtrees.TREE_NAMES_BY_ID[tree_id]
  # print("Tree name:", tree_name)
  class_name = whtrees.get_class_name(tree_name)
  # print("Class name:", class_name)
  class_id = whtrees.TREE_IDS_BY_NAME[class_name]
  # print("Class id:", class_id)
  wht_class = whtrees.get_tree(class_id)
  # print(wht_class)
  # print("Class whtree has %d cells." % len(wht_class))

  spells_by_node_id = {}
  for cell_variants in list(wht_spec.values()) + list(wht_class.values()):
    for cv in cell_variants:
      spells_by_node_id[cv['node']] = cv['spells']

  nodes = whnodes.NODES[class_id]
  # print("found %d nodes." % len(nodes))

  spells_in_node_order = [spells_by_node_id.get(n) for n in nodes]
  return spells_in_node_order  

def get_selected_talent_names(sts_list, tree_id):
  spells_in_node_order = get_spells_in_node_order(tree_id)
  assert len(sts_list) == len(spells_in_node_order)
  result = []
  for sts, spells in zip(sts_list, spells_in_node_order):
    if sts.selected:
      # print(sts)
      # spell = spells_by_node_id[n][0]
      # print("%d:\t%s" % (n, spell))
      if sts.choice_node:
        spell = spells[sts.choice_index]
      else:
        spell = spells[0]
      name = spell['name']
      # name = " / ".join(spells[i]['name'] for i in range(len(spells)))
      max_points = spell['points']
      if max_points > 1:
        if sts.partially_ranked:
          points = sts.ranks_purchased
        else:
          points = max_points
        for i in range(points):
          result.append(name + " (%d of %d)" % (i+1, max_points))
      else:
        result.append(name)
      # TODO(dsloan): handle choice nodes
  return result

def serialize_talent_names(talent_names, tree_id):
  talent_names = list(map(lambda tn: tn.split(" / ")[0], talent_names))
  spells_in_node_order = get_spells_in_node_order(tree_id)
  result = []
  for spells in spells_in_node_order:
    sts = SerializableTalentSelection()
    if spells is not None:
      names = [spell['name'] for spell in spells]
      # look up whether any name is in talent_names
      for i,name in enumerate(names):
        matching_talents = list(filter(lambda tn: tn.startswith(name), talent_names))
        for mt in matching_talents:
          name_tail = mt[len(name):]
          match = re.match("( \\((\\d) of (\\d)\\))*$", name_tail)
          if not match:
            continue

          # this talent is taken, but we need to find out how many ranks
          sts = sts._replace(selected=True)
          if match.group(1):
            points = int(match.group(2))
            max_points = int(match.group(3))
            if points < max_points:
              sts = sts._replace(partially_ranked=True, ranks_purchased=points)
            else:
              sts = sts._replace(partially_ranked=False, ranks_purchased=0)

          if len(spells) > 1:
            # print(spells)
            sts = sts._replace(choice_node=True)
          if i > 0:
            sts = sts._replace(choice_index=i)
            # TODO(dsloan): determine choice index; meanwhile default to 0
    result.append(sts)
  return result

def zero_tree_hash(export_string):
  return generate_blizzard_import_string(parse_blizzard_import_string(blizzard_string))


# find spec id in-game via:
# /run print(PlayerUtil.GetCurrentSpecID())
blizzard_strings = [
  # exported from game - Prot Paladin
  'BIEAwtJ2KpR8WbGzhz/jy2AP80kWSSIKISQBJSSABAAAAAAAAAAAAAAkkkEJJIRLlAIkC',
  # exported from game - Resto Druid
  'BkGAGX1kx6Mci9Zl2t+S+sRoPikEaSSEloEIAUSJJAAAAAAAAAAAAApEEiACESIEkQLJpBAAAAAAAA',
  # exported from game - Brewmaster Monk
  'BwQAdeydY63Y4XKaboK13uRRQAAAAAAAAAAAAgcgSJJJkDISUIAAAgkSOQKBRSkEhEBAJkIplGB',
  # exported from game - Frost Death Knight
  'BsPAdLUHklrTr3hBIcYWdbnCGLCARIBSJASOQSSkQIJJRCSQiIBJJJJJRAAAAAAAAAAAAA',
  # exported from Wowhead - Protection Paladin w/nothing selected
  'BIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
  # ... only Blessing of Freedom (node 130) selected
  'BIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAA',
  # ... and also Hammer of Wrath (node 40)
  'BIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAEAAAAAA',
  # ... and also Auras of Swift Vengeance (131)
  'BIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAkAAAAAA',
  # Prot Paladin imported to wowhead and re-exported:
  'BIEAAAAAAAAAAAAAAAAAAAAAA0kWSSIKISQBJSSABAAAAAAAAAAAAAAkkkEJJIRLlAIkC',
]

def main():
  for blizzard_string in blizzard_strings[-1:]:
    print("Here's a blizzard export string, which they claim has been base64 encoded:\n", blizzard_string)
    sts_list, tree_id = parse_blizzard_import_string(blizzard_string)
    print("Deserialized %d talents." % len(sts_list))

    talent_names = get_selected_talent_names(sts_list, tree_id)
    print("Selected talent names:", talent_names)

    sts_list_again = serialize_talent_names(talent_names, tree_id)
    print("Prepared to re-serialize %d talents." % len(sts_list_again))
    for old,new in zip(sts_list, sts_list_again):
      if old != new:
        print(old, new)
        print()
    assert sts_list == sts_list_again

    s = generate_blizzard_import_string(sts_list_again, tree_id)
    print("Roundtrip through parse/generate:", s)
    # this can't succeed with strings exported from the main game, because tree hash fails
    # It's expected to work on third party (e.g. wowhead) strings.
    if s != blizzard_string:
      assert s == zero_tree_hash(blizzard_string)

if __name__ == '__main__':
  main()
