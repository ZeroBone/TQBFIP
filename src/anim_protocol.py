from manim import *
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
        self.scene = scene

        self.cur_operator_rect = SurroundingRectangle(
            self.scene.proof_operators[0]
        )

    def on_round_start(self, current_operator: ProofOperator):
        print("Round start", current_operator.to_string(self.scene.qbf))

        new_operator_rect = SurroundingRectangle(
            self.scene.proof_operators[_proof_operator_to_mathtex_index(current_operator)],
            buff=.4 * SMALL_BUFF
        )

        self.scene.play(ReplacementTransform(self.cur_operator_rect, new_operator_rect))
        self.scene.wait(1)

        self.cur_operator_rect = new_operator_rect

    def finish(self, accepted: bool):
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

    def construct(self):

        self.proof_operators = _get_proof_operators_mathtex(self.qbf)
        self.proof_operators.to_edge(UP)

        prover_tex = Tex("P")
        prover_tex.scale(3)

        prover_box = SurroundingRectangle(prover_tex, BLUE_C)

        prover_group = VGroup(prover_tex, prover_box)
        prover_group.to_edge(LEFT)

        verifier_tex = Tex("V")
        verifier_tex.scale(3)

        verifier_box = SurroundingRectangle(verifier_tex, RED_C)

        verifier_group = VGroup(verifier_tex, verifier_box)
        verifier_group.to_edge(RIGHT)

        self.add(self.proof_operators)
        self.play(Create(prover_group), Create(verifier_group))
        self.wait(3)

        p = self.qbf.compute_prime_for_protocol()

        prover = HonestProver(self.qbf, p)

        observer = AnimatingObserver(self)

        accepted = run_verifier(self.qbf, prover, p, 0xcafe, observer)

        observer.finish(accepted)
