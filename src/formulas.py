from qbf import *


def simple_equality_formula():

    qbf = QBF()

    x, y = range(1, 3)

    qbf.add_variable(x, QBF.Q_FORALL, "x")
    qbf.add_variable(y, QBF.Q_EXISTS, "y")

    qbf.add_clause({x, -y})
    qbf.add_clause({-x, y})

    return qbf


def extended_equality_formula():

    qbf = QBF()

    x, y, z = range(1, 4)

    qbf.add_variable(x, QBF.Q_FORALL, "x")
    qbf.add_variable(y, QBF.Q_EXISTS, "y")
    qbf.add_variable(z, QBF.Q_FORALL, "z")

    qbf.add_clause({x, -y, z})
    qbf.add_clause({-x, y, z})

    return qbf


def example_2_formula():

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
