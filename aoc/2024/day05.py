from common import assertEqual
from common import submit


def parse_input(input):
  sections = input.split("\n\n")
  rule_section, update_section = sections[0], sections[1]
  rules = [tuple(int(page) for page in line.split("|")) for line in rule_section.splitlines()]
  updates = [[int(page) for page in line.split(",")] for line in update_section.splitlines()]

  return rules, updates


def day05(input):
  rules, updates = parse_input(input)
  rules = set(rules)
  result = 0
  for update in updates:
    if not any((p2, p1) in rules for p1, p2 in zip(update[:-1], update[1:])):
      result += update[len(update)//2]
  return result


test_input = '''\
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
'''
test_output = 143

assertEqual(([(47, 53)], [[75, 47, 61, 53, 29]]), parse_input('''\
47|53

75,47,61,53,29
'''))

assertEqual(test_output, day05(test_input))


print('day05 answer:')
submit(day05(open('day05_input.txt', 'r').read()),
       expected=4996)
print()
