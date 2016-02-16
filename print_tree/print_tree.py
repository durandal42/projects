class Node(object):
  def __init__(self, name, left=None, right=None):
    self.name = name
    self.left = left
    self.right = right

'''
States:
0 - before first child
1 - seeing first child now
2 - between first and second child
3 - seeing second child now
4 - past second child

To generalize past 2 children, would probably want to collapse into:
- more children remain
- seeing child now
- no more children remain
'''

def preorder_directory(node, states=[]):
  if not node: return
  yield None, states
  if states: states[-1] += 1
  yield node.name, states
  if states: states[-1] += 1
  states += [0]
  for child in [node.left, node.right]:
    for n, op in preorder_directory(child, states): yield n, op
  del states[-1]

def print_directory_tree(node):
  for name, states in preorder_directory(node):
    line = ''
    for op in states:
      if op in [1, 3]:
        line += '+-'
      elif op in [0, 2]:
        line += '| '
      elif op == 4:
        line += '  '
      else:
        line += str(op) + " "
    if name: line += name
    print line

ROOT = Node('A',
            Node('B',
                 Node('D'),
                 Node('E')),
            Node('C',
                 Node('F',
                      Node('H'),
                      Node('I')),
                 Node('G')))

print_directory_tree(ROOT)
