import itertools


def generate_ints(length):
  # no leading 0's, or even lone 0's as LHS tokens
  for x in range(10**(length - 1), 10**length):
    yield str(x)


def generate_lhs_skeletons(max_length):
  # For now, let's assume the LHS also has at least one operator
  # (otherwise LHS and RHS will have different numbers of digitis and no operator).
  for i in range(max_length):
    first_token_length = i + 1
    for j in range(max_length
                   - first_token_length - 1):
      second_token_length = j + 1
      for k in range(max_length
                     - first_token_length - 1
                     - second_token_length - 1):
        third_token_length = k + 1
        yield (first_token_length, second_token_length, third_token_length)
      yield (first_token_length, second_token_length)


def validate_lhs_skeleton(lhs_skeleton, length):
  max_lhs = '*'.join(str(10**i - 1) for i in lhs_skeleton)
  remaining_length = length - len(max_lhs) - 1
  min_rhs = 10**(remaining_length - 1)
  # print(f'{max_lhs} >? {min_rhs}')
  if (eval(max_lhs) < min_rhs):
    return False
  return True

OPERATORS = '+-*/'


def generate_lhs(lhs_skeleton):
  if len(lhs_skeleton) == 2:
    for lhs in itertools.product(
            generate_ints(lhs_skeleton[0]),
            OPERATORS,
            generate_ints(lhs_skeleton[1])):
      yield ''.join(lhs)
  elif len(lhs_skeleton) == 3:
    for lhs in itertools.product(
            generate_ints(lhs_skeleton[0]),
            OPERATORS,
            generate_ints(lhs_skeleton[1]),
            OPERATORS,
            generate_ints(lhs_skeleton[2])):
      yield ''.join(lhs)
  else:
    assert False


def generate_nerdles(length=8):
  # There's always one '=', and the rhs is an integer,
  # so we only have at most length-2 characters to play with on the LHS.
  skeletons = [s for s in generate_lhs_skeletons(length - 2)]
  skeletons.sort(key=lambda s: len(s))
  # print(skeletons)
  for lhs_skeleton in skeletons:
    # print('\tfleshing out skeleton:', lhs_skeleton)
    if not validate_lhs_skeleton(lhs_skeleton, length):
      # print("\t\tno possible flesh for skeleton")
      continue
    for lhs in generate_lhs(lhs_skeleton):
      try:
        rhs = eval(lhs)
      except ZeroDivisionError:
        continue
      if rhs < 0: continue
      rhs_int = int(rhs)
      nerdle = lhs + '=' + str(rhs_int)
      if rhs != rhs_int:
        continue
      if len(nerdle) != length:
        # print("rejected: [%s]" % nerdle)
        continue
      yield nerdle

# for now, assume length = 8
# there's a length = 6 variant, though
for n in generate_nerdles(8):
  # print("accepted: [%s]" % n)
  print(n)
