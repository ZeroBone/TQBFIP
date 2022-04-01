import logging
import sympy
from qbf import QBF
from prime import next_prime

logger = logging.getLogger("prover")


def _poly_to_str(poly) -> str:
    return str(poly.as_expr())


def _to_poly_simple(result, gens):
    return sympy.Poly(result, *gens, domain=sympy.ZZ)


def _to_poly(result, initial_poly):
    return _to_poly_simple(result, initial_poly.gens).exclude()


def _linearity_operator(poly, v):
    return _to_poly(v * poly.subs(v, 1) + (1 - v) * poly.subs(v, 0), poly)


def _forall_operator(poly, v):
    return _to_poly(poly.subs(v, 0) * poly.subs(v, 1), poly)


def _exists_operator(poly, v):
    return _to_poly(poly.subs(v, 0) + poly.subs(v, 1), poly)


class ProofOperator:

    def __init__(self, variable: int = 1, linearizing_variable: int = 0):
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

    def is_first_operator(self) -> bool:
        return not self.is_linearity_operator() and self.v == 1

    def is_last_operator(self, qbf: QBF) -> bool:
        return self.v == qbf.get_variable_count() and self.lv == qbf.get_variable_count()

    def get_leftmost_not_yet_resolved_variable(self) -> int:
        return max(self.v, self.lv) + 1

    def next_quantifier_operator(self):
        return ProofOperator(self.v + 1)

    def previous_operator(self):

        if self.is_first_operator():
            return None

        if not self.is_linearity_operator():
            return ProofOperator(self.v - 1, self.v - 1)

        # we are dealing with a linearity operator
        # the previous operator may be both a quantifier
        # as well as a linearity operator
        return ProofOperator(self.v, self.lv - 1)

    def to_string(self, context: QBF) -> str:

        if self.lv != 0:
            return "L_{%s}" % context.get_name(self.lv)

        quantification = context.get_quantification(self.v)

        if quantification == QBF.Q_FORALL:
            return "A_{%s}" % context.get_name(self.v)
        else:
            assert quantification == QBF.Q_EXISTS
            return "E_{%s}" % context.get_name(self.v)


class Prover:

    def __init__(self, qbf: QBF, p: int):
        self.qbf = qbf
        self.p = p

    def get_value_of_entire_polynomial(self) -> int:
        raise NotImplementedError()

    def _get_operator_polynomial(self, operator: ProofOperator, random_choices: dict):
        raise NotImplementedError()

    def get_operator_polynomial(self, operator: ProofOperator, random_choices: dict):
        s = self._get_operator_polynomial(operator, random_choices)

        assert s.is_univariate or s.is_ground, "Prover provided a multivariate s polynomial"

        return s.trunc(self.p).exclude()


class HonestProver(Prover):

    def __init__(self, qbf: QBF):
        super().__init__(qbf, 0)

        self._polynomial_after_operator = {}

        cur_p = qbf.arithmetize_matrix()

        # iterate over the proof operator sequence, in reverse order
        for v in range(qbf.get_variable_count(), 0, -1):

            for variable_to_linearize in range(v, 0, -1):
                current_operator = ProofOperator(v, variable_to_linearize)

                assert current_operator not in self._polynomial_after_operator
                self._polynomial_after_operator[current_operator] = cur_p

                cur_p = _linearity_operator(cur_p, self.qbf.get_symbol(variable_to_linearize))
                # cur_p is now a polynomial where variable_to_linearize is linearized

            current_operator = ProofOperator(v)
            assert current_operator not in self._polynomial_after_operator
            self._polynomial_after_operator[current_operator] = cur_p

            quantification = qbf.get_quantification(v)

            if quantification == QBF.Q_FORALL:
                cur_p = _forall_operator(cur_p, self.qbf.get_symbol(v))
            elif quantification == QBF.Q_EXISTS:
                cur_p = _exists_operator(cur_p, self.qbf.get_symbol(v))
            else:
                assert False

            # cur_p is now a polynomial with the quantification applied

        self.p = qbf.get_lower_bound_for_protocol_prime()

        assert cur_p.is_ground, "Polynomial at the end of the protocol is not trivial"
        self.entire_polynomial_value = int(cur_p.LC())

        if self.entire_polynomial_value != 0:
            # qbf sentence is true
            while self.entire_polynomial_value % self.p == 0:
                self.p = next_prime(self.p)

            self.entire_polynomial_value %= self.p

        # prime p is not computed
        # it is a good idea to reduce all coefficients appearing in the polynomials
        # modulo p, to simplify further computations
        for op, poly in self._polynomial_after_operator.items():
            self._polynomial_after_operator[op] = poly.trunc(self.p)

    def get_value_of_entire_polynomial(self) -> int:
        return self.entire_polynomial_value

    def log_operator_polynomials(self):

        logger.info("Value of entire polynomial = %d", self.entire_polynomial_value)

        logger.info("Printing the operator followed by the "
                    "polynomial to which all further operators evaluate")

        # iterate over the proof operator sequence
        for v in range(1, self.qbf.get_variable_count() + 1):

            current_operator = ProofOperator(v)

            assert current_operator in self._polynomial_after_operator
            cur_p = self._polynomial_after_operator[current_operator]

            logger.info("%s: (degree %2s): %s",
                        current_operator.to_string(self.qbf),
                        cur_p.total_degree(),
                        _poly_to_str(cur_p))

            for lin_var in range(1, v + 1):

                current_operator = ProofOperator(v, lin_var)

                assert current_operator in self._polynomial_after_operator
                cur_p = self._polynomial_after_operator[current_operator]

                logger.info("%s: (degree %2s): %s",
                            current_operator.to_string(self.qbf),
                            cur_p.total_degree(),
                            _poly_to_str(cur_p))

    def _get_operator_polynomial(self, operator: ProofOperator, random_choices: dict):

        eval_subs = {}

        for variable, a in random_choices.items():

            if operator.is_linearity_operator_on(variable):
                continue

            eval_subs[self.qbf.get_symbol(variable)] = a

        poly = self._polynomial_after_operator[operator]

        return poly\
            .eval(eval_subs)\
            .as_poly(poly.gens)\
            .trunc(self.p)\
            .exclude()

    def eval_polynomial_after_operator(self, var_values: dict, operator: ProofOperator) -> int:

        poly = self._polynomial_after_operator[operator]

        gens = (v.symbol for v in self.qbf.get_variables())

        for variable, a in var_values.items():

            eval_subs = {self.qbf.get_symbol(variable): a}

            poly = _to_poly_simple(poly.eval(eval_subs), gens)

        return int(poly.LC()) % self.p

    def eval_polynomial_at_operator(self, var_values: dict, operator: ProofOperator = None) -> int:
        # operator = None means evaluate matrix arithmetization

        if operator is None:
            return self.eval_polynomial_after_operator(var_values, ProofOperator(
                self.qbf.get_variable_count(),
                self.qbf.get_variable_count()
            ))

        if operator.is_first_operator():
            return self.get_value_of_entire_polynomial()

        op = operator.previous_operator()

        assert op is not None

        return self.eval_polynomial_after_operator(var_values, op)
