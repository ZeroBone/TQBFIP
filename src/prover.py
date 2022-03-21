from qbf import QBF


def linearity_operator(p, v):
    return v * p.subs(v, 1) + (1 - v) * p.subs(v, 0)


def forall_operator(p, v):
    return p.subs(v, 0) * p.subs(v, 1)


def exists_operator(p, v):
    return p.subs(v, 0) + p.subs(v, 1)


class ProofOperator:

    def __init__(self, variable: int, linearizing_variable: int = 0):
        assert variable >= 1
        self.v = variable
        self.lv = linearizing_variable  # = 0 if we are applying quantification to the variable

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProofOperator):
            return False
        return (self.v, self.lv) == (o.v, o.lv)

    def __hash__(self) -> int:
        return hash((self.v, self.lv))

    def __str__(self):
        return "(%d, %d)" % (self.v, self.lv)

    def is_linearity_operator_on(self, variable: int) -> bool:
        assert variable != 0
        return self.lv == variable

    def to_string(self, context: QBF, latex: bool = False) -> str:

        if self.lv != 0:
            return "L_{%s}" % context.get_alias(self.lv)

        quantification = context.get_quantification(self.v)

        if quantification == QBF.Q_FORALL:
            if latex:
                return "\\forall_{%s}" % context.get_alias(self.v)
            return "A_{%s}" % context.get_alias(self.v)
        else:
            assert quantification == QBF.Q_EXISTS
            if latex:
                return "\\exists_{%s}" % context.get_alias(self.v)
            return "E_{%s}" % context.get_alias(self.v)


class Prover:

    def __init__(self, qbf: QBF, p: int):
        self.qbf = qbf
        self.p = p

    def get_value_of_entire_polynomial(self) -> int:
        raise NotImplementedError()

    def get_operator_polynomial(self, operator: ProofOperator, verifiers_random_choices: dict):
        raise NotImplementedError()


class HonestProver(Prover):

    def __init__(self, qbf: QBF, p: int):
        super().__init__(qbf, p)

        polynomial_after_operator = {}

        cur_p = qbf.arithmetize_matrix()

        for v in range(qbf.get_variable_count(), 0, -1):

            print("Variables: %d" % v)
            print("Before linearization:", cur_p.expand())

            for variable_to_linearize in range(v, 0, -1):

                polynomial_after_operator[ProofOperator(v, variable_to_linearize)] = cur_p

                cur_p = linearity_operator(cur_p, self.qbf.get_symbol(variable_to_linearize))
                print("Linearized %s:" % qbf.get_alias(variable_to_linearize), cur_p.expand())

            polynomial_after_operator[ProofOperator(v)] = cur_p

            quantification = qbf.get_quantification(v)

            if quantification == QBF.Q_FORALL:
                cur_p = forall_operator(cur_p, self.qbf.get_symbol(v))
            else:
                assert quantification == QBF.Q_EXISTS
                cur_p = exists_operator(cur_p, self.qbf.get_symbol(v))

            print("Applied quantification:", cur_p)

        for k in polynomial_after_operator.keys():
            print("%s -> %s" % (qbf.get_alias(k.v), k.to_string(qbf)), polynomial_after_operator[k])

        self.entire_polynomial_value = int(cur_p)

        print("Value of entire polynomial = %d" % self.entire_polynomial_value)

        self._polynomial_after_operator = polynomial_after_operator

    def get_value_of_entire_polynomial(self) -> int:
        return self.entire_polynomial_value

    def get_operator_polynomial(self, operator: ProofOperator, random_choices: dict):

        polynomial_after_operator = self._polynomial_after_operator[operator]

        for variable, a in random_choices.items():

            if operator.is_linearity_operator_on(variable):
                continue

            polynomial_after_operator = polynomial_after_operator.subs(
                self.qbf.get_symbol(variable),
                a
            )

        return polynomial_after_operator
