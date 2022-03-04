from qbf import *


def simple_equality_formula():

    qbf = QBF()

    qbf.add_variable(1, QBF.Q_FORALL, "x")
    qbf.add_variable(2, QBF.Q_EXISTS, "y")

    qbf.add_clause({1, -2})
    qbf.add_clause({-1, 2})

    return qbf


def extended_equality_formula():

    qbf = QBF()

    qbf.add_variable(1, QBF.Q_FORALL, "x")
    qbf.add_variable(2, QBF.Q_EXISTS, "y")
    qbf.add_variable(3, QBF.Q_FORALL, "z")

    qbf.add_clause({1, -2, 3})
    qbf.add_clause({-1, 2, 3})

    return qbf
