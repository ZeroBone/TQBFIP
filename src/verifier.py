from random import Random
import logging
from qbf import QBF
from prover import Prover, ProofOperator


VERIFIER_DEFAULT_SEED = 0xcafe + 0xbeef

logger = logging.getLogger("protocol")


class ProtocolObserver:

    def __init__(self):
        self.p = None

    def on_handshake(self, p: int, initial_c: int):
        raise NotImplementedError()

    def on_new_round(self,
                     current_operator: ProofOperator,
                     s,
                     prev_c: int,
                     new_rc: dict,
                     new_c: int,
                     prev_var_rc: int = None):
        raise NotImplementedError()

    def on_terminated(self, accepted: bool):
        raise NotImplementedError()


class DummyObserver(ProtocolObserver):

    def __init__(self):
        super().__init__()

    def on_handshake(self, p: int, initial_c: int):
        pass

    def on_new_round(self,
                     current_operator: ProofOperator,
                     s,
                     prev_c: int,
                     new_rc: dict,
                     new_c: int,
                     prev_var_rc: int = None):
        pass

    def on_terminated(self, accepted: bool):
        pass


def _log_random_choices(qbf: QBF, random_choices):
    log_str = ", ".join(("%s := %d" % (qbf.get_name(var), val) for var, val in random_choices.items()))
    logger.info("[V]: Random choices: %s", log_str if log_str else "none")


def _poly_to_str(poly) -> str:
    return str(poly.as_expr())


# evaluate univariate polynomial s at point x
def evaluate_s(s, x: int, p: int) -> int:
    assert s.is_univariate or s.is_ground
    return int(s.eval(x).as_poly(s.gens).LC()) % p


def run_verifier(qbf: QBF, /, prover: Prover, p: int, *,
                 seed: int = None, observer: ProtocolObserver = DummyObserver()):

    observer.p = p

    logger.info("[V]: Asking prover to send value of the entire polynomial")

    # first we ask the prover what he considers to be the value of the entire polynomial
    c = prover.get_value_of_entire_polynomial()

    logger.info("[P]: Value = %d =: c" % c)

    observer.on_handshake(p, c)

    if c == 0:
        # this is absurd, the prover has directly confessed that he
        # would like to prove that the QBF sentence is false
        observer.on_terminated(False)
        return False

    rng = Random(seed)

    rc = {}

    for v in range(1, qbf.get_variable_count() + 1):

        current_operator = ProofOperator(v)

        logger.info("-" * 30)
        logger.info(
            "Starting round %d. Current operator: %s",
            current_operator.get_round_number(),
            current_operator.to_string(qbf)
        )
        _log_random_choices(qbf, rc)

        # noinspection DuplicatedCode
        logger.info("[V]: Asking prover to send s(%s) = h(%s)", qbf.get_name(v), qbf.get_name(v))

        s = prover.get_operator_polynomial(current_operator, rc)

        logger.info("[P]: Sending s(%s) = %s", qbf.get_name(v), _poly_to_str(s))
        logger.info("[P]: deg(s(%s)) = %s", qbf.get_name(v), s.degree())

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            # check that s(0) * s(1) = c

            check_product = evaluate_s(s, 0, p) * evaluate_s(s, 1, p)
            check_product %= p

            logger.info("[V]: s(0) * s(1) = %d, expecting to be equal to c = %d", check_product, c)

            if check_product != c:
                logger.info("[V]: The above check has failed, "
                            "meaning that the prover has sent a malformed s polynomial.")
                observer.on_terminated(False)
                return False

        elif quantification == QBF.Q_EXISTS:

            # check that s(0) + s(1) = c
            check_sum = evaluate_s(s, 0, p) + evaluate_s(s, 1, p)
            check_sum %= p

            logger.info("[V]: s(0) + s(1) = %d, expecting to be equal to c = %d", check_sum, c)

            if check_sum != c:
                logger.info("[V]: The above check has failed, "
                            "meaning that the prover has sent a malformed s polynomial.")
                observer.on_terminated(False)
                return False
        else:
            assert False

        # choose a from F_p
        a = rng.randrange(p)
        rc[v] = a

        logger.info("[V]: Chose a = %d for variable %s", a, qbf.get_name(v))
        _log_random_choices(qbf, rc)

        _prev_c = c

        # calculate c = s(a)
        c = evaluate_s(s, a, p)

        logger.info("[V]: s(a) = %d =: c", c)

        observer.on_new_round(current_operator, s, _prev_c, rc, c)

        for lin_var in range(1, v + 1):

            current_operator = ProofOperator(v, lin_var)

            logger.info("-" * 30)
            logger.info(
                "Starting round %d. Current operator: %s",
                current_operator.get_round_number(),
                current_operator.to_string(qbf)
            )

            # noinspection DuplicatedCode
            logger.info(
                "[V]: Asking prover to send s(%s) = h(%s)",
                qbf.get_name(lin_var),
                qbf.get_name(lin_var)
            )

            s = prover.get_operator_polynomial(current_operator, rc)

            logger.info("[P]: Sending s(%s) = %s", qbf.get_name(lin_var), _poly_to_str(s))
            logger.info("[P]: deg(s(%s)) = %s", qbf.get_name(lin_var), s.degree())

            s_0 = evaluate_s(s, 0, p)
            s_1 = evaluate_s(s, 1, p)

            lin_var_val = rc[lin_var]

            check_sum = (lin_var_val * s_1 + (1 - lin_var_val) * s_0) % p

            logger.info("[V]: a_1 * s_1 + (1 - a_1) * s_0 = %d, expecting to be equal to c = %d", check_sum, c)

            if check_sum != c:
                logger.info("[V]: The above check has failed, "
                            "meaning that the prover has sent a malformed s polynomial.")
                observer.on_terminated(False)
                return False

            # choose a from F_p
            a = rng.randrange(p)
            rc[lin_var] = a

            logger.info(
                "[V]: Re-chose a = %d for variable %s (while linearizing it)",
                a,
                qbf.get_name(lin_var)
            )
            _log_random_choices(qbf, rc)

            _prev_c = c

            # calculate c = s(a)
            c = evaluate_s(s, a, p)

            logger.info("[V]: s(a) = %d =: c" % c)

            observer.on_new_round(current_operator, s, _prev_c, rc, c, lin_var_val)

    observer.on_terminated(True)
    return True
