from manim import *
from formulas import *
from prover import ProofOperator, HonestProver
from verifier import ProtocolObserver, run_verifier
from qbf_tree import QBFTree


def _get_proof_operators_mathtex(qbf: QBF):

    po = []

    for v in range(1, qbf.get_variable_count() + 1):

        po.append(qbf.get_variable_latex_operator(v))

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
        super().__init__()

        self._debug_counter = 0

        self.scene = scene

        # prover and verifier communication

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

        self.prover_verifier_group = VGroup(self.prover_group, self.verifier_group)
        self.prover_verifier_group.to_edge(DOWN)

        _title_direction = .5 * DOWN

        self.verifier_prover_arrow = Arrow(
            self.verifier_group.get_right() + _title_direction,
            self.prover_group.get_left() + _title_direction
        )

        self.prover_verifier_arrow = Arrow(
            self.prover_group.get_left() + _title_direction,
            self.verifier_group.get_right() + _title_direction
        )

        # proof operators

        self.proof_operators = _get_proof_operators_mathtex(self.scene.qbf)
        self.proof_operators.to_edge(UP)

        self.scene.add(self.proof_operators)

        self.operator_rect = SurroundingRectangle(
            self.proof_operators[0]
        )

        # make the created objects visible

        self.scene.play(Create(self.operator_rect), Create(self.prover_verifier_group))

        self.qbf_tree = None

    def _s_polynomial_to_mathtex(self, s):

        s_cleansed = sympy.trunc(sympy.expand(s.as_expr()), self.p)

        return MathTex(sympy.latex(s_cleansed))

    def on_new_round(self, current_operator: ProofOperator, s, random_choices: dict):
        print("Round start", current_operator.to_string(self.scene.qbf))

        # TODO: remove debug counter
        self._debug_counter += 1

        if self._debug_counter >= 6:
            return

        new_operator_rect = SurroundingRectangle(
            self.proof_operators[_proof_operator_to_mathtex_index(current_operator)],
            buff=.4 * SMALL_BUFF
        )

        self.scene.play(ReplacementTransform(self.operator_rect, new_operator_rect))

        self.operator_rect = new_operator_rect

        operator_variable = current_operator.get_primary_variable()

        verifier_prover_message = Tex("Please send me $ s(%s) $"
                                      % self.scene.qbf.get_alias(operator_variable))
        verifier_prover_message.next_to(self.verifier_prover_arrow, UP)

        prover_verifier_message = self._s_polynomial_to_mathtex(s)
        prover_verifier_message.next_to(self.prover_verifier_arrow, UP)

        self.scene.play(Write(verifier_prover_message), GrowArrow(self.verifier_prover_arrow))
        self.scene.wait(1)
        self.scene.play(FadeOut(verifier_prover_message), FadeOut(self.verifier_prover_arrow))
        self.scene.play(Write(prover_verifier_message), GrowArrow(self.prover_verifier_arrow))
        self.scene.wait(1)
        self.scene.play(FadeOut(prover_verifier_message), FadeOut(self.prover_verifier_arrow))

        new_qbf_tree = QBFTree(
            self.scene.qbf,
            self.p,
            random_choices,
            operator_variable
        )

        if self.qbf_tree is None:
            self.scene.play(Create(new_qbf_tree.get_object_group()))
        else:
            self.scene.play(
                ReplacementTransform(self.qbf_tree.get_object_group(), new_qbf_tree.get_object_group())
            )

        self.qbf_tree = new_qbf_tree

        self.scene.wait()
        self.scene.wait(1)

    def on_terminated(self, accepted: bool):
        self.scene.play(FadeOut(self.operator_rect))


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
        self.prover_group = None
        self.verifier_group = None

    def construct(self):

        p = self.qbf.compute_prime_for_protocol()

        prover = HonestProver(self.qbf, p)

        run_verifier(self.qbf, prover, p, 0xcafe, AnimatingObserver(self))
