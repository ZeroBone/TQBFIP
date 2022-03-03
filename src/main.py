import sympy


def _literal_to_variable(literal: int) -> int:
    assert literal != 0
    return literal if literal >= 1 else -literal


def _literal_to_index(literal: int) -> int:
    assert literal != 0
    return _literal_to_variable(literal) - 1


class QBFVariable:

    def __init__(self, quantification: bool, alias: str):
        self.quantification = quantification
        self.alias = alias
        self.symbol = sympy.symbols(self.alias)


class QBF:

    Q_EXISTS = False
    Q_FORALL = True

    def __init__(self):
        # True/False if universally/existentially quantified, indexed by variable number
        self._var = []
        self._matrix = []

    def add_clause(self, clause: set):

        for literal in clause:
            if not self._variable_defined(_literal_to_variable(literal)):
                raise RuntimeError("Variable %d is not defined" % _literal_to_variable(literal))

        self._matrix.append(clause)

    def add_variable(self, variable: int, quantification: bool, alias: str = None):
        assert variable >= 1

        if alias is None:
            alias = "x_%d" % variable

        var = QBFVariable(quantification, alias)

        if variable - 1 == len(self._var):
            self._var.append(var)
        else:
            self._var[variable - 1] = var

    def get_quantification(self, variable: int) -> bool:
        assert variable >= 1
        return self._var[variable - 1].quantification

    def _variable_defined(self, variable: int) -> bool:
        assert variable >= 1
        return variable <= len(self._var)

    def variable_count(self) -> int:
        return len(self._var)

    def to_latex(self) -> str:
        return " ".join([
            ("\\forall " if self._var[i].quantification == QBF.Q_FORALL else "\\exists ") + self._var[i].alias
            for i in range(self.variable_count())
        ]) + " : " + " \\wedge ".join([
            "(" + " \\vee ".join([
                ("\\overline{%s} " if literal < 0 else "%s") %
                self._var[_literal_to_index(literal)].alias for literal in sorted(clause, key=abs)
            ]) + ")" for clause in self._matrix
        ])


def linearity_operator(p, v):
    return (v * p.subs(v, 1) + (1 - v) * p.subs(v, 0)).simplify()


def forall_operator(p, v):
    return (p.subs(v, 0) * p.subs(v, 1)).simplify()


def exists_operator(p, v):
    return (p.subs(v, 0) + p.subs(v, 1)).simplify()


def construct_formula():

    qbf = QBF()

    qbf.add_variable(1, QBF.Q_FORALL, "x")
    qbf.add_variable(2, QBF.Q_EXISTS, "y")
    qbf.add_variable(3, QBF.Q_FORALL, "z")

    qbf.add_clause({1, -2, 3})
    qbf.add_clause({-1, 2, 3})

    return qbf


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
