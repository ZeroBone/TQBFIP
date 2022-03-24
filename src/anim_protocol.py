from manim import *
import sympy
from formulas import *
from prover import ProofOperator, HonestProver
from verifier import ProtocolObserver, run_verifier


def _get_proof_operators_mathtex(qbf: QBF):

    po = []

    for v in range(1, qbf.get_variable_count() + 1):

        po.append(qbf.get_operator(v))

        # append linearization terms

        po.extend(("L_{%s}" % qbf.get_symbol(lin_v) for lin_v in range(1, v + 1)))

    mt = MathTex(*po, r"P_{\varphi}")

    for v in range(1, qbf.get_variable_count() + 1):

        pos = v * (v - 1) // 2

        if qbf.get_quantification(v) == QBF.Q_FORALL:
            mt[pos + v - 1].set_color(RED_C)
            # forall_indices.append(len(po))
        else:
            assert qbf.get_quantification(v) == QBF.Q_EXISTS
            # exists_indices.append(len(po))
            mt[pos + v - 1].set_color(GOLD_C)

        # color linearization operators
        for i in range(v):
            mt[pos + v + i].set_color(PURPLE_A)

    return mt


def _proof_operator_to_mathtex_index(op: ProofOperator):
    return (op.v * (op.v - 1) // 2) + op.v + op.lv - 1


class AnimatingObserver(ProtocolObserver):

    def __init__(self, scene):

        self._debug_counter = 0

        self.scene = scene

        self.cur_operator_rect = SurroundingRectangle(
            self.scene.proof_operators[0]
        )

        _title_direction = .5 * UP

        self.verifier_prover_arrow = Arrow(
            self.scene.verifier_group.get_right() + _title_direction,
            self.scene.prover_group.get_left() + _title_direction
        )

        self.prover_verifier_arrow = Arrow(
            self.scene.prover_group.get_left() + _title_direction,
            self.scene.verifier_group.get_right() + _title_direction
        )

    def on_new_round(self, current_operator: ProofOperator, s):
        print("Round start", current_operator.to_string(self.scene.qbf))

        self._debug_counter += 1

        if self._debug_counter >= 3:
            return

        operator_variable = current_operator.get_primary_variable()

        new_operator_rect = SurroundingRectangle(
            self.scene.proof_operators[_proof_operator_to_mathtex_index(current_operator)],
            buff=.4 * SMALL_BUFF
        )

        self.scene.play(ReplacementTransform(self.cur_operator_rect, new_operator_rect))

        verifier_prover_message = Tex("Please send me $ s(%s) $"
                                      % self.scene.qbf.get_alias(operator_variable))
        verifier_prover_message.next_to(self.verifier_prover_arrow, DOWN)

        s_lambda = sympy.lambdify(self.scene.qbf.get_symbol(operator_variable), s, "math")

        p = 17

        def _s_plotter(x: float) -> float:
            v = s_lambda(x)
            if v >= p:
                v -= (v // p) * p
            elif v < 0:
                v += ((-v // p) + 1) * p
            return v

        s_axes = Axes(x_range=[0, 16], y_range=[0, 16], x_length=5, y_length=5)
        s_graph = s_axes.plot(_s_plotter)
        VGroup(s_axes, s_graph).to_edge(DOWN)

        self.scene.play(Write(verifier_prover_message), Write(self.verifier_prover_arrow))
        self.scene.wait(1)
        self.scene.play(FadeOut(verifier_prover_message), FadeOut(self.verifier_prover_arrow))
        self.scene.play(Create(s_axes), Create(s_graph), Write(self.prover_verifier_arrow))
        self.scene.wait(1)
        self.scene.play(FadeOut(s_axes), FadeOut(s_graph), FadeOut(self.prover_verifier_arrow))

        self.cur_operator_rect = new_operator_rect

    def on_terminated(self, accepted: bool):
        self.scene.play(FadeOut(self.cur_operator_rect))


class ProtocolScene(Scene):

    def __init__(
            self,
            renderer=None,
            camera_class=Camera,
            always_update_mobjects=False,
            random_seed=None,
            skip_animations=False,
            qbf: QBF = example_2_formula()
    ):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.qbf = qbf
        self.proof_operators = None
        self.prover_group = None
        self.verifier_group = None

    def construct(self):

        self.proof_operators = _get_proof_operators_mathtex(self.qbf)
        self.proof_operators.to_edge(UP)

        prover_tex = Tex("P")
        prover_tex.scale(3)

        prover_box = SurroundingRectangle(prover_tex, BLUE_C)

        self.prover_group = VGroup(prover_tex, prover_box)
        self.prover_group.to_edge(RIGHT)

        verifier_tex = Tex("V")
        verifier_tex.scale(3)

        verifier_box = SurroundingRectangle(verifier_tex, RED_C)

        self.verifier_group = VGroup(verifier_tex, verifier_box)
        self.verifier_group.to_edge(LEFT)

        VGroup(self.prover_group, self.verifier_group).next_to(self.proof_operators, DOWN)

        self.add(self.proof_operators)
        self.play(Create(self.prover_group), Create(self.verifier_group))
        self.wait(3)

        p = self.qbf.compute_prime_for_protocol()

        prover = HonestProver(self.qbf, p)

        run_verifier(self.qbf, prover, p, 0xcafe, AnimatingObserver(self))
