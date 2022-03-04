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

    def get_symbol(self, variable: int):
        assert variable >= 1
        return self._var[variable - 1].symbol

    def get_alias(self, variable: int):
        assert variable >= 1
        return self._var[variable - 1].alias

    def _variable_defined(self, variable: int) -> bool:
        assert variable >= 1
        return variable <= len(self._var)

    def variable_count(self) -> int:
        return len(self._var)

    def _literal_to_variable(self, literal):
        return self._var[_literal_to_index(literal)]

    def to_latex(self) -> str:
        return " ".join([
            ("\\forall " if self._var[i].quantification == QBF.Q_FORALL else "\\exists ") + self._var[i].alias
            for i in range(self.variable_count())
        ]) + " : " + " \\wedge ".join([
            "(" + " \\vee ".join([
                ("\\overline{%s} " if literal < 0 else "%s") %
                self._literal_to_variable(literal).alias for literal in sorted(clause, key=abs)
            ]) + ")" for clause in self._matrix
        ])

    def construct_p_phi(self):

        p_phi = 1

        for clause in self._matrix:
            prod = 1

            for literal in sorted(clause, key=abs):
                if literal >= 1:
                    prod *= (1 - self._literal_to_variable(literal).symbol)
                else:
                    prod *= self._literal_to_variable(literal).symbol

            p_phi *= 1 - prod

        return p_phi


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

    qbf = construct_formula()

    p = qbf.construct_p_phi()

    print(p)

    for v in range(qbf.variable_count(), 0, -1):

        print("Variables: %d" % v)
        print("Before linearization:", p.expand())

        for variable_to_linearize in range(v, 0, -1):
            p = linearity_operator(p, qbf.get_symbol(variable_to_linearize))
            print("Linearized %s:" % qbf.get_alias(variable_to_linearize), p.expand())

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            p = forall_operator(p, qbf.get_symbol(v))
        else:
            p = exists_operator(p, qbf.get_symbol(v))

        print("Applied quantification:", p)

    print("Final result:", p)


if __name__ == "__main__":
    main()
