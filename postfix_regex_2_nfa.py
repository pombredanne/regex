# Converts postfix regexes to nondeterministic finite automata.


class Nfa:
	"""
	a nondeterministic finite automaton. Takes the form of a black box around 
	a set of connected states, exposing only the input state (so that 
	expressions can be parsed and NFAs can be linked) and the output state 
	(again, so that NFAs can be linked).
	"""
	def __init__(self, inState, outState):
		"""
		initializes the NFA with empty input and output states.

		inState: the NFA's input state
		outState: the NFA's output state
		"""
		self.inState = inState
		self.outState = outState

	def __repr__(self):
		"""
		prints the input state, which will recursively print the other states.
		"""
		return str(self.inState)


class State:
	"""
	a state of a nondeterministic finite automaton. Holds connections to other 
	states.
	"""
	def __init__(self):
		"""
		initializes the state with an empty set of connections.
		"""
		self.connections = []

	def addConnection(self, value, state):
		"""
		adds a connection to another state.

		value: the input consumed by the connection
		state: the state the connection leads to

		returns: void
		"""
		self.connections.append((value, state))

	def __repr__(self, level = 0):
		"""
		prints the id of the current state, then recursively prints its 
		connections, its connections' connections, etc.

		level: determines the offset for each level of the printed NFA
		"""
		offset = "  " * level
		rep = offset + str(id(self)) + "\n"

		for (value, state) in self.connections:
			# The id of each state will be indented based on its distance from 
			# the initial state.
			rep += value + state.__repr__(level + 1)

		return rep


def regexToNfa(postfixRegex):
	"""
	Converts a postfix regex into an NFA.

	postfixRegex: the regex to convert

	returns: a corresponding NFA.
	"""
	# op1 holds the accumulated NFA, while op2 holds a secondary NFA for 
	# binary operations.
	op1 = None
	op2 = None

	for char in postfixRegex:
		# Each operator is linked to a function which constructs the 
		# appropriate NFA using op1 and op2 (in the case of binary operators).
		if char == ',':
			op1 = regConcat(op1, op2)
		elif char == '|':
			op1 = regOr(op1, op2)
		elif char == '+':
			op1 = regOneOrMore(op1)
		elif char == '*':
			op1 = regZeroOrMore(op1)
		elif char == '?':
			op1 = regZeroOrOne(op1)		

		# Non-operator characters are converted to NFAs and are stored in 
		# either op1 (for the first character encountered) or op2 (for all 
		# remaining characters).
		else:
			automaton = regChar(char)
			if not op1:
				op1 = automaton
			else:
				op2 = automaton

	return(op1)


def regChar(a):
	"""
	converts a non-operator character into an NFA

	a: the input character

	returns: the resulting NFA
	"""
	start = State()
	end = State()
	start.addConnection(a, end)

	return Nfa(start, end)

def regConcat(a, b):
	"""
	combines two NFAs into a single concatenated NFA

	a: the first NFA
	b: the second NFA

	returns: the resulting NFA
	"""
	a.outState.addConnection('e', b.inState)

	return Nfa(a.inState, b.outState)

def regOr(a, b):
	"""
	combines two NFAs into a single either/or NFA

	a: the first NFA
	b: the second NFA

	returns: the resulting NFA
	"""
	start = State()
	start.addConnection('e', a.inState)
	start.addConnection('e', b.inState)

	end = State()
	a.outState.addConnection('e', end)
	b.outState.addConnection('e', end)

	return Nfa(start, end)
