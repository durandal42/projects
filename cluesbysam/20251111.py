
evaluate(
    knowns={
        G: 0,
        H: 0, N: 0,
        D: 1, S: 1, X: 1,
        E: 1, M: 1,
        R: 0, W: 1,
        C: 1,
        V: 1,
        F: 1,
        I: 1,
        P: 1,
        T: 1,
        O: 1,
        Z: 1,
    },
    claims=[
        # G: Exactly 2 of the 3 innocents neighboring me are in between Denis and Xena
        'num_innocents(neighbors(G)) == 3 and '
        'num_innocents(neighbors(G) & below(D) & above(X)) == 2',
        # H: Salil is one of 3 criminals in column C
        'is_criminal(S) and '
        'num_criminals(column(C)) == 3',
        # S: Painter is the only profession with exactly 2 innocents
        'num_innocents(profession("painter")) == 2 and '
        'not any(num_innocents(profession(p)) == 2 for p in set(PROFESSIONS) if p != "painter")',
        # E: Exactly 1 innocent above Wally is neighboring Salil
        'num_innocents(above(W) & neighbors(S)) == 1',
        # W: Each column has at least 3 criminals
        'all(num_criminals(column(c)) >= 3 for c in "ABCD")',
        # C: There are more criminal than innocent builders
        'num_criminals(profession("builder")) > num_innocents(profession("builder"))',
        # V: Freya has exactly 2 innocent neighbors
        'num_innocents(neighbors(F)) == 2',
        # F: Both innocents in row 2 are connected
        'num_innocents(row(2)) == 2 and '
        'connected(innocents(row(2)))',
        # I: There's an odd number of criminals above Vince
        'num_criminals(above(V)) % 2 == 1',
        # P: Vince has more innocent neighbors than Zoe
        'num_innocents(neighbors(V)) > num_innocents(neighbors(Z))',
        # T: Isaac and Zoe have an equal number of criminal neighbors
        'num_criminals(neighbors(I)) == num_criminals(neighbors(Z))',
        # O: only one column has exactly 1 innocent
        'sum(1 for c in "ABCD" if num_innocents(column(c)) == 1) == 1',
        # Z: There are no innocents in the corners
        'num_innocents(corners()) == 0',

    ])
