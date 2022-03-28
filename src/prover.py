import logging
import sympy
from qbf import QBF

logger = logging.getLogger("prover")


def _poly_to_str(poly) -> str:
    return str(poly.as_expr())


def _to_poly(result, initial_poly, p: int):

    return sympy.Poly(result, initial_poly.gens, domain=sympy.ZZ)\
        .trunc(p)\
        .exclude()


def linearity_operator(poly, v, p: int):
    return _to_poly(v * poly.subs(v, 1) + (1 - v) * poly.subs(v, 0), poly, p)


def forall_operator(poly, v, p: int):
    return _to_poly(poly.subs(v, 0) * poly.subs(v, 1), poly, p)


def exists_operator(poly, v, p: int):
    return _to_poly(poly.subs(v, 0) + poly.subs(v, 1), poly, p)


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

    def is_linearity_operator(self) -> bool:
        return self.lv != 0

    def get_primary_variable(self) -> int:

        if self.is_linearity_operator():
            return self.lv

        return self.v

    def to_string(self, context: QBF) -> str:

        if self.lv != 0:
            return "L_{%s}" % context.get_alias(self.lv)

        quantification = context.get_quantification(self.v)

        if quantification == QBF.Q_FORALL:
            return "A_{%s}" % context.get_alias(self.v)
        else:
            assert quantification == QBF.Q_EXISTS
            return "E_{%s}" % context.get_alias(self.v)


class Prover:

    def __init__(self, qbf: QBF, p: int):
        self.qbf = qbf
        self.p = p

    def get_value_of_entire_polynomial(self) -> int:
        raise NotImplementedError()

    def _get_operator_polynomial(self, operator: ProofOperator, verifiers_random_choices: dict):
        raise NotImplementedError()

    def get_operator_polynomial(self, operator: ProofOperator, verifiers_random_choices: dict):

        s = self._get_operator_polynomial(operator, verifiers_random_choices)

        assert s.is_univariate or s.is_ground, "Prover provided a multivariate s polynomial"

        return s.trunc(self.p).exclude()


class HonestProver(Prover):

    def __init__(self, qbf: QBF, p: int):
        super().__init__(qbf, p)

        polynomial_after_operator = {}

        cur_p = qbf.arithmetize_matrix()

        logger.info("Printing (in reverse order) the operator followed by the "
                    "polynomial to which all further operators evaluate")

        # iterate over the proof operator sequence, in reverse order
        for v in range(qbf.get_variable_count(), 0, -1):

            for variable_to_linearize in range(v, 0, -1):
                current_operator = ProofOperator(v, variable_to_linearize)
                polynomial_after_operator[current_operator] = cur_p

                logger.info("%s: %s", current_operator.to_string(qbf), _poly_to_str(cur_p))

                cur_p = linearity_operator(cur_p, self.qbf.get_symbol(variable_to_linearize), self.p)
                # cur_p is now a polynomial where variable_to_linearize is linearized

            current_operator = ProofOperator(v)
            polynomial_after_operator[current_operator] = cur_p

            logger.info("%s: %s", current_operator.to_string(qbf), _poly_to_str(cur_p))

            quantification = qbf.get_quantification(v)

            if quantification == QBF.Q_FORALL:
                cur_p = forall_operator(cur_p, self.qbf.get_symbol(v), self.p)
            else:
                assert quantification == QBF.Q_EXISTS
                cur_p = exists_operator(cur_p, self.qbf.get_symbol(v), self.p)

            # cur_p is now a polynomial with the quantification applied

        assert cur_p.is_ground, "Polynomial at the end of the protocol is not trivial"
        self.entire_polynomial_value = int(cur_p.LC()) % self.p

        logger.info("Value of entire polynomial = %d", self.entire_polynomial_value)

        self._polynomial_after_operator = polynomial_after_operator

    def get_value_of_entire_polynomial(self) -> int:
        return self.entire_polynomial_value

    def _get_operator_polynomial(self, operator: ProofOperator, random_choices: dict):

        eval_subs = {}

        for variable, a in random_choices.items():

            if operator.is_linearity_operator_on(variable):
                continue

            eval_subs[self.qbf.get_symbol(variable)] = a

        return self._polynomial_after_operator[operator].eval(eval_subs)
