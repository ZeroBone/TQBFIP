from manim import *
from formulas import *
from prover import HonestProver
from verifier import run_verifier


class TQBFProtocol(Scene):

    def construct(self):

        qbf = example_2_formula()

        p = qbf.compute_prime_for_protocol()

        prover = HonestProver(qbf, p)

        qbf_formula = MathTex(qbf.to_latex())
        qbf_formula.to_edge(UP)

        # p_phi = MathTex(sympy.latex(qbf.arithmetize_matrix()))

        self.play(Write(qbf_formula))
        self.wait(2)
