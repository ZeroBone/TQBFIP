import sympy


def linearity_operator(p, v):
    return (v * p.subs(v, 1) + (1 - v) * p.subs(v, 0)).simplify()


def forall_operator(p, v):
    return (p.subs(v, 0) * p.subs(v, 1)).simplify()


def exists_operator(p, v):
    return (p.subs(v, 0) + p.subs(v, 1)).simplify()


def main():
    x, y, z = sympy.symbols("x y z")

    p_phi = (1 - (1-x) * y * (1-z)) * (1 - x * (1-y) * (1-z))

    l_3 = linearity_operator(p_phi, z).expand()
    l_23 = linearity_operator(l_3, y).expand()
    l_123 = linearity_operator(l_23, x).expand()

    print(l_3)
    print(l_23)
    print(l_123)

    fa_l_123 = forall_operator(l_123, z)
    print("Forall_3", fa_l_123)

    l_2_fa_l_123 = linearity_operator(fa_l_123, y).expand()
    l_12_fa_l_123 = linearity_operator(l_2_fa_l_123, x).expand()

    print(l_2_fa_l_123)
    print(l_12_fa_l_123)

    ex_l_12_fa_l_123 = exists_operator(l_12_fa_l_123, y)
    print("Exists_2", ex_l_12_fa_l_123)

    l_1_ex_l_12_fa_l_123 = linearity_operator(ex_l_12_fa_l_123, x)
    print(l_1_ex_l_12_fa_l_123)


if __name__ == "__main__":
    main()
