from manim import *
from formulas import *
from prover import ProofOperator, HonestProver
from verifier import ProtocolObserver, run_verifier, evaluate_s
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

    # rounds_limit = 0 means no limit for the amount of rounds to be animated
    def __init__(self, scene, rounds_limit: int = 0):
        super().__init__()

        self._rounds_limit = rounds_limit
        self._rounds_counter = 0

        self.scene = scene

        self.prover_group = None

        self.verifier_group = None
        self.bottom_group = None

        self.verifier_prover_arrow = None
        self.prover_verifier_arrow = None

        self.proof_operators = None
        self.c_variable = None

        self.top_group = None
        self.operator_rect = None

        self.qbf_tree = None

    def on_handshake(self, p: int, initial_c: int):

        self.p = p

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

        self.bottom_group = VGroup(self.prover_group, self.verifier_group)
        self.bottom_group.to_edge(DOWN)

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

        self.c_variable = Variable(initial_c, "c", num_decimal_places=0)
        p_variable = Variable(self.p, "p", num_decimal_places=0)

        self.top_group = VGroup(
            self.proof_operators,
            VGroup(self.c_variable, p_variable).arrange(RIGHT, buff=2)
        ).arrange(DOWN).to_edge(UP)

        self.operator_rect = None

        # qbf tree

        self.qbf_tree = QBFTree(
            self.scene.qbf,
            self.p,
            {},
            1
        )

        # make the created objects visible

        self.scene.play(
            FadeIn(self.top_group),
            Create(self.bottom_group),
            Create(self.qbf_tree.get_object_group())
        )

        self.scene.wait()
        self.scene.wait(3)

    def _s_polynomial_to_mathtex(self, s):

        s_cleansed = sympy.trunc(sympy.expand(s.as_expr()), self.p, s.gens)

        return MathTex(sympy.latex(s_cleansed))

    def on_new_round(self, current_operator: ProofOperator, s, rc: dict, new_c: int, prev_c: int):

        self._rounds_counter += 1

        if self._rounds_limit != 0 and self._rounds_counter > self._rounds_limit:
            return

        # TODO: add random choices to the animation

        new_operator_rect = SurroundingRectangle(
            self.proof_operators[_proof_operator_to_mathtex_index(current_operator)],
            buff=.4 * SMALL_BUFF
        )

        if self.operator_rect is None:
            self.scene.play(Create(new_operator_rect))
        else:
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

        # verification of the s polynomial by the verifier animation

        verification_brace = Brace(self.verifier_group, RIGHT)

        if current_operator.is_linearity_operator():

            verification_steps = [
                MathTex(r"a_1 \cdot s(1) + (1 - a_1) \cdot s(0) \stackrel{?}{=} c"),
                MathTex(r"a_1 \cdot s(1) + (1 - a_1) \cdot s(0) \stackrel{?}{=} %d" % prev_c),
            ]

        elif self.scene.qbf.get_quantification(operator_variable) == QBF.Q_FORALL:
            # check that s(0) * s(1) = c

            check_product = evaluate_s(s, 0, self.p) * evaluate_s(s, 1, self.p)
            check_product %= self.p

            assert check_product == prev_c

            verification_steps = [
                MathTex(r"s(0) \cdot s(1) \stackrel{?}{=} c")
            ]

        elif self.scene.qbf.get_quantification(operator_variable) == QBF.Q_EXISTS:
            # check that s(0) + s(1) = c
            check_sum = evaluate_s(s, 0, self.p) + evaluate_s(s, 1, self.p)
            check_sum %= self.p

            assert check_sum == prev_c

            verification_steps = [
                MathTex(r"s(0) + s(1) \stackrel{?}{=} c")
            ]

        else:
            assert False

        _last_ver_step = None

        for ver_step in verification_steps:

            ver_step.next_to(verification_brace, RIGHT)

            if _last_ver_step is None:
                self.scene.play(FadeIn(verification_brace), FadeIn(ver_step))
                self.scene.wait(1)
            else:
                self.scene.play(ReplacementTransform(_last_ver_step, ver_step))
                self.scene.wait(.5)

            _last_ver_step = ver_step

        self.scene.play(FadeOut(verification_brace), FadeOut(_last_ver_step))

        # qbf tree

        new_qbf_tree = QBFTree(
            self.scene.qbf,
            self.p,
            rc,
            current_operator.get_leftmost_variable_that_is_not_yet_resolved()
        )

        self.scene.play(
            ReplacementTransform(self.qbf_tree.get_object_group(), new_qbf_tree.get_object_group()),
            self.c_variable.tracker.animate.set_value(new_c)
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
            qbf: QBF = default_example_formula()
    ):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.qbf = qbf
        self.prover_group = None
        self.verifier_group = None

    def construct(self):

        p = self.qbf.compute_prime_for_protocol()

        prover = HonestProver(self.qbf, p)

        run_verifier(self.qbf, prover, p, 0xcafe, AnimatingObserver(self, 2))
