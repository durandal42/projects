# debt = (balance, interest rate, minimum payment)


def pay_monthly_debt(debt, available):
  b, i, m = debt
  assert available >= m
  payment = min(b, available)
  b -= payment
  available -= payment
  debt = b, i, m
  return debt, available


def accrue_monthly_interest(debt):
  b, i, m = debt
  b *= 1.0 + i / 100.0 / 12.0
  debt = b, i, m
  return debt


def pay_monthly_debts(debts, available):
  minimums = sum(d[2] for d in debts)
  assert available >= minimums
  surplus = available - minimums
  new_debts = []
  for d in debts:
    new_d, surplus = pay_monthly_debt(d, surplus + d[2])
    if new_d[0] > 0:
      new_debts.append(new_d)
  assert surplus >= 0
  return new_debts, surplus


def accrue_interest(debts):
  new_debts = []
  for d in debts:
    new_d = accrue_monthly_interest(d)
    new_debts.append(new_d)
  return new_debts


def pay_debts(debts, available, verbose=True):
  months, paid = 0, 0
  if verbose:
    print debts
  while debts:
    debts_paid, surplus = pay_monthly_debts(debts, available)
    if surplus > 0:
      if verbose:
        print "had $%d left over in month %d" % (surplus, months)
    paid += available - surplus
    months += 1
    debts_after = accrue_interest(debts_paid)
    if len(debts) <= len(debts_after) and debts[0][0] <= debts_after[0][0]:
      if verbose:
        print "not making progress on primary debt; can never pay it off"
      return False
    debts = debts_after
  if verbose:
    print "paid off in %d months, paying %d in total" % (months, paid)
  return True


def snowball(debts):
  return sorted(debts, key=lambda d: d[0])


def avalanche(debts):
  return sorted(debts, key=lambda d: -d[1])


def emily_lizard(debts):
  snowballed = snowball(debts)
  return snowballed[:1] + avalanche(snowballed[1:])


def compare_strategies(debts, available):
  print debts
  print "initial balance:", sum(d[0] for d in debts)
  print
  print "snowball:"
  pay_debts(snowball(debts), available)
  print
  print "avalanche:"
  pay_debts(avalanche(debts), available)
  print
  print "emily lizard:"
  pay_debts(emily_lizard(debts), available)
  print
  print


import itertools


def find_cusp(debts):
  for a in itertools.count(sum(d[2] for d in debts)):
    if pay_debts(debts, a, verbose=False):
      return a


def compare_cusps(debts):
  print "avalanche cusp:", find_cusp(avalanche(debts))
  print "snowball cusp:", find_cusp(snowball(debts))
  print "emily_lizard cusp:", find_cusp(emily_lizard(debts))

# https://www.moneycrashers.com/best-way-pay-off-debt-snowball-avalanche-snowflaking/
sample_data = [(700, 18, 17.5), (3000, 25, 92.5),
               (8000, 5, 85), (10000, 8, 203)]
sample_surplus = sum(d[2] for d in sample_data) + 100

compare_strategies(sample_data, sample_surplus)
compare_cusps(sample_data)

# https://www.daveramsey.com/blog/debt-snowball-vs-debt-avalanche
sample_data = [(20000, 20, 0), (9000, 17, 0), (10000, 5, 0),
               (16000, 4.25, 0), (2000, 4, 0)]
# snowball can't recover with 785 or less, emily_lizard can't recover with
# 461 or less
sample_surplus = 1000

compare_strategies(sample_data, sample_surplus)
compare_cusps(sample_data)

# https://www.forbes.com/sites/robertberger/2017/07/20/debt-snowball-versus-debt-avalanche-what-the-academic-research-shows/#6c621c591454
sample_data = [(3500, 17.99, 90), (7500, 18.00, 150), (10000, 7.50, 70),
               (7000, 8.50, 55), (4500, 6.5, 200), (1000, 10.05, 30)]
sample_surplus = 800

compare_strategies(sample_data, sample_surplus)
compare_cusps(sample_data)
