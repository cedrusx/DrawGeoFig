import math
import logging

import constraints


class RuleConstructor(object):
    """Construct a rule and shapes from a string @definition.

    Attributes:
        rule: a rule instance, or None if failed.
        shapes: a list of shapes implicitly defined in @definition.
    """

    def __init__(self, description):
        self.rule = None
        self.shapes = []
        if not description:
            return
        description = description.replace(' ', '')
        if description is '':
            return
        if len(description) is 2:
            self.shapes = [description]  # TODO shape
            return
        for Type in RuleTypes:
            if Type.bingo(description):
                self.rule = Type(description)
                self.shapes = self.rule.get_shapes()


class Rule(object):
    """Prototype for a rule class. Do NOT instantiate this class.

    Attributes:
        type: a string to describe the type of this rule.
        description: a string to describe the rule.
    """

    # Reduction of degree of freedom that a rule would impose to the
    # position of one dot, given the position of all other dots.
    # It should be overriden by subclasses.
    degree = 0

    @classmethod
    def bingo(cls, description):
        """Return True if the description string can be recognized to be
        a valid rule of this type."""
        pass

    def __init__(self, description):
        self.description = description
        self.type = self.__class__.__name__
        self.degree = self.__class__.degree

    def get_shapes(self):
        """Get the shapes implicitly defined in the rule."""
        return []

    def get_constraint_for_dot(self, dot, positions):
        """Get the constraint for a specified dot in the rule,
        provided the positions of all other dots."""
        pass

    @staticmethod
    def are_float(strings):
        """Return True if all the string in @strings are float numbers."""
        for s in strings:
            try:
                float(s)
            except ValueError:
                return False
        return True

    @staticmethod
    def get_line_by_rotation(pos0, pos1, pos2, rotation):
        """Return the coefficients (a,b) of a line that goes through @pos1,
        and is rotated by @rotation against the line from @pos1 to @pos2."""
        x0,y0 = pos0
        x1,y1 = pos1
        x2,y2 = pos2
        if x1 == x2:
            if y2 > y1:
                theta = math.pi/2
            elif y2 < y1:
                theta = -math.pi/2
            else:
                logging.error('Identical positions')
                return
        else:
            theta = math.atan((y2 - y1) / (x2 - x1))
        theta += rotation / 180.0 * math.pi
        a = math.tan(theta)
        b = y0 - a * x0
        logging.info('y=' + str(a) + 'x+' + str(b) \
            + ' (theta=' + str(theta / math.pi * 180) + ')')
        return a, b


class RulePosition(Rule):
    """Define the position of a dot.

    e.g. '(3.1,2.5)'
    """

    degree = 2
    __wrap_l = '('
    __wrap_r = ')'
    __separator = ','

    @classmethod
    def bingo(cls, description):
        """Return True if the description string can be recognized to be
        a valid rule of this type."""
        values = description[1:-1].split(cls.__separator)
        return (description[0] is cls.__wrap_l and
                description[-1] is cls.__wrap_r and
                len(values) is 2 and
                cls.are_float(values))

    def get_constraint_for_dot(self, dot, positions={}):
        """Get the constraint for a specified dot in the rule,
        provided the positions of all other dots."""
        values = self.description[1:-1].split(self.__class__.__separator)
        return constraints.Position((float(values[0]), float(values[1])))


class RulePara(Rule):
    """Make two lines be parallel.

    e.g. 'AB-CD'
    """

    degree = 1
    __separator = '-'

    @classmethod
    def bingo(cls, description):
        """Return True if the description string can be recognized to be
        a valid rule of this type."""
        lines = description.split(cls.__separator)
        return (len(lines) is 2 and
                len(lines[0]) is 2 and
                len(lines[1]) is 2)

    def get_shapes(self):
        """Get the shapes implicitly defined in the rule."""
        lines = self.description.split(self.__class__.__separator)
        return lines

    def get_constraint_for_dot(self, dot, positions):
        """Get the constraint for a specified dot in the rule,
        provided the positions of all other dots."""
        if self.description[0] is dot:
            basedot = self.description[1]
            baseline = self.description[3:5]
        elif self.description[1] is dot:
            basedot = self.description[0]
            baseline = self.description[3:5]
        elif self.description[3] is dot:
            basedot = self.description[4]
            baseline = self.description[0:2]
        elif self.description[4] is dot:
            basedot = self.description[3]
            baseline = self.description[0:2]
        else:
            logging.error('Rule %s is not for dot %s' % (self.description, dot))
            return
        return constraints.Line(self.__class__.get_line_by_rotation(
            positions[basedot], positions[baseline[0]], positions[baseline[1]],
            0))


