import json
import sys

print('loading cards...')
CARDS = json.load(open('default-cards-20230716211530.json'))
print('loaded', len(CARDS), 'cards.')

# print('example card:', CARDS[0])

input_columns = ['name', 'set', 'collector_number', 'artist', 'foil?']
lookup_columns = input_columns[:4]
output_columns = input_columns + ['price']
for line in sys.stdin:
  tokens = line.rstrip("\n").split("\t")
  # print(tokens)

  card_dict = {}
  for c, t in zip(input_columns, tokens):
    card_dict[c] = t
  # print("looking for:", card_dict)

  matching_cards = []
  for card in CARDS:
    match = True
    for c in lookup_columns:
      v = card_dict[c]
      if v and v != card.get(c):
        match = False
      if match == False:
        break
    if match:
      matching_cards.append(card)

  if len(matching_cards) == 0:
    # print("no matches!")
    matching_cards = [card_dict]
    # break
  if len(matching_cards) > 1:
    # print("multiple matches!")
    matching_cards = [card_dict]
    # break

  for card in matching_cards[:10]:
    # special handling for price
    card['foil?'] = card_dict.get('foil?', '')
    if card['foil?'] == 'TRUE':
      card['price'] = card.get('prices', {}).get('usd_foil', '')
    else:
      card['price'] = card.get('prices', {}).get('usd', '')

    print("\t".join(card.get(c) for c in output_columns))
