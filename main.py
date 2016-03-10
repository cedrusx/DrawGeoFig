import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

DEF_ANGLE = '='
DEF_PERP = '|'
DEF_PARA = '-'
DEFAULT_POSITIONS = [(0,0), (2,0), (1,1)]
TYPES = {'POSITION':0, 	# '(0,0)'
		 'ANGLE':1, 	# 'ABC=60', 'ABC' (meaning 'ABC=180')
		 'PERP':2, 		# 'AB|BC'
		 'PARA':3,		# 'AB-CD'
		 'UNKNOWN':4}

def gettype(rule):
	if ',' in rule:
		return TYPES['POSITION']
	if len(rule) == 3 or DEF_ANGLE in rule:
		return TYPES['ANGLE']
	if DEF_PERP in rule:
		return TYPES['PERP']
	if DEF_PARA in rule:
		return TYPES['PARA']
	return TYPES['UNKNOWN']

class RuleParser:
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
			newdot = newdot.split(',')
			newrule = newrule.rstrip(' \n').split(';')
			self.dots.extend(newdot)
			for r in newrule:
				if r is '':
					continue
				if len(r) == 2:
					self.__addlines([r])
				else:
					for d in newdot:
						self.dotrules.append((d,r))
					if len(r) == 3 or DEF_ANGLE in r:
						self.__addlines([r[0:2], r[1:3]])
					elif DEF_PERP in r:
						self.__addlines(r.split(DEF_PERP))
					elif DEF_PARA in r:
						self.__addlines(r.split(DEF_PARA))

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

	def __getdefaultposition(self):
		"""Return the next position from the list DEFAULT_POSITIONS."""
		if self.__dict__.has_key('dpcount'):
			self.dpcount += 1
			if self.dpcount == len(DEFAULT_POSITIONS):
				self.dpcount -= len(DEFAULT_POSITIONS)
		else:
			self.dpcount = 0
		return DEFAULT_POSITIONS[self.dpcount]

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

	def __getlinefromrule(self, dot, rule):
		"""For a dot, each rule can restrict it to be on a line.
		This method calculates a set of parameters (a,b) from a rule,
		such that the dot (x,y) must be on y=ax+b."""
		type = gettype(rule)
		if type is TYPES['ANGLE']:
			if len(rule) == 3:
				rotation = 180.0
			else:
				rotation = float(rule[4:])
			if rule[0] is dot:
				baseline = rule[1:3]	# 'ABC' -> 'BC'
				basedot = rule[1]
				rotation = -rotation
			elif rule[2] is dot:
				baseline = rule[1::-1]	# 'ABC' -> 'BA'
				basedot = rule[1]
			else:
				logging.error('Invalid rule: ' + rule)
				return
		elif type is TYPES['PERP'] or type is TYPES['PARA']:
			if type is TYPES['PERP']:
				rotation = 90.0
			else:
				rotation = 0.0
			if rule[0] is dot:
				basedot = rule[1]
				baseline = rule[3:5]
			elif rule[1] is dot:
				basedot = rule[0]
				baseline = rule[3:5]
			elif rule[3] is dot:
				basedot = rule[4]
				baseline = rule[0:2]
			elif rule[4] is dot:
				basedot = rule[3]
				baseline = rule[0:2]
			else:
				logging.error('Invalid rule: ' + rule)
				return
		else:
			logging.error('Unknown rule: ' + rule)
			return
		# Now we get baseline, basedot and rotation
		x0,y0 = self.positions[basedot]
		x1,y1 = self.positions[baseline[0]]
		x2,y2 = self.positions[baseline[1]]
		if x1 == x2:
			if y2 > y1:
				theta = math.pi/2
			elif y2 < y1:
				theta = -math.pi/2
			else:
				logging.error('Invalid rule (identical dots): ' + rule)
				return
		else:
			theta = math.atan((y2 - y1) / (x2 - x1))
		theta += rotation / 180.0 * math.pi
		a = math.tan(theta)
		b = y0 - a * x0
		logging.info(basedot + dot + ': y=' + str(a) + 'x+' + str(b) \
			+ ' (theta=' + str(theta / math.pi * 180) + ')')
		return a,b

	def __findintersect(self, lines):
		"""Find the intersect point of two lines.
		Each line is defined by (a,b) thus it would be y=ax+b."""
		a1,b1 = lines[0]
		a2,b2 = lines[1]
		if (a1 == a2):
			logging.warning('Oops! Parallel lines never intersect! Ignoring one rule')
			return self.__getrandompositiononline(lines[0])
		x = (b2 - b1) / (a1 - a2)
		y = (a1 * b2 - a2 * b1) / (a1 - a2)
		return (x,y)

	def __calcpositions(self):
		"""Calculate the positions of all dots in self.dots,
		based on the rules in self.dotrules."""
		for dot in self.dots:
			freedom = 2
			lines = []
			rules = self.__getrulesfordot(dot)
			logging.info(dot + ": " + str(rules))
			for rule in rules:
				type = gettype(rule)
				if type is TYPES['POSITION']:
					x,y = rule[1:-1].split(',')
					pos = (float(x), float(y))
					freedom = 0
					if len(rules) > 1:
						logging.warning('Position of ' + dot + ' is assigned. ' \
							+ 'Other rules will be ignored')
				else:
					line = self.__getlinefromrule(dot, rule)
					if line is not None:
						lines.append(line)
						freedom -= 1
				# If overdetermined, additional rules would be ignored
				if freedom == 0:
					break
			if freedom == 2:
				# Not determined - generate a random position
				pos = self.__getrandomposition()
			elif freedom == 1:
				# Underdetermined - generate a semi-random position 
				pos = self.__getrandompositiononline(lines[0])
			elif len(lines) == 2:
				# Fully determined - calculate the exact position
				pos = self.__findintersect(lines)
			self.positions[dot] = pos
			logging.info('Freedom: ' + str(freedom) + '. Position: ' + str(pos))

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