from formulas import *
from qbf import *
from prover import Prover, HonestProver, ProofOperator
from random import Random


def run_verifier(qbf: QBF, prover: Prover, p: int, seed: int = None) -> bool:

    # first we ask the prover what he considers to be the value of the entire polynomial
    c = prover.get_value_of_entire_polynomial()

    if c == 0:
        # this is absurd, the prover has directly confessed that he
        # would like to prove that the QBF sentence is false
        return False

    rng = Random(seed)

    random_choices = {}

    for v in range(1, qbf.variable_count() + 1):

        v_symbol = qbf.get_symbol(v)

        print("Variable: %s Random choices:" % qbf.get_alias(v), random_choices)

        s = prover.get_operator_polynomial(ProofOperator(v), random_choices)

        print("Prover sent s(%s) =" % qbf.get_alias(v), s)

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            # check that s(0) * s(1) = c

            check_product = (int(s.subs(v_symbol, 0)) * int(s.subs(v_symbol, 1))) % p

            print("s(0) * s(1) = %d, expecting to be equal to c = %d" % (check_product, c))

            if check_product != c:
                return False

        else:
            assert quantification == QBF.Q_EXISTS

            # check that s(0) + s(1) = c
            check_sum = (int(s.subs(v_symbol, 0)) + int(s.subs(v_symbol, 1))) % p

            print("s(0) + s(1) = %d, expecting to be equal to c = %d" % (check_sum, c))

            if check_sum != c:
                return False

        # choose a from F_p
        a = rng.randrange(p)
        random_choices[v] = a

        print("Chose a = %d for variable %s" % (a, qbf.get_alias(v)))
        print("s =", s)

        # calculate c = s(a)
        c = int(s.subs(v_symbol, a)) % p

        print("s(a) = %d" % c)

        for variable_to_linearize in range(1, v + 1):

            lin_v_symbol = qbf.get_symbol(variable_to_linearize)

            print("Linearizing %s" % qbf.get_alias(variable_to_linearize))

            s = prover.get_operator_polynomial(ProofOperator(v, variable_to_linearize), random_choices)
            print("Prover sent s(%s) =" % qbf.get_alias(variable_to_linearize), s)

            s_0 = int(s.subs(lin_v_symbol, 0))
            s_1 = int(s.subs(lin_v_symbol, 1))

            a_for_x = random_choices[variable_to_linearize]

            check_sum = (a_for_x * s_1 + (1 - a_for_x) * s_0) % p

            print("a_1 * s_1 + (1 - a_1) * s_0 = %d, expecting to be equal to c = %d" % (check_sum, c))

            if check_sum != c:
                return False

            # choose a from F_p
            a = rng.randrange(p)
            random_choices[variable_to_linearize] = a

            print(
                "Re-chose a = %d for variable %s (while linearizing it)" %
                (a, qbf.get_alias(variable_to_linearize))
            )
            print("s =", s)

            # calculate c = s(a)
            c = int(s.subs(lin_v_symbol, a)) % p

            print("s(a) = %d" % c)

    return True


def main():

    qbf = example_2_formula()

    p = qbf.compute_prime_for_protocol()

    prover = HonestProver(qbf, p)

    print("Prime number for the proof: %d" % p)

    accepted = run_verifier(qbf, prover, p, 0xcafe)

    print("Verifier: %s" % ("accepts" if accepted else "rejects"))


if __name__ == "__main__":
    main()
