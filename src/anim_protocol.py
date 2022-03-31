import random
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
    def __init__(self, scene, honest_prover: HonestProver, rounds_limit: int = 0):
        super().__init__()

        self.scene = scene

        self._prover = honest_prover

        self._rounds_limit = rounds_limit
        self._rounds_counter = 0

        self.prover_group = None

        self.verifier_group = None
        self.bottom_group = None

        self.verifier_prover_arrow = None
        self.prover_verifier_arrow = None

        self.proof_operators = None
        self.rc_vars = None
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

        # proof operators and the row underneath (with the variables)

        self.proof_operators = _get_proof_operators_mathtex(self.scene.qbf)

        self.rc_vars = [
            Variable(self.p, v.name, num_decimal_places=0)
            for v in self.scene.qbf.get_variables()
        ]

        self.c_variable = Variable(initial_c, "c", num_decimal_places=0)
        p_variable = Variable(self.p, "p", num_decimal_places=0)

        proof_vars_group = VGroup(self.c_variable, p_variable).arrange(RIGHT, buff=.8)
        proof_vars_surrounding = SurroundingRectangle(proof_vars_group, color=GRAY,
                                                      corner_radius=.1, buff=.25)
        proof_vars_group_surrounded = VGroup(proof_vars_group, proof_vars_surrounding)

        vars_row = VGroup(
            *self.rc_vars,
            proof_vars_group_surrounded
        ).arrange(RIGHT, buff=.8)

        self.top_group = VGroup(
            self.proof_operators,
            vars_row
        ).arrange(DOWN).to_edge(UP)

        vars_row.remove(*self.rc_vars)

        self.operator_rect = None

        # qbf tree

        self.qbf_tree = QBFTree(
            self._prover,
            {},
            1
        )

        # make the created objects visible

        self.scene.play(
            FadeIn(self.top_group),
            Create(self.qbf_tree.get_object_group()),
            FadeIn(self.bottom_group)
        )

        self.scene.wait()
        self.scene.wait(3)

    def _s_polynomial_to_mathtex(self, s, var_alias: str):

        s_cleansed = sympy.trunc(sympy.expand(s.as_expr()), self.p, s.gens)

        return MathTex("s(%s) =" % var_alias, sympy.latex(s_cleansed))

    def on_new_round(self,
                     current_operator: ProofOperator,
                     s,
                     prev_c: int,
                     new_rc: dict,
                     new_c: int,
                     prev_var_rc: int = None):

        self._rounds_counter += 1

        if self._rounds_limit != 0 and self._rounds_counter > self._rounds_limit:
            return

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
                                      % self.scene.qbf.get_name(operator_variable))
        verifier_prover_message.next_to(self.verifier_prover_arrow, UP)

        prover_verifier_message = self._s_polynomial_to_mathtex(s, self.scene.qbf.get_name(operator_variable))
        prover_verifier_message.next_to(self.prover_verifier_arrow, UP)

        self.scene.play(Write(verifier_prover_message), GrowArrow(self.verifier_prover_arrow))
        self.scene.wait(1)
        self.scene.play(FadeOut(verifier_prover_message), FadeOut(self.verifier_prover_arrow))
        self.scene.play(Write(prover_verifier_message), GrowArrow(self.prover_verifier_arrow))
        self.scene.wait(1)
        self.scene.play(FadeOut(prover_verifier_message), FadeOut(self.prover_verifier_arrow))

        # verification of the s polynomial by the verifier animation

        verification_brace = Brace(self.verifier_group, RIGHT)

        s_0 = evaluate_s(s, 0, self.p)
        s_1 = evaluate_s(s, 1, self.p)

        if current_operator.is_linearity_operator():

            assert prev_var_rc is not None

            lin_var = self.scene.qbf.get_name(current_operator.lv)

            check_value = (prev_var_rc * s_1 + s_0 - prev_var_rc * s_0) % self.p

            assert check_value == prev_c

            final_step = MathTex(r"%d = %d" % (check_value, prev_c))
            final_step[0].set_color(GREEN_C)

            verification_steps = [
                MathTex(r"%s \cdot s(1) + (1 - %s) \cdot s(0) \stackrel{?}{=} c" %
                        (lin_var, lin_var)),
                MathTex(r"%s \cdot s(1) + s(0) - %s \cdot s(0) \stackrel{?}{=} c" %
                        (lin_var, lin_var)),
                MathTex(r"%s \cdot %d + %d - %s \cdot %d \stackrel{?}{=} %d" %
                        (lin_var, s_1, s_0, lin_var, s_0, prev_c)),
                MathTex(r"%d \cdot %d + %d - %d \cdot %d \stackrel{?}{=} %d" %
                        (prev_var_rc, s_1, s_0, prev_var_rc, s_0, prev_c)),
                MathTex(r"%d + %d - %d \stackrel{?}{=} %d" %
                        ((prev_var_rc * s_1) % self.p, s_0, (prev_var_rc * s_0) % self.p, prev_c)),
                MathTex(r"%d \stackrel{?}{=} %d" %
                        (check_value, prev_c)),
                final_step
            ]

        elif self.scene.qbf.get_quantification(operator_variable) == QBF.Q_FORALL:
            # check that s(0) * s(1) = c

            assert (s_0 * s_1) % self.p == prev_c

            final_step = MathTex(r"%d = %d" % ((s_0 * s_1) % self.p, prev_c))
            final_step[0].set_color(GREEN_C)

            verification_steps = [
                MathTex(r"s(0) \cdot s(1) \stackrel{?}{=} c"),
                MathTex(r"%d \cdot %d \stackrel{?}{=} %d" % (s_0, s_1, prev_c)),
                MathTex(r"%d \stackrel{?}{=} %d" % ((s_0 * s_1) % self.p, prev_c)),
                final_step
            ]

        elif self.scene.qbf.get_quantification(operator_variable) == QBF.Q_EXISTS:
            # check that s(0) + s(1) = c

            assert (s_0 + s_1) % self.p == prev_c

            final_step = MathTex(r"%d = %d" % ((s_0 + s_1) % self.p, prev_c))
            final_step[0].set_color(GREEN_C)

            verification_steps = [
                MathTex(r"s(0) + s(1) \stackrel{?}{=} c"),
                MathTex(r"%d + %d \stackrel{?}{=} %d" % (s_0, s_1, prev_c)),
                MathTex(r"%d \stackrel{?}{=} %d" % ((s_0 + s_1) % self.p, prev_c)),
                final_step
            ]

        else:
            assert False

        if current_operator.is_last_operator(self.scene.qbf):
            final_step = Tex(r"Proof accepted!")
            final_step[0].set_color(GREEN_C)
            verification_steps.append(final_step)

        _last_ver_step = None

        for ver_step in verification_steps:

            ver_step.next_to(verification_brace, RIGHT)

            if _last_ver_step is None:
                self.scene.play(FadeIn(verification_brace), FadeIn(ver_step))
                self.scene.wait(.4)
            else:
                self.scene.play(ReplacementTransform(_last_ver_step, ver_step, run_time=.25))
                self.scene.wait(.4)

            _last_ver_step = ver_step

        if current_operator.is_last_operator(self.scene.qbf):
            # verifier accepts
            self.scene.wait(3)
            self.scene.play(FadeOut(verification_brace), FadeOut(_last_ver_step))
            return
        else:
            self.scene.play(FadeOut(_last_ver_step))

        # random picking of a

        assert operator_variable in new_rc
        picked_a_value = new_rc[operator_variable]

        a_var = Variable(
            random.randrange(self.p),
            Tex("Picking randomnly $ a $"), num_decimal_places=0)

        a_var.next_to(verification_brace, RIGHT)

        def _randomize_a_var(_a_var, rfv: float):
            if rfv == 1.0:
                a_var.tracker.set_value(picked_a_value)
            else:
                a_var.tracker.set_value(random.randrange(self.p))

        # actually it is irrelevant what rate_func we use since we only use the rate function's
        # value to determine the last frame of the animation
        self.scene.play(UpdateFromAlphaFunc(a_var, _randomize_a_var, rate_func=rate_functions.linear))
        self.scene.wait(.5)

        a_picked_s_a_calculated_1 = MathTex(r"a = %d \Rightarrow" % picked_a_value)

        a_picked_s_a_calculated_2 = MathTex(
            r"&%s := a = %d \\ &c := s(a) = %d" %
            (self.scene.qbf.get_name(operator_variable), picked_a_value, new_c)
        )

        a_picked_s_a_calculated_group = VGroup(a_picked_s_a_calculated_1, a_picked_s_a_calculated_2)\
            .arrange(RIGHT)\
            .next_to(verification_brace, RIGHT)

        self.scene.play(FadeOut(a_var))
        self.scene.play(Write(a_picked_s_a_calculated_group))
        self.scene.wait(.8)

        self.scene.play(FadeOut(a_picked_s_a_calculated_group), FadeOut(verification_brace))

        # qbf tree and new variable values

        new_qbf_tree = QBFTree(
            self._prover,
            new_rc,
            current_operator.get_leftmost_not_yet_resolved_variable()
        )

        cur_rc_var = self.rc_vars[operator_variable - 1]

        if not current_operator.is_linearity_operator():
            cur_rc_var.tracker.set_value(picked_a_value)
            _rc_var_update_anim = Write(cur_rc_var)
        else:
            _rc_var_update_anim = cur_rc_var.tracker.animate.set_value(picked_a_value)

        self.scene.play(
            ReplacementTransform(self.qbf_tree.get_object_group(), new_qbf_tree.get_object_group()),
            self.c_variable.tracker.animate.set_value(new_c),
            _rc_var_update_anim
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
            qbf: QBF = default_example_formula(),
            rounds_limit: int = 2,
            seed: int = 0xcafe
    ):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.qbf = qbf
        self.rounds_limit = rounds_limit
        self.seed = seed

    def construct(self):

        p = self.qbf.compute_prime_for_protocol()

        prover = HonestProver(self.qbf, p)

        observer = AnimatingObserver(self, prover, self.rounds_limit)

        run_verifier(self.qbf, prover, p, self.seed, observer)


if __name__ == "__main__":
    scene = ProtocolScene(qbf=default_example_formula(), rounds_limit=2, seed=0xcafe)
    scene.render()
