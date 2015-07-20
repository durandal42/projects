import random
import re

def parse_grammar_file(filename):
  symbols = {}
  root = None
  current_rhs = None
  for line in open(filename):
    line = line.strip()
    if not line: continue

    if line[0] == '#':
      symbol_name = line[1:]
      if not root:
        root = symbol_name
      current_rhs = []
      symbols[symbol_name] = current_rhs
    else:
      current_rhs.append(line.split('#')[0].strip())

  return symbols, '{%s}' % root

def random_cfg_string(symbols, root, rng=random.randrange):
  while True:
    m = re.search("{(\w+)}", root)
    if not m: return root
    options = symbols[m.group(1)]
    choice = options[rng(len(options))]
    root = (root[:m.start()] +
            random_cfg_string(symbols, choice, rng) +
            root[m.end():])

if __name__ == '__main__':
  import sys
  symbols, root = parse_grammar_file(sys.argv[1])

  NUM_SAMPLES = 0
  if NUM_SAMPLES: print '%d sample CFG outputs:' % NUM_SAMPLES
  for i in xrange(NUM_SAMPLES):
    print random_cfg_string(symbols, root)
