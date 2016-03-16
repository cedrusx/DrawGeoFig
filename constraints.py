import logging

class Calculator(object):

    def get_position(self, constraints):
        """Return a position meeting all the constraints, or None if fails."""
        if len(constraints) is 1 and constraints[0].type is 'Position':
            return constraints[0].position
        elif (len(constraints) is 2 and constraints[0].type is 'Line'
                                    and constraints[1].type is 'Line'):
            return self.__line_line(constraints[0], constraints[1])
        else:
            return

    def __line_line(self, line1, line2):
        """Find the intersect point of two lines.
        Each line is defined by (a,b) thus it would be y=ax+b."""
        a1,b1 = line1.coefficients
        a2,b2 = line2.coefficients
        if (a1 == a2):
            logging.warning('Oops! Parallel lines never intersect! Ignoring one rule')
            return
        x = (b2 - b1) / (a1 - a2)
        y = (a1 * b2 - a2 * b1) / (a1 - a2)
        return (x,y)


class Position(object):
    def __init__(self, position):
        self.type = self.__class__.__name__
        self.position = position


class Line(object):
    def __init__(self, coefficients):
        self.type = self.__class__.__name__
        self.coefficients = coefficients


class Circle(object):
    def __init__(self, center, radius):
        self.type = self.__class__.__name__
        self.center = center
        self.radius = radius