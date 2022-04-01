from qbf import *


def default_example_formula():

    qbf = QBF()

    x, y, z, w = range(1, 5)

    qbf.add_variable(x, QBF.Q_EXISTS, "x")
    qbf.add_variable(y, QBF.Q_FORALL, "y")
    qbf.add_variable(z, QBF.Q_EXISTS, "z")
    qbf.add_variable(w, QBF.Q_FORALL, "w")

    qbf.add_clause({x, y, -z})
    qbf.add_clause({-x, -y, -w})
    qbf.add_clause({-y, w, z})

    return qbf


def simple_equality_formula():

    qbf = QBF()

    x, y = range(1, 3)

    qbf.add_variable(x, QBF.Q_FORALL, "x")
    qbf.add_variable(y, QBF.Q_EXISTS, "y")

    qbf.add_clause({x, -y})
    qbf.add_clause({-x, y})

    return qbf


def extended_equality_formula(make_unsat: bool = False):

    qbf = QBF()

    x, y, z = range(1, 4)

    qbf.add_variable(x, QBF.Q_FORALL, "x")
    qbf.add_variable(y, QBF.Q_EXISTS, "y")
    qbf.add_variable(z, QBF.Q_FORALL, "z")

    qbf.add_clause({x, -y, z})
    qbf.add_clause({-x, y, z})

    if make_unsat:
        qbf.add_clause({x, y})

    return qbf


def single_clause_or_formula(n: int):

    qbf = QBF()

    for x_i in range(1, n + 1):
        qbf.add_variable(x_i, QBF.Q_EXISTS, "x_%d" % x_i)

    qbf.add_clause(set([x_i for x_i in range(1, n + 1)]))

    return qbf


def forall_quantified_tautology():

    qbf = QBF()

    qbf.add_variable(1, QBF.Q_FORALL, "x")
    qbf.add_variable(2, QBF.Q_FORALL, "y")
    qbf.add_variable(3, QBF.Q_FORALL, "z")
    qbf.add_variable(4, QBF.Q_FORALL, "w")

    qbf.add_clause({1, -1})

    return qbf


# this method generates a formula such that the polynomial
# evaluates to 37, and the formula itself contains 5 variables, so
# we would work modulo first prime number greater than 2^5 = 32,
# which is exactly 37 which is 0 mod 37
def prime_eval_formula():

    qbf = QBF()

    x, y, z, u, w = range(1, 6)

    qbf.add_variable(x, QBF.Q_EXISTS, "x")
    qbf.add_variable(y, QBF.Q_FORALL, "y")
    qbf.add_variable(z, QBF.Q_EXISTS, "z")
    qbf.add_variable(u, QBF.Q_EXISTS, "u")
    qbf.add_variable(w, QBF.Q_EXISTS, "w")

    qbf.add_clause({x, -z})
    qbf.add_clause({-z, -u, -w})
    qbf.add_clause({-x, -y, -u, -w})
    qbf.add_clause({-y, -z})

    return qbf
