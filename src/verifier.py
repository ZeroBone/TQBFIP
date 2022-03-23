from random import Random
import logging
from qbf import QBF
from prover import Prover, ProofOperator


logger = logging.getLogger("protocol")


def run_verifier(qbf: QBF, prover: Prover, p: int, seed: int = None):

    logger.info("[V]: asks P for the value of the entire polynomial")

    # first we ask the prover what he considers to be the value of the entire polynomial
    c = prover.get_value_of_entire_polynomial()

    logger.info("[P]: Value = %d" % c)

    if c == 0:
        # this is absurd, the prover has directly confessed that he
        # would like to prove that the QBF sentence is false
        return False

    rng = Random(seed)

    random_choices = {}

    for v in range(1, qbf.get_variable_count() + 1):

        v_symbol = qbf.get_symbol(v)

        logger.info("-" * 30)
        logger.info("Starting new round. Current operator: %s", ProofOperator(v).to_string(qbf))
        logger.info("[V]: Random choices: %s", random_choices)
        logger.info("[V]: Asking prover to send s(%s) = h(%s)", qbf.get_alias(v), qbf.get_alias(v))

        s = prover.get_operator_polynomial(ProofOperator(v), random_choices)

        logger.info("[P]: s(%s) = %s", qbf.get_alias(v), s)

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            # check that s(0) * s(1) = c

            check_product = (int(s.subs(v_symbol, 0)) * int(s.subs(v_symbol, 1))) % p

            logger.info("[V]: s(0) * s(1) = %d, expecting to be equal to c = %d", check_product, c)

            if check_product != c:
                logger.info("[V]: The above check has failed, "
                            "meaning that the prover has sent a malformed s polynomial.")
                return False

        else:
            assert quantification == QBF.Q_EXISTS

            # check that s(0) + s(1) = c
            check_sum = (int(s.subs(v_symbol, 0)) + int(s.subs(v_symbol, 1))) % p

            logger.info("[V]: s(0) + s(1) = %d, expecting to be equal to c = %d", check_sum, c)

            if check_sum != c:
                logger.info("[V]: The above check has failed, "
                            "meaning that the prover has sent a malformed s polynomial.")
                return False

        # choose a from F_p
        a = rng.randrange(p)
        random_choices[v] = a

        logger.info("[V]: Chose a = %d for variable %s", a, qbf.get_alias(v))
        logger.info("[V]: s = %s", s)

        # calculate c = s(a)
        c = int(s.subs(v_symbol, a)) % p

        logger.info("[V]: s(a) = %d", c)

        for variable_to_linearize in range(1, v + 1):

            lin_v_symbol = qbf.get_symbol(variable_to_linearize)

            logger.info("-" * 30)
            logger.info(
                "Starting new round. Current operator: %s",
                ProofOperator(variable_to_linearize).to_string(qbf)
            )
            logger.info(
                "[V]: Asking prover to send s(%s) = h(%s)",
                qbf.get_alias(variable_to_linearize),
                qbf.get_alias(variable_to_linearize)
            )

            s = prover.get_operator_polynomial(ProofOperator(v, variable_to_linearize), random_choices)

            logger.info("[P]: s(%s) = %s", qbf.get_alias(variable_to_linearize), s)

            s_0 = int(s.subs(lin_v_symbol, 0))
            s_1 = int(s.subs(lin_v_symbol, 1))

            a_for_x = random_choices[variable_to_linearize]

            check_sum = (a_for_x * s_1 + (1 - a_for_x) * s_0) % p

            logger.info("[V]: a_1 * s_1 + (1 - a_1) * s_0 = %d, expecting to be equal to c = %d", check_sum, c)

            if check_sum != c:
                logger.info("[V]: The above check has failed, "
                            "meaning that the prover has sent a malformed s polynomial.")
                return False

            # choose a from F_p
            a = rng.randrange(p)
            random_choices[variable_to_linearize] = a

            logger.info(
                "[V]: Re-chose a = %d for variable %s (while linearizing it)",
                a,
                qbf.get_alias(variable_to_linearize)
            )
            logger.info("[V]: s = %s", s)

            # calculate c = s(a)
            c = int(s.subs(lin_v_symbol, a)) % p

            logger.info("[V]: s(a) = %d" % c)

    return True
