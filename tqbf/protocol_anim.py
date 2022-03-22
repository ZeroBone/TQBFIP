from manim import *
from formulas import *


def _get_proof_operators_mathtex(qbf: QBF):

    po = []

    forall_indices = []
    exists_indices = []
    linearization_indices = []

    for v in range(1, qbf.get_variable_count() + 1):

        if qbf.get_quantification(v) == QBF.Q_FORALL:
            forall_indices.append(len(po))
        else:
            assert qbf.get_quantification(v) == QBF.Q_EXISTS
            exists_indices.append(len(po))

        po.append(qbf.get_operator(v))

        # append linearization terms

        linearization_indices.extend((i + len(po) for i in range(v)))

        po.extend(("L_{%s}" % qbf.get_symbol(lin_v) for lin_v in range(1, v + 1)))

    mt = MathTex(*po)

    for i in forall_indices:
        mt[i].set_color(RED_C)

    for i in exists_indices:
        mt[i].set_color(GREEN_C)

    for i in linearization_indices:
        mt[i].set_color(BLUE_C)

    return mt


class ProtocolScene(Scene):

    def construct(self):

        qbf = example_2_formula()

        proof_operators = _get_proof_operators_mathtex(qbf)

        self.add(proof_operators)
