import sys
import random
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

import rules
import constraints


class RuleParser(object):
    """A parser to get rules from an input stream.

    Attributes:
        dots: a list of names like ['A','B']
        lines: a list of dot pairs like [['A','B'],['B','C']]
        dotrules: a list of dot-rule pairs
    """

    def __init__(self):
        self.dots = []
        self.lines = []
        self.dotrules = []

    def parse(self, input):
        while True:
            line = input.readline()
            if not line:
                break
            newdot, newrule = line.split(':')
            newdots = newdot.split(',')
            newrules = newrule.rstrip(' \n').split(';')
            self.dots.extend(newdots)
            for r in newrules:
                rule_constructor = rules.RuleConstructor(r)
                if rule_constructor.rule:
                    for d in newdots:
                        self.dotrules.append(
                            (d, rule_constructor.rule))
                self.__addlines(rule_constructor.shapes)

    def __addlines(self, newlines):
        """Avoid duplication when adding a line into self.lines."""
        for new in newlines:
            if sorted(new) not in self.lines:
                self.lines.append(sorted(new))


class SmartCalc(RuleParser):
    """Init me with an input stream giving rules, then I'll give you the world

    Attributes:
        positions: a dict containing the coordinates of each dot
    """

    def __init__(self, input):
        """All works should be done here."""
        RuleParser.__init__(self)
        self.parse(input)
        self.positions = {}
        self.__calcpositions()

    def __getrulesfordot(self, dot):
        """Return all rules for a specified dot."""
        rules = []
        for r in self.dotrules:
            if r[0] == dot:
                rules.append(r[1])
        return rules

    def __getrandomposition(self):
        """Return a random position not too far away from current positions."""
        cp = self.positions.values() # current positions for reference
        if len(cp) == 0: # No reference positions
            return (random.gauss(0, 1), random.gauss(0, 1))
        xmin,ymin = xmax,ymax = cp[0]
        for x,y in cp[1:]:
            xmin = min(xmin, x)
            ymin = min(ymin, y)
            xmax = max(xmax, x)
            ymax = max(ymax, y)
        if xmin == xmax and ymin == ymax: # Only one reference position
            return (cp[0][0] + random.gauss(0, 1),
                    cp[0][1] + random.gauss(0, 1))
        std = max(xmax - xmin, ymax - ymin)
        return (random.gauss((xmax + xmin) / 2, std),
                random.gauss((ymax + ymin) / 2, std))

    def __getrandompositiononline(self, line):
        """Return a random position on a given line."""
        cp = self.positions.values() # current positions for reference
        if len(cp) == 0: # No reference positions
            px = random.gauss(0, 1)
        else:
            xmin,ymin = xmax,ymax = cp[0]
            for x,y in cp[1:]:
                xmin = min(xmin, x)
                ymin = min(ymin, y)
                xmax = max(xmax, x)
                ymax = max(ymax, y)
            if xmin == xmax and ymin == ymax: # Only one reference position
                px = cp[0][0]
            else:
                std = max(xmax - xmin, ymax - ymin)
                px = random.gauss((xmax + xmin) / 2, std)
        py = line[0] * px + line[1]
        return (px,py)

    def __calcpositions(self):
        """Calculate the positions of all dots in self.dots,
        based on the rules in self.dotrules."""
        for dot in self.dots:
            consts = []
            rules = self.__getrulesfordot(dot)
            logging.info("%s: %s" % (dot, rules))
            freedom = 2
            for rule in rules:
                if rule.degree <= freedom:
                    consts.append(rule.get_constraint_for_dot(dot, self.positions))
                elif rule.degree is 2 and freedom is 1:
                    consts = [rule.get_constraint_for_dot(dot, self.positions)]
                freedom -= rule.degree
            if freedom <= 0:
                pos = constraints.Calculator().get_position(consts)
                if pos is None and consts[0].type is 'Line':
                    pos = self.__getrandompositiononline(
                        consts[0].coefficients)
            elif freedom is 1 and consts[0].type is 'Line':
                # Underdetermined - generate a semi-random position
                pos = self.__getrandompositiononline(
                    consts[0].coefficients)
            elif freedom is 2:
                # Not determined - generate a random position
                pos = self.__getrandomposition()
            else:
                pos = None
            if pos:
                self.positions[dot] = pos
                logging.info('Freedom: %d. Position: %s' % (
                    freedom, (self.positions[dot],)))
            else:
                logging.error('Failed to calculate position. Find the bug!')


def main():
    if len(sys.argv) == 2:
        infile = sys.argv[1]
    else:
        print 'USAGE: python ' + sys.argv[0] + ' FILENAME'
        return
    input = open(infile, 'r')
    calc = SmartCalc(input)
    print calc.positions
    for line in calc.lines:
        plt.plot([calc.positions[line[0]][0], calc.positions[line[1]][0]], \
            [calc.positions[line[0]][1], calc.positions[line[1]][1]], '-ok')
        plt.hold('on')
    for dot in calc.dots:
        plt.text(calc.positions[dot][0] + 0.03, calc.positions[dot][1] + 0.03, dot)
    plt.axis('equal')
    plt.axis('off')
    plt.grid('on')
    plt.show()

if __name__ == '__main__':
    main()