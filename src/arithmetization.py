from manim import *
from formulas import *


class ArithmetizationScene(Scene):

    def construct(self):

        qbf = example_2_formula()

        qbf_formula_arr = qbf.to_latex_array()
        qbf_formula_arr[0] = "\\varphi = " + qbf_formula_arr[0]

        qbf_formula = MathTex(*qbf_formula_arr)
        qbf_formula.to_edge(UP)

        p_phi = MathTex(
            "P_{\\varphi}(%s) = \\quad " % ",".join([
                qbf.get_alias(v + 1) for v in range(qbf.get_variable_count())
            ]),
            *qbf.get_arithmetization_latex_array()
        )
        p_phi.next_to(qbf_formula, DOWN)

        self.play(Write(qbf_formula))
        self.play(Write(p_phi[:1]))

        self.wait(.5)

        clause_frame = SurroundingRectangle(qbf_formula[1], buff=.1)

        self.play(Create(clause_frame))

        for c in range(qbf.get_clause_count()):

            i = 1 + 2 * c

            if c != 0:
                next_clause_frame = SurroundingRectangle(qbf_formula[i], buff=.1)
                self.play(ReplacementTransform(clause_frame, next_clause_frame))
                clause_frame = next_clause_frame

            self.wait(.25)
            self.play(ReplacementTransform(qbf_formula[i].copy(), p_phi[i]))
            self.wait(1)
