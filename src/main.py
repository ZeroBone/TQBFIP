from formulas import *
from qbf import *
from prover import HonestProver, ProofOperator
from prime import next_prime
import random


def main():

    random.seed(10)

    qbf = extended_equality_formula()

    p = next_prime(1 << qbf.variable_count())

    print("Prime number for the proof: %d" % p)

    prover = HonestProver(qbf, p)

    print("----------------")

    c = 1

    random_choices = {}

    verification_success = True

    for v in range(1, qbf.variable_count() + 1):

        v_symbol = qbf.get_symbol(v)

        print("Variable: %d Random choices:" % v, random_choices)

        s = prover.get_operator_polynomial(ProofOperator(v), random_choices)

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            # check s(0) * s(1) = c

            check_product = int(s.subs(v_symbol, 0) * s.subs(v_symbol, 1))

            print("s(0) * s(1) = %d, comparing with c = %d" % (check_product, c))

            if check_product != c:
                verification_success = False
                break

        else:
            assert quantification == QBF.Q_EXISTS

            # check s(0) + s(1) = c
            check_sum = int(s.subs(v_symbol, 0) + s.subs(v_symbol, 1))

            print("s(0) + s(1) = %d, comparing with c = %d" % (check_sum, c))

            if check_sum != c:
                verification_success = False
                break

        # choose a from F_p
        a = random.randrange(p)

        random_choices[v] = a

        # c = s(a)
        print(s.subs(v_symbol, a))
        print(type(s.subs(v_symbol, a)))
        c = int(s.subs(v_symbol, a))

        for variable_to_linearize in range(1, v + 1):
            print("Linearizing %s" % qbf.get_alias(variable_to_linearize))

            s = prover.get_operator_polynomial(ProofOperator(v, variable_to_linearize), random_choices)

    print("Result: verifier %s" % "accepts" if verification_success else "rejects")


if __name__ == "__main__":
    main()
