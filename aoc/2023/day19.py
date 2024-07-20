from common import assertEqual
from common import submit
import re
import operator
import math


def parse_workflow(line):
  m = re.match('(\\w+){(.*)}', line)
  label = m.group(1)
  rules = [parse_rule(r) for r in m.group(2).split(',')]
  return label, rules


def parse_rule(rule_str):
  m = re.match('(([xmas])([<>])(\\d+):)?+(\\w+)', rule_str)
  sendto = m.group(5)
  if m.group(1):
    category = m.group(2)
    condition = m.group(3)
    threshold = int(m.group(4))
    return ((category, condition, threshold), sendto)
  else:
    return (None, sendto)


def parse_part(part_str):
  m = re.match('{(.*)}', part_str)
  return dict(parse_rating(r) for r in m.group(1).split(','))


def parse_rating(rating_str):
  m = re.match('([xmas])=(\\d+)', rating_str)
  score = int(m.group(2))
  return m.group(1), range(score, score+1)


def apply_workflow(label, part, workflows):
  # print(f'apply_workflow({label}, {part})')
  if label == 'R':
    return 0
  if label == 'A':
    return math.prod(len(score) for score in part.values())
  total = 0
  # print(workflows[label])
  for criteria, sendto in workflows[label]:
    if not criteria:
      return total + apply_workflow(sendto, part, workflows)
    category, op, threshold = criteria
    part_score = part[category]

    yes = dict(part)
    no = dict(part)
    if op == '<':
      yes[category] = range(part_score.start, min(part_score.stop, threshold))
      no[category] = range(max(part_score.start, threshold), part_score.stop)
    elif op == '>':
      yes[category] = range(max(part_score.start, threshold+1), part_score.stop)
      no[category] = range(part_score.start, min(part_score.stop, threshold+1))
    else:
      assert False
    if len(yes[category]) > 0:
      total += apply_workflow(sendto, yes, workflows)
    if len(no[category]) == 0:
      break
    part = no

  return total


def business_logic(workflows, parts):
  return sum(sum(s.start for s in p.values()) for p in parts
             if apply_workflow('in', p, workflows) > 0)


def day19(input):
  paragraphs = input.split('\n\n')
  input_workflows = paragraphs[0]
  workflows = dict(parse_workflow(line) for line in input_workflows.splitlines())
  # print(workflows)

  input_parts = paragraphs[1]
  parts = [parse_part(line) for line in input_parts.splitlines()]
  # print(parts)

  return business_logic(workflows, parts)


test_input = '''\
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}
'''
test_output = 19114

assertEqual(test_output, day19(test_input))


print('day19 answer:')
submit(day19(open('day19_input.txt', 'r').read()),
       expected=397643)
print()

# part2 complication
test_output = 167409079868000


def business_logic(workflows, parts):
  all_parts = dict((category, range(1, 4000+1)) for category in 'xmas')
  return apply_workflow('in', all_parts, workflows)


assertEqual(test_output, day19(test_input))


print('day19, part2 answer:')
submit(day19(open('day19_input.txt', 'r').read()),
       expected=132392981697081)
print()
