from manim import *
from qbf import QBF
from prover import HonestProver, ProofOperator


class _TextBox:

    def __init__(self, qbf: QBF, cur_var: int, value: int):

        self.text = MathTex(qbf.get_variable_latex_operator(cur_var), "[%d]" % value)

        self.text[0].set_color(RED_C if qbf.get_quantification(cur_var) == QBF.Q_FORALL else GOLD_C)

        self.text.scale(.75)

        self.box = SurroundingRectangle(self.text, corner_radius=.1, color=BLUE) \
            .set_z_index(5)

        self.group = VGroup(self.text, self.box)


class QBFTreeNode:

    def __init__(self):
        pass

    def get_object_group(self):
        raise NotImplementedError()


class QBFTreeRandomChoiceQuantifierNode(QBFTreeNode):

    def __init__(self, prover: HonestProver, rc: dict, first_var: int, cur_op: ProofOperator):
        super().__init__()

        assert first_var >= 1
        assert cur_op.v >= 1
        assert cur_op.v < first_var, "the current variable is not a random choice variable"
        assert cur_op.v in rc

        self._v_child = _construct_node(prover, rc, first_var, cur_op.next_quantifier_operator())

        self._value = prover.eval_polynomial_at_operator(rc, cur_op)

        # TODO: make TextBox support proof operators and display linearity operator there
        self.text_box = _TextBox(prover.qbf, cur_op.v, self._value)

        children_group = self._v_child.get_object_group()

        # children_group.arrange(RIGHT)
        self.text_box.group.next_to(children_group, UP)

        self.v_line = Line(self.text_box.group.get_bottom(), children_group.get_top(), color=PURPLE)

    def get_object_group(self):

        return VGroup(
            self.text_box.group,
            self.v_line,
            self._v_child.get_object_group()
        )


class QBFTreeQuantifierNode(QBFTreeNode):

    def __init__(self, prover: HonestProver, rc: dict, first_var: int, cur_op: ProofOperator):
        super().__init__()

        assert first_var >= 1
        assert not cur_op.is_linearity_operator()
        assert cur_op.v >= 1
        assert cur_op.v >= first_var, "the current variable is a random choice variable"

        v_0_rc = rc.copy()
        v_1_rc = rc.copy()

        v_0_rc[cur_op.v] = 0
        v_1_rc[cur_op.v] = 1

        self.v_0_child = _construct_node(prover, v_0_rc, first_var, cur_op.next_quantifier_operator())
        self.v_1_child = _construct_node(prover, v_1_rc, first_var, cur_op.next_quantifier_operator())

        self._value = prover.eval_polynomial_at_operator(rc, cur_op)

        self._text_box = _TextBox(prover.qbf, cur_op.v, self._value)

        v_0_group = self.v_0_child.get_object_group()
        v_1_group = self.v_1_child.get_object_group()

        children_group = VGroup(v_0_group, v_1_group)

        if cur_op.v == prover.qbf.get_variable_count():
            # children are leafes, it would be a good idea to increase the buffer slightly
            buff = self._text_box.group.width - min(v_0_group.width, v_1_group.width)
            children_group.arrange(RIGHT, buff=buff)
        else:
            children_group.arrange(RIGHT)

        self._text_box.group.next_to(children_group, UP)

        self._v_0_line = Line(self._text_box.group.get_left(), v_0_group.get_top(), color=RED_C)
        self._v_1_line = Line(self._text_box.group.get_right(), v_1_group.get_top(), color=GREEN_C)

    def get_object_group(self):

        v_0_group = self.v_0_child.get_object_group()
        v_1_group = self.v_1_child.get_object_group()

        return VGroup(
            self._text_box.group,
            VGroup(self._v_0_line, self._v_1_line),
            VGroup(v_0_group, v_1_group)
        )


class QBFTreeLeafNode(QBFTreeNode):

    def __init__(self, prover: HonestProver, rc: dict):
        super().__init__()

        self._value = prover.eval_polynomial_at_operator(rc)

        self._text = Integer(self._value, 0).scale(.75)

        self._box = SurroundingRectangle(self._text, color=GOLD, corner_radius=.1)

        VGroup(self._text, self._box).to_edge(DOWN)

    def get_object_group(self):
        return VGroup(self._text, self._box)


def _construct_node(
        prover: HonestProver,
        rc: dict,
        first_var: int,
        cur_op: ProofOperator = ProofOperator()) -> QBFTreeNode:

    assert first_var >= 1
    assert first_var <= prover.qbf.get_variable_count() + 1
    assert cur_op.v >= 1
    assert cur_op.v <= prover.qbf.get_variable_count() + 1

    if cur_op.v > prover.qbf.get_variable_count():
        return QBFTreeLeafNode(prover, rc)

    # the node is a quantifier node

    if cur_op.v >= first_var:
        return QBFTreeQuantifierNode(prover, rc, first_var, cur_op)

    return QBFTreeRandomChoiceQuantifierNode(prover, rc, first_var, cur_op)


class QBFTree:

    # first_var is the id of the first variable that has not yet been resolved
    # this means that from that variable (inclusive), the arithmetization should
    # be evaluated at zeros or ones for all variable assignments
    # before the first_var, the value from the rc dictionary should be used
    # for the calculation
    def __init__(self, prover: HonestProver, rc: dict, first_var: int):
        assert first_var >= 1

        # if first_variable is one greater than the maximum id of an existent variable
        # then this means that the tree should be built for the matrix
        # which of course means that the tree will be simply one leaf node
        assert first_var <= prover.qbf.get_variable_count() + 1

        for v_with_random_value in range(1, first_var):
            assert v_with_random_value in rc,\
                "Was expecting value for variable %d" % v_with_random_value

        self.root = _construct_node(prover, rc, first_var)

    def get_object_group(self):
        return self.root.get_object_group().center()
