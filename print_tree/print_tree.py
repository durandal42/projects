class Node(object):
  def __init__(self, name, left=None, right=None):
    self.name = name
    self.left = left
    self.right = right


def preorder(node):
  if not node: return
  yield node.name
  for name in preorder(node.left): yield name
  for name in preorder(node.right): yield name

ROOT = Node('A',
            Node('B',
                 Node('D'),
                 Node('E')),
            Node('C',
                 Node('F',
                      Node('H'),
                      Node('I')),
                 Node('G')))

for name in preorder(ROOT):
  print name

# TODO(durandal) ascii art