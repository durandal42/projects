from clues import *

evaluate(
    knowns={
        N: 0,
        G: 1, H: 1,
        D: 1, E: 1,
        O: 1,
        L: 0, R: 1,
        C: 1,
        B: 1, F: 0, J: 1, T: 0,
        M: 1,
        Z: 1,
        I: 0,
        P: 1, X: 0,
    },
    claims=[
        # N: There are more criminals than innocents in between Floyd and Isaac
        'num_criminals(right(F) & left(I)) > num_innocents(right(F) & left(I))',
        # G: There are no innocents in row 1 who neighbors Isaac
        'num_innocents(row(1) & neighbors(I)) == 0',
        # H: There are as many innocent painters are there are innocent singers
        'num_innocents(profession("painter")) == num_innocents(profession("singer"))',
        # D: Only 1 o the 2 innocents neighboring Nancy is Pam's neighbor
        'num_innocents(neighbors(N)) == 2 and num_innocents(neighbors(N) & neighbors(P)) == 1',
        # E: Only 1 of the 5 innocents neighoring Olive is a farmer
        'num_innocents(neighbors(O)) == 5 and num_innocents(neighbors(O) & profession("farmer")) == 1',
        # O: Rob is one of Zoe's 2 criminal neighbors
        'is_criminal(R) and num_criminals(neighbors(Z)) == 2',
        # L: Exactly 1 painter has a criminal directly above them
        'sum(1 for s in profession("painter") if num_criminals(above(s, directly=True)) == 1) == 1',
        # R: THere are more criminals in column B than column C
        'num_criminals(column(B)) > num_criminals(column(C))',
        # C: Zoe and Betty have an equal number of criminal neighbors
        'num_criminals(neighbors(Z)) == num_criminals(neighbors(B))',
        # F: Isaac and Zoe have an equal number of innocent neighbors
        'num_innocents(neighbors(I)) == num_innocents(neighbors(Z))',
        # M: There's an odd number of criminals neighboring Rob
        'num_criminals(neighbors(R)) % 2 == 1',
        # Z: Daniel and I have an equal number of innocent neighbors
        'num_innocents(neighbors(D)) == num_innocents(neighbors(Z))',
        # I: There's an odd number of innocents neighboring Pam
        'num_innocents(neighbors(P)) % 2 == 1',
        # Luigi is the only innocent in his row
        'num_innocents(row(3)) == 1',
    ])
