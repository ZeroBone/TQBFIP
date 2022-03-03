from manim import *
from main import *


class TQBFProtocol(Scene):

    def construct(self):

        qbf = construct_formula()

        text = MathTex(qbf.to_latex())

        self.play(Write(text))
        self.wait(2)


