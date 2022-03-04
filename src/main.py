from formulas import *
from qbf import *
from prover import HonestProver


def main():

    qbf = extended_equality_formula()

    cur_p = qbf.construct_p_phi()

    prover = HonestProver(qbf)

    print(cur_p)

    for v in range(qbf.variable_count(), 0, -1):

        print("Variables: %d" % v)
        print("Before linearization:", cur_p.expand())

        for variable_to_linearize in range(v, 0, -1):
            cur_p = prover.get_linearized_polynomial(variable_to_linearize, cur_p)
            print("Linearized %s:" % qbf.get_alias(variable_to_linearize), cur_p.expand())

        quantification = qbf.get_quantification(v)

        if quantification == QBF.Q_FORALL:
            cur_p = prover.get_forall_polynomial(v, cur_p)
        else:
            cur_p = prover.get_exists_polynomial(v, cur_p)

        print("Applied quantification:", cur_p)

    print("Final result:", cur_p)


if __name__ == "__main__":
    main()
