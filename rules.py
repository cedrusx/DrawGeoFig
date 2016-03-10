class Rule:
	""""""
	def __init__(self, description):
		self.description = description
		self.type = self.gettype()
		self.shapes = self.initshapes()

	def gettype(self):
		return 'Base'

	def initshapes(self):
		""""""
		return []

	@classmethod
	def bingo(cls, description):
		return cls.separator in description

	def getlinefordot(self, dot, positions):
		pass

	def draw(self):
		pass

class RulePara(Rule):
	separator = '-'
	def gettype(self):
		return 'Para'

class RulePerp(Rule):
	separator = '|'
	def gettype(self):
		return 'Para'

class RuleConstructor:
	"""Determine the type of rule from a rule definition and 
	return a corresponding rule instance"""
	def __call__(cls, description):
		for Type in RuleTypes:
			if Type.bingo(description):
				return Type(description)
		return None

def test():
	descriptions = ['AB|CD', 'AB-CD', 'ABCD']
	for d in descriptions:
		print d
		rule = RuleConstructor()(d)
		if rule is not None:
			print rule.type

RuleTypes = [RulePara, RulePerp]

if __name__ == '__main__':
	test()