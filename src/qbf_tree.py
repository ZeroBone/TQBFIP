import math
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

    def __init__(self, qbf: QBF, p: int, random_choices: dict, variable: int):
        super().__init__()
        assert variable >= 1

        self._v = variable

        v_0_rc = random_choices.copy()
        v_0_rc[self._v] = 0

        v_1_rc = random_choices.copy()
        v_1_rc[self._v] = 1

        self.v_0_child = _construct_node(qbf, p, v_0_rc, self._v + 1)
        self.v_1_child = _construct_node(qbf, p, v_1_rc, self._v + 1)

        if qbf.get_quantification(self._v) == QBF.Q_FORALL:
            self._value = self.v_0_child.get_value() * self.v_1_child.get_value()
        else:
            assert qbf.get_quantification(self._v) == QBF.Q_EXISTS
            self._value = self.v_0_child.get_value() + self.v_1_child.get_value()

        self._value %= p

        self.text = Integer(
            self._value,
            math.ceil(math.log10(p - 1)) + 1
        )

        self.box = SurroundingRectangle(self.text, corner_radius=.2)

        v_0_group = self.v_0_child.get_object_group()
        v_1_group = self.v_1_child.get_object_group()

        group = VGroup(self.text, self.box).next_to(VGroup(v_0_group, v_1_group), LEFT, 1.5)

        self.v_0_line = Line(group.get_bottom(), v_0_group.get_left())
        self.v_1_line = Line(group.get_top(), v_1_group.get_left())

    def get_value(self) -> int:
        return self._value

    def get_object_group(self):
        return VGroup(self.text, self.box, VGroup(self.v_0_line, self.v_1_line)).arrange(RIGHT)


class QBFTreeLeafNode(QBFTreeNode):

    def __init__(self, qbf: QBF, p: int, random_choices: dict):
        super().__init__()

        eval_subs = {}

        for var, val in random_choices.items():
            eval_subs[qbf.get_symbol(var)] = val

        arithmetization = qbf.arithmetize_matrix()
        self._value = int(arithmetization.eval(eval_subs).as_poly(arithmetization.gens).LC())
        self._value %= p

        self.text = Integer(
            self._value,
            math.ceil(math.log10(p - 1)) + 1
        )

        self.box = SurroundingRectangle(self.text, corner_radius=.2)

    def get_value(self) -> int:
        return self._value

    def get_object_group(self):
        return VGroup(self.text, self.box)


def _construct_node(qbf: QBF, p: int, random_choices: dict, first_variable: int) -> QBFTreeNode:
    assert first_variable >= 1

    if first_variable >= qbf.get_variable_count():
        return QBFTreeLeafNode(qbf, p, random_choices)

    return QBFTreeNonLeafNode(qbf, p, random_choices, first_variable)


class QBFTree:

    def __init__(self, qbf: QBF, p: int, random_choices: dict, first_variable: int):
        assert first_variable >= 1
        assert first_variable <= qbf.get_variable_count()

        self.first_variable = first_variable

        self.root = _construct_node(qbf, p, random_choices, first_variable)

    def get_object_group(self):
        return self.root.get_object_group()
