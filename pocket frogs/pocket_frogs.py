"""
One-off script to massage data.
From: https://pocketfrogs.fandom.com/wiki/Weekly_Sets
To: https://docs.google.com/spreadsheets/d/1YoPQylzi8C5pybXFLgRb3g7_i2WVCAccTgHPmFv1qeA/
"""

import csv
import re


def enumerate_frogs(frogs_desc):
  # print("input:", frogs_desc)
  # Remove various "and" spellings, standardize on comma separation.
  for a in [", and", " and ", " & ", "; ", ", "]:
    frogs_desc = frogs_desc.replace(a, ",")

  paren_level = 0
  for i, c in enumerate(frogs_desc):
    if c == '(':
      paren_level += 1
    if c == ')':
      paren_level -= 1
    if c == ',' and paren_level == 0:
      frogs_desc = frogs_desc[:i] + ';' + frogs_desc[i + 1:]
    if paren_level > 1:
      return None
  frog_descs = frogs_desc.split(';')
  # print("semi-colon separated:", frog_descs)

  expanded = True
  while expanded:
    expanded = False

    expanded_frog_descs = []
    for frog_desc in frog_descs:
      m = re.search("\\(([^()]*)\\)", frog_desc)
      if m:
        expanded = True
        tokens = m.group(1).split(',')
        for t in tokens:
          expanded_frog_descs.append(
              re.sub("\\(([^()]*)\\)", t.strip(), frog_desc))
      else:
        expanded_frog_descs.append(frog_desc)
    # print("expanded:", expanded_frog_descs)
    frog_descs = expanded_frog_descs

  frogs = []
  for frog_desc in frog_descs:
    count = 1
    m = re.match("(\\d+)x (.*)", frog_desc)
    if m:
      count = int(m.group(1))
      frog_desc = m.group(2)
    frogs.append((frog_desc, count))
  # print("counted:", frogs)

  return frogs


def assertEquals(expected, actual):
  if expected != actual:
    raise AssertionError("expected: %s;\tactual: %s" % (expected, actual))
assertEquals(
    [
        ("Glass Chroma Anura", 1),
    ],
    enumerate_frogs("Glass Chroma Anura"))

assertEquals(
    [
        ("Glass Chroma Anura", 2),
    ],
    enumerate_frogs("2x Glass Chroma Anura"))

assertEquals(
    [
        ("Green Chroma Bovis", 2),
        ("Green Chroma Velatus", 2),
        ("Green Chroma Marmorea", 2),
    ],
    enumerate_frogs("2x Green Chroma (Bovis, Velatus, and Marmorea)"))

assertEquals(
    [
        ("Olive Folium Insero", 2),
        ("Red Tingo Insero", 2),
        ("White Cafea Floresco", 2),
    ],
    enumerate_frogs("2x (Olive Folium, Red Tingo) Insero, 2x White Cafea Floresco"))
assertEquals(
    [
        ("Red Albeo Americano", 1),
        ("Blue Albeo Americano", 1),
        ("Red Albeo Frondis", 1),
        ("Blue Albeo Frondis", 1),
        ("Beige Bruna Marmorea", 2),
        ("Olive Bruna Marmorea", 2),
    ],
    enumerate_frogs("(Red & Blue) Albeo Americano, (Red & Blue) Albeo Frondis, 2x (Beige & Olive) Bruna Marmorea"))
"""
assertEquals(
    [
        ("Aqua Callaina Nebula", 1),
        ("Blue Callaina Nebula", 1),
        ("White Callaina Nebula", 1),
        ("White Ceres Nebula", 1),
        ("Beige Ceres Nebula", 1),
        ("Aqua Albeo Nebula", 1),
        ("Aqua Caelus Nebula", 2),
    ],
    enumerate_frogs(
        "((Aqua, Blue, White) Callaina, (White, Beige) Ceres, Aqua Albeo, 2x Aqua Caelus) Nebula")
)
"""

reader = csv.reader(open('raw sets.csv'))
writer = csv.writer(open('massaged sets.csv', 'w'))
next(reader)  # skip header
for row in reader:
  frogs = enumerate_frogs(row[-1])
  if not frogs:
    print("couldn't enumerate:", row[-1])
    continue
  for frog in frogs:
    assert re.match("\\w+ \\w+ \\w+", frog[0])
    writer.writerow(row[:-1] + list(frog))
