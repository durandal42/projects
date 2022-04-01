import random

dates_by_index = {
    67: "2022/04/01",
    66: "2022/03/31",
    65: "2022/03/30",
    64: "2022/03/29",
    63: "2022/03/28",
    62: "2022/03/27",
    61: "2022/03/26",
    60: "2022/03/25",
    59: "2022/03/24",
    58: "2022/03/23",
    57: "2022/03/22",
    56: "2022/03/21",
    55: "2022/03/20",
    54: "2022/03/19",
    53: "2022/03/18",
    52: "2022/03/17",
    51: "2022/03/16",
    50: "2022/03/15",
    49: "2022/03/14",
    48: "2022/03/13",
    47: "2022/03/12",
    46: "2022/03/11",
    45: "2022/03/10",
    44: "2022/03/09",
    43: "2022/03/08",
    42: "2022/03/07",
    41: "2022/03/06",
    40: "2022/03/05",
    39: "2022/03/04",
    38: "2022/03/03",
    37: "2022/03/02",
    36: "2022/03/01",
    35: "2022/02/28",
    34: "2022/02/27",
    33: "2022/02/26",
    32: "2022/02/25",
    31: "2022/02/24",
}

solutions_by_index = {
    67: ("MAUVE", "MINOR", "HANDY", "GOUGE"),
    66: ("BISON", "DECRY", "RIVET", "FAIRY"),
    65: ("MERIT", "TRUST", "TAROT", "GOOSE"),
    64: ("RELAY", "RIGHT", "MODEL", "BLEEP"),
    63: ("DROWN", "HIPPO", "DAIRY", "REACT"),
    62: ("FAIRY", "NERDY", "HONOR", "DEALT"),
    61: ("ENEMY", "FINCH", "BUYER", "GRAIN"),
    60: ("SKUNK", "POSIT", "BENCH", "CHILD"),
    59: ("WREAK", "GREED", "DIMLY", "WIDOW"),
    58: ("SNARE", "NERDY", "VINYL", "SCREW"),
    57: ("CHOIR", "STINT", "BADLY", "ANGRY"),
    56: ("SAVOR", "CHOKE", "FURRY", "PAGAN"),
    55: ("DROOL", "PRICK", "INPUT", "PHASE"),
    54: ("SLINK", "SCENE", "BUGGY", "SHACK"),
    53: ("ARBOR", "PRIED", "BISON", "PLACE"),
    52: ("ADMIT", "BLURT", "WINDY", "STOMP"),
    51: ("SLURP", "BOOTH", "PRONE", "SCONE"),
    50: ("LOWER", "DETER", "WHICH", "BELLE"),
    49: ("FRAUD", "AGENT", "TEMPO", "SWORN"),
    48: ("DRAFT", "DRAIN", "BANJO", "GUEST"),
    47: ("KARMA", "PUPIL", "CAULK", "HELLO"),
    46: ("AGATE", "ADORE", "MIDST", "SINEW"),
    45: ("HASTY", "SHEER", "SOLVE", "HOLLY"),
    44: ("FREER", "IDIOT", "MINUS", "TWIRL"),
    43: ("POPPY", "FRAIL", "DOZEN", "STIFF"),
    42: ("TWEAK", "NIGHT", "SONIC", "FLACK"),
    41: ("VOICE", "FORGO", "WIDER", "HOVEL"),
    40: ("LIKEN", "HASTY", "HEATH", "HUNKY"),
    39: ("NANNY", "AFFIX", "CLING", "STUFF"),
    38: ("CARVE", "METER", "OVINE", "SMEAR"),
    37: ("CABAL", "FROTH", "DATUM", "WOMEN"),
    36: ("QUERY", "DEBAR", "DEPOT", "NUTTY"),
    35: ("FRAIL", "DRAMA", "SKIRT", "HILLY"),
    34: ("PASTE", "CAPUT", "SKIFF", "CHOIR"),
    33: ("PEARL", "TOUGH", "BELLE", "JUNTO"),  # predates badword filter!
    32: ("VIXEN", "SHREW", "ALIGN", "QUILL"),
    31: ("BOAST", "MIGHT", "STILT", "FLIER"),
}


