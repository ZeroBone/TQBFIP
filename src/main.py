from formulas import *
from qbf import *
from prover import HonestProver, ProofOperator
from prime import next_prime
from secrets import randbelow


def main():

    qbf = extended_equality_formula()

    p = next_prime(1 << qbf.variable_count())

    print("Prime number for the proof: %d" % p)

    prover = HonestProver(qbf, p)

    print("----------------")

    c = 1

    for v in range(1, qbf.variable_count() + 1):

        print("Variable: %d" % v)

        s = prover.get_operator_polynomial(ProofOperator(v))

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            # TODO
            pass
        else:
            assert quantification == QBF.Q_EXISTS

        a = randbelow(p)

        # c = s(a)

        for variable_to_linearize in range(1, v + 1):
            print("Linearizing %s" % qbf.get_alias(variable_to_linearize))


if __name__ == "__main__":
    main()
