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

import base64
import itertools

loadout_bits = 0b10001111000100000010011111011101111010111011111
# print("Python encodes base64 looking like this:", base64.b64encode(loadout_bits.to_bytes(8, byteorder='big')))

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
  # print(bits_to_base64)

  base64_to_bits = {}
  for i,b in enumerate(bits_to_base64):
    base64_to_bits[b] = i
  # print(base64_to_bits)
  
  return bits_to_base64, base64_to_bits

bits_to_base64, base64_to_bits = make_base64_mapping()

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
        exportString += bits_to_base64[currentValue];
        currentValue = 0
        currentReservedBits = 0
        remainingRequiredBits -= spaceInCurrentValue

  if currentReservedBits > 0:
    exportString += bits_to_base64[currentValue];

  return exportString

assert blizzard_convert_to_base64([(1,8)]) == 'BA'
assert blizzard_convert_to_base64([(1,8), (251, 16)]) == 'BsPA'

# produces a list of values which still need to have data extracted from them

class blizzard_convert_from_base64:
  def __init__(self, exportString):
    self.dataValues = [base64_to_bits[c] for c in exportString]
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

def parse_blizzard_import_string(s, expected_spec_id=None):
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
  if expected_spec_id is not None and spec_id != expected_spec_id: return False

  # --  Tree Hash, 128 bits, optional.  
  # --  A hash of the content of the tree to compare against the current tree when importing a loadout.
  #  For third-party sites that want to generate loadout strings, this can be ommitted and zero-filled,
  #    which will ignore the extra validation on import.
  #  If the tree has changed and treehash is zero-filled, it will attempt to import the loadout
  #    but may result in incomplete or incorrect nodes getting selected.
  tree_hash = bits.extract_value(128)
  print("tree_hash:", tree_hash)

  points_spent = 0
  node_in_progress = False
  i = 0
  nodes_selected = []
  nodes_not_selected = []
  while True:
    try:
      # -- FILE CONTENT (variable-size)
      # --  Is Node Selected, 1 bit
      # --    Is Partially Ranked, 1 bit
      # --      Ranks Purchased, 6 bits
      # --    Is Choice Node, 1 bit
      # --      Choice Entry Index, 2 bits
      node_selected = bits.extract_value(1)
      node_in_progress = True
      # print("node_selected:", node_selected)
      if node_selected:
        nodes_selected.append(i)
        # print("node_selected:", i)
        partially_ranked = bits.extract_value(1)
        # print("  partially_ranked:", partially_ranked)
        if partially_ranked:
          ranks_purchased = bits.extract_value(6)
          # print("    ranks_purchased:", ranks_purchased)
          points_spent += ranks_purchased
        else:
          points_spent += 1
        choice_node = bits.extract_value(1)
        # print("  choice_node:", choice_node)
        if choice_node:
          choice_index = bits.extract_value(2)
          # print("    choice_index:", choice_index)
      else:
        nodes_not_selected.append(i)
      node_in_progress = False
      i += 1
    except IndexError:
      break

  if node_in_progress:
    print("WARNING: ran out of bits while decoding a node!")

  print("nodes_selected:", nodes_selected)
  print("nodes_not_selected:", nodes_not_selected)
  print("Points spent:", points_spent)

def generate_blizzard_import_string(loadout, tree_id, wht):
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

  for cv in sorted(cell_variants for cell_id, cell_variants in wht.items(),
                             key=lambda cv: cv['node_id']):
    # TODO(dsloan): flesh this out
    # -- FILE CONTENT (variable-size)
    # --  Is Node Selected, 1 bit
    # --    Is Partially Ranked, 1 bit
    # --      Ranks Purchased, 6 bits
    # --    Is Choice Node, 1 bit
    # --      Choice Entry Index, 2 bits
    if not cv.selected:
      data.append((0, 1))
    else:
      data.append((1, 1))
      if not cv.partially_ranked:
        data.append((0, 1))
      else:
        data.append((1, 1))
        data.append((cv.ranks_purchased, 6))
      if not cv.choice_node:
        data.append((0,1))
      else:
        data.append((1, 1))
        data.append((cv.choice_index, 2))
  return blizzard_convert_to_base64(data)

blizzard_string = 'BIEAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAkkkEJJIRLlAIEA'

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

]

for blizzard_string in blizzard_strings[-1:]:
  print("Here's a blizzard export string, which they claim has been base64 encoded:\n", blizzard_string)
  parse_blizzard_import_string(blizzard_string)

