from formulas import *
from qbf import *
from prover import HonestProver
from prime import next_prime


def main():

    qbf = extended_equality_formula()

    p = next_prime(1 << qbf.variable_count())

    print("Prime number for the proof: %d" % p)

    prover = HonestProver(qbf, p)

    print("----------------")

    for v in range(1, qbf.variable_count() + 1):

        print("Variable: %d" % v)

        for variable_to_linearize in range(1, v + 1):
            print("Linearizing %s" % qbf.get_alias(variable_to_linearize))


if __name__ == "__main__":
    main()
