import sys
import math
import numpy as np
import matplotlib.pyplot as plt

DEF_ANGLE = '='
DEF_PERP = '|'
DEF_PARA = '-'
DEFAULT_POSITIONS = [(0,0), (2,0), (1,1)]
TYPES = {'POSITION':0, 	# '(0,0)'
		 'ANGLE':1, 	# 'ABC=60', 'ABC' (meaning 'ABC=180')
		 'PERP':2, 		# 'AB-BC'
		 'PARA':3,		# 'AB|CD'
		 'UNKNOWN':4}

def debug(message):
	print message

def addline(lines, newlines):
	for new in newlines:
		if sorted(new) not in lines:
			lines.append(sorted(new))
			
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

def parse(input):
	dots = []
	dotrules = []
	lines = []
	while True:
		line = input.readline()
		if not line:
			return dots, dotrules, lines
		newdot, newrule = line.split(':')
		newdot = newdot.split(',')
		newrule = newrule.rstrip(' \n').split(';')
		dots.extend(newdot)
		for r in newrule:
			if len(r) == 2:
				lines.append(sorted(r))
			else:
				for d in newdot:
					dotrules.append((d,r))
				if len(r) == 3 or DEF_ANGLE in r:
					addline(lines, [r[0:2], r[1:3]])
				elif DEF_PERP in r:
					addline(lines, r.split(DEF_PERP))
				elif DEF_PARA in r:
					addline(lines, r.split(DEF_PARA))

def getrulesfordot(dot, dotrules):
	rules = []
	for r in dotrules:
		if r[0] == dot:
			rules.append(r[1])
	return rules

def defaultposition():
	if defaultposition.__dict__.has_key('count'):
		defaultposition.count += 1
		if defaultposition.count == len(DEFAULT_POSITIONS):
			defaultposition.count -= len(DEFAULT_POSITIONS)
	else:
		defaultposition.count == 0
	return DEFAULT_POSITIONS(defaultposition.count)

def getlinefromrule(dot, positions, rule):
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
			print 'Invalid rule: ', rule
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
			baseline = rule[0:1]
		elif rule[4] is dot:
			basedot = rule[3]
			baseline = rule[0:1]
		else:
			print 'Invalid rule: ', rule	
	else:
		print 'Unknown rule: ', rule
	# Now we get baseline, basedot and rotation
	x0,y0 = positions[basedot]
	x1,y1 = positions[baseline[0]]
	x2,y2 = positions[baseline[1]]
	if x1 == x2:
		if y2 > y1:
			theta = math.pi/2
		elif y2 < y1:
			theta = -math.pi/2
		else:
			print 'Invalid rule (identical dots): ', rule
	else:
		theta = math.atan((y2 - y1) / (x2 - x1))
	print 'dot:', dot, 'rule:', rule
	print baseline, 'theta =', theta / math.pi * 180, 'rotation =', rotation
	theta += rotation / 180.0 * math.pi
	a = math.tan(theta)
	b = y0 - a * x0
	print basedot + dot, 'theta =', theta / math.pi * 180, 'y=' + str(a) + 'x+' + str(b)
	return a,b

def findintersect(lines):
	"""Find the intersect point of two lines.
	Each line is defined by (a,b) thus it would be y=ax+b."""
	a1,b1 = lines[0]
	a2,b2 = lines[1]
	if (a1 == a2):
		print 'Error! Parallel lines never intersect!'
		return
	x = (b2 - b1) / (a1 - a2)
	y = (a1 * b2 - a2 * b1) / (a1 - a2)
	return (x,y)
	
def calculate(dots, dotrules):
	positions = {}
	for dot in dots:
		freedom = 2
		lines = []
		rules = getrulesfordot(dot, dotrules)
		for rule in rules:
			type = gettype(rule)
			if type is TYPES['POSITION']:
				x,y = rule[1:-1].split(',')
				pos = (float(x), float(y))
				freedom = 0
				if len(rules) > 1:
					print 'Position of ', dot, ' is assigned. ', \
						'Other rules will be ignored'
			else:
				lines.append(getlinefromrule(dot, positions, rule))
				freedom -= 1
			if freedom == 0:
				break
		if freedom == 2:	# 
			print 'Position of ', dot, ' is not defined. ', \
				'Default position will be used.'
			pos = defaultposition()
		elif freedom == 1:
			# TODO: underdetermined
			print 'Position of ', dot, ' is underdetermined.' \
				'I don\'t know what to do'
			pos = (0, 0)
		elif len(lines) == 2:
			pos = findintersect(lines)
		positions[dot] = pos
		print dot + ': (' + str(pos[0]) + ',' + str(pos[1]) + ')'
	return positions

def main():
	if len(sys.argv) == 2:
		infile = sys.argv[1]
	else:
		print 'USAGE: python ' + sys.argv[0] + ' FILENAME'
		return
	input = open(infile, 'r')
	dots, dotrules, lines = parse(input)
	positions = calculate(dots, dotrules)
	print positions
	for line in lines:
		plt.plot([positions[line[0]][0],positions[line[1]][0]], \
			[positions[line[0]][1],positions[line[1]][1]], '-ok')
		plt.hold('on')
	for dot in dots:
		plt.text(positions[dot][0] + 0.03, positions[dot][1] + 0.03, dot)
	plt.axis('equal')
	plt.axis('off')
	plt.grid('on')
	plt.show()

if __name__ == '__main__':
	main()