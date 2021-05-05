"""
One-off script to massage data.
From: https://pocketfrogs.fandom.com/wiki/Weekly_Sets
To: https://docs.google.com/spreadsheets/d/1YoPQylzi8C5pybXFLgRb3g7_i2WVCAccTgHPmFv1qeA/
"""

import csv
import re


def enumerate_frogs(frogs_desc):
  # print("\ninput:", frogs_desc)

  # Remove various "and"spellings, standardize on comma separation.
  for a in [", and", " and ", "& ", "; ", ", "]:
    frogs_desc = frogs_desc.replace(a, ",")

  # Look for clauses containing a parenthesized expression with no further
  # nesting. If found, expand them in place.
  # Repeat until this stops working.
  while True:
    clause_with_parenthesized_expr_regex = "[^(),]*\\(([^()]*)\\)[^(),]*"
    parenthesized_expr_regex = "\\([^()]*\\)"
    m = re.search(clause_with_parenthesized_expr_regex, frogs_desc)
    if m is None:
      break
    containing_clause = m.group(0)
    # print("containing_clause:", containing_clause)
    inner_expr = m.group(1)
    # print("inner_expr:", inner_expr)
    tokens = inner_expr.split(',')
    if len(tokens) == 1:
      # This was actually an annotation; drop it.
      expanded_tokens = [re.sub(parenthesized_expr_regex,
                                "", containing_clause).strip()]
    else:
      expanded_tokens = []
      for t in tokens:
        count_prefix_regex = "\\d+[Xx] "
        m = re.match(count_prefix_regex, t)
        count_prefix = ""
        if m:
          count_prefix = m.group(0)
          t = re.sub(count_prefix_regex, "", t)
        expanded_token = count_prefix + re.sub(parenthesized_expr_regex,
                                               t.strip(), containing_clause)
        # print("expanded_token:", expanded_token)
        expanded_tokens.append(expanded_token)
    expanded_clause = ",".join(expanded_tokens)
    # print("expanded_clause:", expanded_clause)
    frogs_desc = re.sub(clause_with_parenthesized_expr_regex,
                        expanded_clause, frogs_desc, count=1)
    # print("updated frogs_desc:", frogs_desc)

  frog_descs = frogs_desc.split(",")

  frogs = []
  for frog_desc in frog_descs:
    count = 1
    m = re.match("(?:(\\d+)[Xx] )?(\\w*) (\\w*) (\\w*)$", frog_desc)
    if not m:
      print("bad frog description:", frog_desc)
      return None
    count = (m.group(1) is None) and 1 or int(m.group(1))
    primary = m.group(2)
    secondary = m.group(3)
    pattern = m.group(4)
    frogs.append((primary, secondary, pattern, count))
  # print("counted:", frogs)

  return frogs


def assertEquals(expected, actual):
  if expected != actual:
    raise AssertionError("\n\texpected: %s;\n\tactual:   %s" %
                         (expected, actual))
assertEquals(
    [
        ("Glass", "Chroma", "Anura", 1),
    ],
    enumerate_frogs("Glass Chroma Anura"))

assertEquals(
    [
        ("Glass", "Chroma", "Anura", 2),
    ],
    enumerate_frogs("2x Glass Chroma Anura"))

assertEquals(
    [
        ("Green", "Chroma", "Bovis", 2),
        ("Green", "Chroma", "Velatus", 2),
        ("Green", "Chroma", "Marmorea", 2),
    ],
    enumerate_frogs("2x Green Chroma (Bovis, Velatus, and Marmorea)"))

assertEquals(
    [
        ("Olive", "Folium", "Insero", 2),
        ("Red", "Tingo", "Insero", 2),
        ("White", "Cafea", "Floresco", 2),
    ],
    enumerate_frogs("2x (Olive Folium, Red Tingo) Insero, 2x White Cafea Floresco"))
assertEquals(
    [
        ("Red", "Albeo", "Americano", 1),
        ("Blue", "Albeo", "Americano", 1),
        ("Red", "Albeo", "Frondis", 1),
        ("Blue", "Albeo", "Frondis", 1),
        ("Beige", "Bruna", "Marmorea", 2),
        ("Olive", "Bruna", "Marmorea", 2),
    ],
    enumerate_frogs("(Red & Blue) Albeo Americano, (Red & Blue) Albeo Frondis, 2x (Beige & Olive) Bruna Marmorea"))

assertEquals(
    [
        ("Aqua", "Callaina", "Nebula", 1),
        ("Blue", "Callaina", "Nebula", 1),
        ("White", "Callaina", "Nebula", 1),
        ("White", "Ceres", "Nebula", 1),
        ("Beige", "Ceres", "Nebula", 1),
        ("Aqua", "Albeo", "Nebula", 1),
        ("Aqua", "Caelus", "Nebula", 2),
    ],
    enumerate_frogs(
        "((Aqua, Blue, White) Callaina, (White, Beige) Ceres, Aqua Albeo, 2x Aqua Caelus) Nebula")
)

assertEquals(
    [
        ("Glass", "Chroma", "Gyrus", 4),
        ("Glass", "Chroma", "Puncti", 2),
        ("Glass", "Chroma", "Bulla", 2),
    ],
    enumerate_frogs("Glass Chroma (4x Gyrus, 2x Puncti, 2x Bulla)"))

reader = csv.reader(open('raw sets.csv'))
writer = csv.writer(open('massaged sets.csv', 'w'))

assert ['Name', 'Year', 'Week', 'Frogs Required'] == next(reader)  # header
writer.writerow(["Name", "Year", "Week", "Primary",
                 "Secondary", "Pattern", "Qty"])

for input_row in reader:
  frogs = enumerate_frogs(input_row[-1])
  for frog in frogs:
    output_row = input_row[:-1] + list(frog)
    print(output_row)
    writer.writerow(output_row)
