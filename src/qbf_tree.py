from manim import *
from qbf import QBF


class QBFTreeNode:

    def __init__(self):
        pass

    def get_value(self) -> int:
        raise NotImplementedError()

    def get_object_group(self):
        raise NotImplementedError()


class QBFTreeNonLeafNode(QBFTreeNode):

    def __init__(self, qbf: QBF, p: int, random_choices: dict, first_var: int, cur_var: int):
        super().__init__()
        assert first_var >= 1
        assert cur_var >= 1

        v_0_rc = random_choices.copy()
        v_1_rc = random_choices.copy()

        if cur_var >= first_var:
            v_0_rc[cur_var] = 0
            v_1_rc[cur_var] = 1
        else:
            assert cur_var in random_choices
            v_0_rc[cur_var] = random_choices[cur_var]
            v_1_rc[cur_var] = random_choices[cur_var]

        self.v_0_child = _construct_node(qbf, p, v_0_rc, first_var, cur_var + 1)
        self.v_1_child = _construct_node(qbf, p, v_1_rc, first_var, cur_var + 1)

        if qbf.get_quantification(cur_var) == QBF.Q_FORALL:
            self._value = self.v_0_child.get_value() * self.v_1_child.get_value()
        else:
            assert qbf.get_quantification(cur_var) == QBF.Q_EXISTS
            self._value = self.v_0_child.get_value() + self.v_1_child.get_value()

        self._value %= p

        self.text = MathTex(qbf.get_variable_latex_operator(cur_var), "[%d]" % self._value)

        self.text[0].set_color(RED_C if qbf.get_quantification(cur_var) == QBF.Q_FORALL else GOLD_C)

        self.text.scale(.75)

        self.box = SurroundingRectangle(self.text, corner_radius=.1, color=BLUE)\
            .set_z_index(5)

        group = VGroup(self.text, self.box)

        v_0_group = self.v_0_child.get_object_group()
        v_1_group = self.v_1_child.get_object_group()

        children_group = VGroup(v_0_group, v_1_group)

        if cur_var == qbf.get_variable_count():
            # children are leafes, it would be a good idea to increase the buffer slightly
            buff = group.width - min(v_0_group.width, v_1_group.width)
            children_group.arrange(RIGHT, buff=buff)
        else:
            children_group.arrange(RIGHT)

        group.next_to(children_group, UP)

        self.v_0_line = Line(group.get_left(), v_0_group.get_top(), color=RED_C)
        self.v_1_line = Line(group.get_right(), v_1_group.get_top(), color=GREEN_C)

    def get_value(self) -> int:
        return self._value

    def get_object_group(self):

        v_0_group = self.v_0_child.get_object_group()
        v_1_group = self.v_1_child.get_object_group()

        return VGroup(
            VGroup(self.text, self.box),
            VGroup(self.v_0_line, self.v_1_line),
            VGroup(v_0_group, v_1_group)
        )


class QBFTreeLeafNode(QBFTreeNode):

    def __init__(self, qbf: QBF, p: int, random_choices: dict):
        super().__init__()

        eval_subs = {}

        for var, val in random_choices.items():
            eval_subs[qbf.get_symbol(var)] = val

        arithmetization = qbf.arithmetize_matrix()
        self._value = int(arithmetization.eval(eval_subs).as_poly(arithmetization.gens).LC())
        self._value %= p

        self.text = Integer(self._value, 0).scale(.75)

        self.box = SurroundingRectangle(self.text, color=GOLD, corner_radius=.1)

        VGroup(self.text, self.box).to_edge(DOWN)

    def get_value(self) -> int:
        return self._value

    def get_object_group(self):
        return VGroup(self.text, self.box)


def _construct_node(qbf: QBF, p: int, random_choices: dict, first_var: int, cur_var: int = 1) -> QBFTreeNode:
    assert first_var >= 1
    assert first_var <= qbf.get_variable_count()
    assert cur_var >= 1
    assert cur_var <= qbf.get_variable_count() + 1

    if cur_var > qbf.get_variable_count():
        return QBFTreeLeafNode(qbf, p, random_choices)

    return QBFTreeNonLeafNode(qbf, p, random_choices, first_var, cur_var)


class QBFTree:

    # first_var is the id of the first variable that has not yet been resolved
    # this means that from that variable (inclusive), the arithmetization should
    # be evaluated at zeros or ones for all variable assignments
    # before the first_var, the value from the random_choices dictionary should be used
    # for the calculation
    def __init__(self, qbf: QBF, p: int, random_choices: dict, first_var: int):
        assert first_var >= 1

        # if first_variable is one greater than the maximum id of an existent variable
        # then this means that the tree should be built for the matrix
        # which of course means that the tree will be simply one leaf node
        assert first_var <= qbf.get_variable_count() + 1

        for v_with_random_value in range(1, first_var):
            assert v_with_random_value in random_choices,\
                "Was expecting value for variable %d" % v_with_random_value

        self.first_variable = first_var

        # TODO: construct the qbf tree in a way such that random_choices are visible

        self.root = _construct_node(qbf, p, random_choices, first_var)

    def get_object_group(self):
        return self.root.get_object_group().center()
