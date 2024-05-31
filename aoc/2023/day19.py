from common import assertEqual
from common import submit
import re
import operator


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
  return m.group(1), int(m.group(2))


SUPPORTED_OPS = {'<': operator.lt, '>': operator.gt}
FINAL_WORKFLOWS = {'A': True, 'R': False}


def apply_workflow(label, part, workflows):
  if label in FINAL_WORKFLOWS:
    return FINAL_WORKFLOWS[label]
  for criteria, sendto in workflows[label]:
    if not criteria:
      return apply_workflow(sendto, part, workflows)
    category, condition, threshold = criteria
    op = SUPPORTED_OPS[condition]
    if op(part[category], threshold):
      return apply_workflow(sendto, part, workflows)
  assert False


def day19(input):
  paragraphs = input.split('\n\n')
  input_workflows = paragraphs[0]
  workflows = dict(parse_workflow(line) for line in input_workflows.splitlines())
  # print(workflows)

  input_parts = paragraphs[1]
  parts = [parse_part(line) for line in input_parts.splitlines()]
  # print(parts)

  return sum(sum(p.values()) for p in parts if apply_workflow('in', p, workflows))


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
