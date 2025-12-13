from clues import *

evaluate({
    'B': 0,
    'D': 0, 'H': 0, 'M': 0,
    'R': 0,
    'T': 1, 'Z': 0,
    'V': 1,
    'I': 1,
    'K': 0, 'L': 0, 'P': 1, 'S': 0, 'W': 0, 'X': 1,
    'C': 0,
    'O': 0,
},
    [
    # Gary and Isaac have 3 innocent neighbors in common
    "innocents([D,H,M]) == 3",
    # Hank and Zoe have an equal number of criminal neighbors
    "criminals([C,E,G,I,L,O]) == criminals([S,T,X])",
    # There's an odd number of criminals neighboring Xena
    "criminals([R,S,T,W,Z]) % 2 == 1",
    # Only 1 of the 2 innocents neighboring Vera is on the edges
    "innocents([P,R,W]) == 2 and innocents([P,W]) == 1",
    # proved: R is innocent
    # Tom is one of 2 criminals in row 4
    "criminals([P,R,S,T]) == 2 and criminals([T]) == 1",
    # proved: T is criminal
    # proved: Z is innocent
    # Xena and Ben have an equal number of criminal neighbors
    "criminals([R,S,T,W,Z]) == criminals([C,F,G])",
    # There are as many criminal painters are there are criminal singers.
    "criminals([P,S]) == criminals([M,V])",
    # proved: V is criminal
    # V: Eve and I have an equal number of criminal neighbors
    "criminals([P,R,W]) == criminals([D,H,I])",
    # proved: I is criminal
    # Exactly 3 of Rob's 5 innocent neighbors also neighbor Lisa
    "innocents([K,L,M,P,S,V,W,X]) == 5 and innocents([K,M,P,S]) == 3",
    # proved: K is innocent
    # proved: L is innocent
    # proved: P is criminal
    # proved: S is innocent
    # proved: W is innocent
    # proved: X is criminal
    # There's an odd number of innocents on the edges.
    "innocents([B,C,D,E,I,O,T,Z,X,W,V,P,K,F]) % 2 == 1",
    # proved: C is innocent
    # There are more criminal builders than criminal coders
    "criminals([C,F,G]) > criminals([D,H,O])",
    # # proved: O is innocent
    # # There are more innocents than criminals on the edges
    "innocents([B,C,D,E,I,O,T,Z,X,W,V,P,K,F]) > "
    "criminals([B,C,D,E,I,O,T,Z,X,W,V,P,K,F])",
])