def daily_seed():
  # Since this function appears to return the integer number
  # of days since the Quordle origin, we can avoid almost all
  # of this by just using the Quordle index, appropriately offset.

  # bS = new Date("01/24/2022")
  origin = datetime.datetime(year=2022, month=1, day=24)
  # const S = new Date;
  now = datetime.now()
  # return (S.getTime() - bS.getTime() +
  #         (bS.getTimezoneOffset() - S.getTimezoneOffset()) * tS.minute)
  #         / Ne >> 0
  # tS.minute = 60 * 1e3
  # Ne = tS.day = 24 * 60 * 60 * 1e3
  # TODO: time zone offsets, if needed
  return (now - origin).total_seconds() / (24 * 60 * 60)


class JavaScriptRandom:
  def __init__(self, e=None):
    # e == null && (e = new Date().getTime()),
    if e is None:
      e = int(datetime.now().timestamp() * 1000)
    self.N = 624
    self.M = 397
    self.MATRIX_A = 2567483615
    self.UPPER_MASK = 2147483648
    self.LOWER_MASK = 2147483647
    # this.mt = new Array(this.N),
    self.mt = []  # we'll append as needed instead of pre-allocating the array
    self.mti = self.N + 1
    self.init_seed(e)

  def init_seed(self, e):
    # assume for now; all inputs to bitwise operators are non-negative
    # any time we see >>> 0, treat that as "coerce to unsigned 32 bit integer"

    # for (this.mt[0] = e >>> 0, this.mti = 1; this.mti < this.N; this.mti++) {
    self.mt.clear()
    self.mt.append(e)
    for mti in range(1, self.N):
      e = self.mt[-1] ^ self.mt[-1] >> 30
      self.mt.append((((e & 4294901760) >> 16) * 1812433253 <<
                      16) + (e & 65535) * 1812433253 + mti)
      # this.mt[this.mti] >>>= 0
      self.mt[-1] %= 2**32
    # the JS loop ends when the condition is false; e.g. mti >= N
    # the python loop ends on the last iteration of the range; e.g. mti = N - 1
    # so, fix it. and then, since we're fixing this in the end,
    # don't bother incrementing it above!
    self.mti = self.N

  def random_int(self):
    t = [0, self.MATRIX_A]

    if self.mti >= self.N:
      #         for (this.mti == this.N + 1 && this.init_seed(5489),
      if self.mti == self.N + 1:
        self.init_seed(5489)

      #         n = 0; n < this.N - this.M; n++)
      for n in range(self.N - self.M):
        e = self.mt[n] & self.UPPER_MASK | self.mt[n + 1] & self.LOWER_MASK
        self.mt[n] = self.mt[n + self.M] ^ e >> 1 ^ t[e & 1]

      #         for (; n < this.N - 1; n++)
      for n in range(n, self.N - 1):
        e = self.mt[n] & self.UPPER_MASK | self.mt[n + 1] & self.LOWER_MASK
        self.mt[n] = self.mt[n + (self.M - self.N)] ^ e >> 1 ^ t[e & 1]

      e = self.mt[self.N - 1] & self.UPPER_MASK | self.mt[0] & self.LOWER_MASK
      self.mt[self.N - 1] = self.mt[self.M - 1] ^ e >> 1 ^ t[e & 1]
      self.mti = 0

    e = self.mt[self.mti]
    self.mti += 1
    e ^= e >> 11
    e ^= e << 7 & 2636928640
    e ^= e << 15 & 4022730752
    e ^= e >> 18
    e %= 2**32
    return e

  def random_int31(self):
    return self.random_int() >> 1


print("Loading Quordle wordbank...")
BADWORDS = set("GYPSY GIPSY MAMMY AGORA SLAVE HUSSY JUNTA JUNTO".split())
WORDBANK = sorted([word.strip().upper()
                   for word in open("wordlists/legal-targets.txt")])
print("\tQuordle wordbank size:", len(WORDBANK))
print("\tQuordle badwords:", len(BADWORDS))


def select_words(seed, n, badwords=None):
  if badwords is None:
    if n > 33:
      # badwords filtering was added some time after day 33,
      # on which JUNTO was a target word
      badwords = BADWORDS
    else:
      badwords = []
  r = JavaScriptRandom(seed)
  # Throw away four random numbers immediately:
  for _ in range(4):
    r.random_int31()
  t = (None,) * 4
  # Retry until we get uniqe and non-bad words:
  while (len(set(t)) < len(t) or any(True for w in t if w in badwords)):
    t = tuple([WORDBANK[r.random_int31() % len(WORDBANK)] for _ in range(4)])
  return t


def test_vs_observed():
  for i, s in solutions_by_index.items():
    calculated = select_words(i, 4)
    print(f"Calculated: {calculated}, Actual: {s}, Match: {calculated==s}")


if __name__ == '__main__':
  test_vs_observed()
