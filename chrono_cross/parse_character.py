STAMINA = {
    13: "Draggy",
    12: "Kid, Pierre, Razzly",
    11: "Funguy, Glenn, Harle, Irenes, Leena, Luccia, Marcy, Mel, Miki, Mojo, NeoFio, Norris, Orlha, Riddel, Starky, Steena",
    10: "Doc, Fargo, Grobyc, Janice, Korcha, Pip, Serge, Skelly, Sprigg, Van, Lynx",
    9: "Greco, Karsh, Leah, Macha, Nikki, Orcha, Poshul, Radius, Sneff, Turnip, Viper",
    8: "Guile, Zappa, Zoah",
}

EXAMPLE = '''
Serge
Element Grid: [Star Level Required to Receive Slot]

[  22  ][  31  ][  39  ][      ][      ][      ][      ][      ]
[  19  ][  20  ][  24  ][  30  ][      ][      ][      ][      ]
[  12  ][  14  ][  16  ][  23  ][  36  ][      ][      ][      ]
[  07  ][  08  ][  09  ][  13  ][  21  ][  34  ][  46  ][  48  ]
[  00  ][  00  ][  00  ][  05  ][  11  ][  18  ][  26  ][  37  ]
[  01  ][  02  ][  03  ][  10  ][  15  ][  29  ][  35  ][  41  ]
[  04  ][  06  ][  25  ][  28  ][  33  ][  40  ][  43  ][  44  ]
[  17  ][  27  ][  32  ][  47  ][      ][      ][      ][      ]
INNATE COLOR: White

MAX HP:         850 (4.5% above average)
MAX STR:         88 (5.5% above average)
MAX RES:         78 (3.2% above average)
MAX MAG:         52 (8.6% above average)
MAX M.RES:       43 (6.4% above average)
Dash&Slash: Physical Tech - One Enemy - Typical
Luminaire: Magical Tech - All Enemies - Typical
FlyingArrow: Magical Tech - One Enemy - Typical
Overall Analysis: Naturally, by the math, and element grid, there can be nothing but positive remarks for our silent protagonist. His secondary stats are average, including his 10 Stamina Recovery. Since the numbers don't necessarily do it justice, I will talk more about this grid. This is the second best overall grid in my book. Excellent throughout the game and comes up just short against the one Harle and Riddel possess. In fact, after this section, I will give advanced rankings of the characters based on the 5 main stats and the grid. It isn't binders full of women, but I have spreadsheets full of statistics on this game. Serge ranks highly in almost every metric I have used, including his personal best of 2nd in that specific one. When he becomes Lynx, everything is the same, but Lynx's final technique is a magical technique on all. For my money, that is slightly better. That being said, white is probably the best overall innate, so I would still say Serge has a bigger advantage. He is basically a must on an all white team. Look, all this praise without even mentioning the Mastermune. What a joke that makes the game.
'''

STAT_NAMES = ["HP", "STR", "RES", "MAG", "M.RES"]

import re


def parse(lines):
  name = lines[0].strip()

  stamina = None
  for sta, names in STAMINA.items():
    if name in names.split(', '):
      stamina = sta
      break

  grid = []
  stats = {}

  for line in lines:
    match = re.match("\[\s*(\d*)\s*\]" * 8, line)
    if match:
      grid.append(match.groups())

    match = re.match("INNATE COLOR: (\w+)", line)
    if match:
      color = match.group(1)

    for stat in STAT_NAMES:
      match = re.match("MAX %s:\s*(\d+)" % stat, line)
      if match:
        stats[stat] = int(match.group(1))

  grid_size = [sum(1 for g in grid if g[i] != '') for i in range(8)]

  return [name, color, stamina] + [stats[stat] for stat in STAT_NAMES] + grid_size


def csv(parsed):
  return '\t'.join(str(x) for x in parsed)

# print csv(parse(EXAMPLE.splitlines()))


def parse_many(lines):
  buffer = []
  for line in lines:
    line = line.strip()
    if re.match("\w+$", line):  # this is a new name
      if buffer:
        print csv(parse(buffer))
      buffer = []
    buffer.append(line)
  if buffer:
    print csv(parse(buffer))

import sys
parse_many(sys.stdin.readlines())
