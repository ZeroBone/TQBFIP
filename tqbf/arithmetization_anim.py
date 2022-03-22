from manim import *
from formulas import *


class ArithmetizationScene(Scene):

    def construct(self):

        qbf = example_2_formula()

        color_palette = [BLUE_C, RED_C, GREEN_C, GOLD_C]

        qbf_formula = MathTex(r"\varphi =", *qbf.to_latex_array())
        qbf_formula.to_edge(UP)

        p_phi = MathTex(
            r"P_{\varphi}(%s) = \quad " % ",".join([
                qbf.get_alias(v + 1) for v in range(qbf.get_variable_count())
            ]),
            *qbf.get_matrix_arithmetization_latex_array()
        )

        equivalence_formula_arr = qbf.get_arithmetization_latex_array()
        equivalence_formula_arr[0] = "&" + equivalence_formula_arr[0]

        equivalence_formula = MathTex(
            r"&\varphi \in \operatorname{TQBF} \Leftrightarrow \\",
            *equivalence_formula_arr
        )

        for v in range(qbf.get_variable_count()):
            equivalence_formula[1 + v].set_color(color_palette[v % len(color_palette)])

        equivalence_formula[qbf.get_variable_count() + 1].set_color(PURPLE_A)

        for v in range(qbf.get_variable_count()):
            qbf_formula.set_color_by_tex(
                "%s" % qbf.get_alias(v + 1),
                color_palette[v % len(color_palette)]
            )

        qbf_formula.set_color_by_tex(r"\wedge", TEAL_A)

        for c in range(qbf.get_clause_count()):
            qbf_formula[qbf.get_variable_count() + 2 + 2 * c].set_color(PURPLE_A)

        VGroup(qbf_formula, p_phi, equivalence_formula).arrange(DOWN)

        self.play(Write(qbf_formula))
        self.play(Write(p_phi[:1]))

        self.wait(.5)

        clause_frame = SurroundingRectangle(qbf_formula[qbf.get_variable_count() + 2], buff=.1)

        self.play(Create(clause_frame))

        for c in range(qbf.get_clause_count()):

            p_i = 1 + 2 * c
            qbf_i = qbf.get_variable_count() + 2 + 2 * c

            if c != 0:
                next_clause_frame = SurroundingRectangle(qbf_formula[qbf_i], buff=.1)
                self.play(ReplacementTransform(clause_frame, next_clause_frame))
                clause_frame = next_clause_frame

            self.wait(.125)
            self.play(ReplacementTransform(qbf_formula[qbf_i].copy(), p_phi[p_i]))
            self.wait(1)

        self.play(FadeOut(clause_frame), Write(equivalence_formula))
        self.wait(3)
