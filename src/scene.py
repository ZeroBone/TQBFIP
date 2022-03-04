from manim import *
from main import *


class TQBFProtocol(Scene):

    def construct(self):

        qbf = construct_formula()

        text = MathTex(qbf.to_latex())

        p_phi = MathTex(sympy.latex(qbf.construct_p_phi()))

        group = Group(text, p_phi)

        self.add(group.arrange(DOWN, buff=5))