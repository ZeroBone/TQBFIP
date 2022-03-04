from qbf import QBF


def linearity_operator(p, v):
    return v * p.subs(v, 1) + (1 - v) * p.subs(v, 0)


def forall_operator(p, v):
    return p.subs(v, 0) * p.subs(v, 1)


def exists_operator(p, v):
    return p.subs(v, 0) + p.subs(v, 1)


class Prover:

    def __init__(self, qbf: QBF):
        self.qbf = qbf

    def get_linearized_polynomial(self, variable: int, cur_p):
        pass

    def get_forall_polynomial(self, variable: int, cur_p):
        pass

    def get_exists_polynomial(self, variable: int, cur_p):
        pass


class HonestProver(Prover):

    def __init__(self, qbf: QBF):
        super().__init__(qbf)

    def get_linearized_polynomial(self, variable: int, cur_p):
        return linearity_operator(cur_p, self.qbf.get_symbol(variable))

    def get_forall_polynomial(self, variable: int, cur_p):
        return forall_operator(cur_p, self.qbf.get_symbol(variable))

    def get_exists_polynomial(self, variable: int, cur_p):
        return exists_operator(cur_p, self.qbf.get_symbol(variable))
