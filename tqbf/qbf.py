import sympy

from prime import next_prime


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
        self.symbol = sympy.symbols(self.alias, integer=True)

    def get_latex_symbol(self, b_index: int) -> str:

        latex_op_sym = r"\prod" if self.quantification == QBF.Q_FORALL else r"\sum"

        return "%s_{b_{%d}=0}^1" % (latex_op_sym, b_index)


def _intersperse(arr: list, separator) -> list:
    result = [separator] * (len(arr) * 2 - 1)
    result[0::2] = arr
    return result


class QBF:

    _var: list[QBFVariable]
    Q_EXISTS = False
    Q_FORALL = True

    def __init__(self):
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

    def get_alias(self, variable: int) -> str:
        assert variable >= 1
        return self._var[variable - 1].alias

    def _variable_defined(self, variable: int) -> bool:
        assert variable >= 1
        return variable <= len(self._var)

    def get_variable_count(self) -> int:
        return len(self._var)

    def _literal_to_variable(self, literal):
        return self._var[_literal_to_index(literal)]

    def to_latex_array(self) -> list:
        return [
            ("\\forall " if self._var[i].quantification == QBF.Q_FORALL else "\\exists ") + self._var[i].alias
            for i in range(self.get_variable_count())
        ] + [":"] + _intersperse([
            "(" + " \\vee ".join([
                ("\\overline{%s}" if literal < 0 else "{%s}") %
                self._literal_to_variable(literal).alias for literal in sorted(clause, key=abs)
            ]) + ")" for clause in self._matrix
        ], " \\wedge ")

    def arithmetize_matrix(self):

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

    def _latex_clause_arithmetization(self, clause) -> str:

        return "1 - " + " ".join([
            ("(1 - %s)" if literal >= 1 else "%s") % self._literal_to_variable(literal).alias
            for literal in sorted(clause, key=abs)
        ])

    def get_matrix_arithmetization_latex_array(self):

        return _intersperse(
            ["&(%s)" % self._latex_clause_arithmetization(clause) for clause in self._matrix],
            "\\cdot \\\\"
        )

    def get_arithmetization_latex_array(self):

        return [
            v.get_latex_symbol(i + 1) for i, v in enumerate(self._var)
        ] + [
            r"P_{\varphi}(%s)" % ",".join(("b_{%d}" % i for i in range(1, self.get_variable_count() + 1))),
            r"\neq 0"
        ]

    def compute_prime_for_protocol(self):
        return next_prime(1 << self.get_variable_count())

    def get_clause_count(self) -> int:
        return len(self._matrix)
