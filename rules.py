class RuleConstructor:
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

    type = 'base'  # Should be overriden by subclasses

    @classmethod
    def bingo(cls, description):
        """Return True if the description string can be recognized to be
        a valid rule of this type."""
        pass

    def __init__(self, description):
        self.description = description
        self.type = self.__class__.type

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


class RulePosition(Rule):
    """Define the position of a dot.

    e.g. '(3.1,2.5)'
    """
    type = 'position'
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

    def get_constraint_for_dot(self, dot, positions):
        """Get the constraint for a specified dot in the rule,
        provided the positions of all other dots."""
        pass


class RulePara(Rule):
    """Make two lines be parallel.

    e.g. 'AB-CD'
    """

    type = 'para'
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
        pass


class RulePerp(Rule):
    """Make two lines be perpendicular.

    e.g. 'AB|CD'
    """

    type = 'perp'
    __separator = '|'

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
        pass


class RuleAngle(Rule):
    """Define the value of a angle.

    e.g. 'ABC=45'
    """

    type = 'angle'
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
        pass


class RuleCollinear(RuleAngle):
    """Restrict three dots to be collinear.

    e.g. 'ABC' (is equivalent to 'ABC=180')
    """

    @classmethod
    def bingo(cls, description):
        return len(description) is 3

    def __init__(self, description):
        self.description = description + '=180'
        self.type = self.__class__.type


RuleTypes = [RulePosition, RulePara, RulePerp, RuleAngle, RuleCollinear]


def test():
    descriptions = ['(1.3, 2.4)',
                    'AB-CD',
                    'AB|CD',
                    'ABC',
                    'ABC=32',
                    None,
                    '',
                    'AB',
                    '(1.3a,2.4)',
                    'ABC-EF',
                    ' AB',
                    'ABCD',
                    'ABC=32a',
                    'ABCD=32']
    for d in descriptions:
        print d
        rule_constructor = RuleConstructor(d)
        if rule_constructor.rule:
            print '%s --> Type: %s. Shapes: %s' % (
                rule_constructor.rule.description,
                rule_constructor.rule.type,
                rule_constructor.shapes)
        else:
            print '%s --> Invalid rule' % d

if __name__ == '__main__':
    test()