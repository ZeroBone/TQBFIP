from qbf import QBF


def linearity_operator(p, v):
    return v * p.subs(v, 1) + (1 - v) * p.subs(v, 0)


def forall_operator(p, v):
    return p.subs(v, 0) * p.subs(v, 1)


def exists_operator(p, v):
    return p.subs(v, 0) + p.subs(v, 1)


class ProofOperator:

    def __init__(self, variable: int, linearizing_variable: int = 0):
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


class Prover:

    def __init__(self, qbf: QBF, p: int):
        self.qbf = qbf
        self.p = p

    def get_operator_polynomial(self, operator: ProofOperator):
        raise NotImplementedError()


class HonestProver(Prover):

    def __init__(self, qbf: QBF, p: int):
        super().__init__(qbf, p)

        proof_operators = {}

        cur_p = qbf.arithmetize_matrix()

        print(cur_p)

        for v in range(qbf.variable_count(), 0, -1):

            print("Variables: %d" % v)
            print("Before linearization:", cur_p.expand())

            for variable_to_linearize in range(v, 0, -1):
                cur_p = linearity_operator(cur_p, self.qbf.get_symbol(variable_to_linearize))
                print("Linearized %s:" % qbf.get_alias(variable_to_linearize), cur_p.expand())

                proof_operators[ProofOperator(v, variable_to_linearize)] = cur_p

            quantification = qbf.get_quantification(v)

            if quantification == QBF.Q_FORALL:
                cur_p = forall_operator(cur_p, self.qbf.get_symbol(v))
            else:
                cur_p = exists_operator(cur_p, self.qbf.get_symbol(v))

            proof_operators[ProofOperator(v)] = cur_p

            print("Applied quantification:", cur_p)

        print("Final result:", cur_p)
        for k in proof_operators.keys():
            print(k, proof_operators[k])

    def get_operator_polynomial(self, operator: ProofOperator):
        pass