class RulePerp(Rule):
    """Make two lines be perpendicular.

    e.g. 'AB|CD'
    """

    degree = 1
    __separator = '|'

    @classmethod
    def bingo(cls, description):
        """Return True if the description string can be recognized to be
        a valid self.description of this type."""
        lines = description.split(cls.__separator)
        return (len(lines) is 2 and
                len(lines[0]) is 2 and
                len(lines[1]) is 2)

    def get_shapes(self):
        """Get the shapes implicitly defined in the self.description."""
        lines = self.description.split(self.__class__.__separator)
        return lines

    def get_constraint_for_dot(self, dot, positions):
        """Get the constraint for a specified dot in the self.description,
        provided the positions of all other dots."""
        if self.description[0] is dot:
            basedot = self.description[1]
            baseline = self.description[3:5]
        elif self.description[1] is dot:
            basedot = self.description[0]
            baseline = self.description[3:5]
        elif self.description[3] is dot:
            basedot = self.description[4]
            baseline = self.description[0:2]
        elif self.description[4] is dot:
            basedot = self.description[3]
            baseline = self.description[0:2]
        else:
            logging.error('Rule %s is not for dot %s' % (self.description, dot))
            return
        return constraints.Line(self.__class__.get_line_by_rotation(
            positions[basedot], positions[baseline[0]], positions[baseline[1]],
            90))


class RuleAngle(Rule):
    """Define the value of a angle.

    e.g. 'ABC=45'
    """

    degree = 1
    __separator = '='

    @classmethod
    def bingo(cls, description):
        """Return True if the description string can be recognized to be
        a valid rule of this type."""
        angle, _, value = description.partition(cls.__separator)
        return (cls.__separator in description and
                len(angle) is 3 and
                cls.are_float([value]))

    def get_shapes(self):
        """Get the shapes implicitly defined in the rule."""
        lines = [self.description[0:2], self.description[1:3]]
        return lines

    def get_constraint_for_dot(self, dot, positions):
        """Get the constraint for a specified dot in the rule,
        provided the positions of all other dots."""
        rotation = float(self.description[4:])
        if self.description[0] is dot:
            baseline = self.description[1:3]    # 'ABC' -> 'BC'
            basedot = self.description[1]
            rotation = -rotation
        elif self.description[2] is dot:
            baseline = self.description[1::-1]  # 'ABC' -> 'BA'
            basedot = self.description[1]
        else:
            logging.error('Rule %s is not for dot %s' % (self.description, dot))
            return
        return constraints.Line(self.__class__.get_line_by_rotation(
            positions[basedot], positions[baseline[0]], positions[baseline[1]],
            rotation))


class RuleCollinear(RuleAngle):
    """Restrict three dots to be collinear.

    e.g. 'ABC' (is equivalent to 'ABC=180')
    """

    @classmethod
    def bingo(cls, description):
        return len(description) is 3

    def __init__(self, description):
        Rule.__init__(self, description)
        self.description = description + '=180'


RuleTypes = [RulePosition, RulePara, RulePerp, RuleAngle, RuleCollinear]


def test():
    descriptions = ['(1.3, 2.4)',
                    'AB-CD',
                    'AB|CD',
                    'ABC',
                    'ABC=32',
                    '',
                    None,
                    'AB',
                    '(1.3a,2.4)',
                    'ABC-EF',
                    ' AB',
                    'ABCD',
                    'ABC=32a',
                    'ABCD=32']
    for d in descriptions:
        print d
        self.description_constructor = self.descriptionConstructor(d)
        if rule_constructor.rule:
            print '%s --> Type: %s. Shapes: %s' % (
                rule_constructor.rule.description,
                rule_constructor.rule.type,
                rule_constructor.shapes)
        else:
            print '%s --> Invalid rule' % d

if __name__ == '__main__':
    test()