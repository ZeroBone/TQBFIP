from formulas import *
from qbf import *
from prover import Prover, HonestProver, ProofOperator
from prime import next_prime
from random import Random


def run_verifier(qbf: QBF, prover: Prover, p: int, seed: int = None) -> bool:

    c = 1

    rng = Random(seed)

    random_choices = {}

    for v in range(1, qbf.variable_count() + 1):

        v_symbol = qbf.get_symbol(v)

        print("Variable: %d Random choices:" % v, random_choices)

        s = prover.get_operator_polynomial(ProofOperator(v), random_choices)

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

        # calculate c = s(a)
        c = int(s.subs(v_symbol, a)) % p

        for variable_to_linearize in range(1, v + 1):

            lin_v_symbol = qbf.get_symbol(variable_to_linearize)

            print("Linearizing %s" % qbf.get_alias(variable_to_linearize))

            s = prover.get_operator_polynomial(ProofOperator(v, variable_to_linearize), random_choices)
            print(s)

            s_0 = int(s.subs(lin_v_symbol, 0))
            s_1 = int(s.subs(lin_v_symbol, 1))

            a_1 = random_choices[variable_to_linearize]

            check_sum = (a_1 * s_0 + (1 - a_1) * s_1) % p

            print("a_1 * s_0 + (1 - a_1) * s_1 = %d, expecting to be equal to c = %d" % (check_sum, c))

            if check_sum != c:
                return False

    return True


def main():

    # qbf = extended_equality_formula()
    qbf = example_2_formula()

    p = next_prime(1 << qbf.variable_count())
    # p = 10000019

    print("Prime number for the proof: %d" % p)

    prover = HonestProver(qbf, p)

    accepted = run_verifier(qbf, prover, p, 0xcafe)

    print("Verifier: %s" % ("accepts" if accepted else "rejects"))


if __name__ == "__main__":
    main()
