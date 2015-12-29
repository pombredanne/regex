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
		initializes the state with an empty set of connections
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

	def __repr__(self, level = 0, visited = []):
		"""
		prints the id of the current state, then recursively prints its 
		connections, its connections' connections, etc.

		level: determines the offset for each level of the printed NFA
		visited: tracks the printed states, so that states' connections are 
			not printed twice
		"""
		offset = "  " * level
		rep = offset + str(id(self)) + "\n"

		if id(self) not in visited:
			# We add the id of the state to the list of visited states.
			visited.append(id(self))
			for (value, state) in self.connections:
				# The id of each state will be indented based on its distance from 
				# the initial state.
				rep += value + state.__repr__(level + 1, visited)

		return rep


def regexToNfa(postfixRegex):
	"""
	Converts a postfix regex into an NFA.

	postfixRegex: the regex to convert

	returns: a corresponding NFA.
	"""
	# A stack of the computed sub-NFAs.
	ops = []

	for char in postfixRegex:
		# Each character is linked to a function which constructs the 
		# appropriate NFA using the top element(s) of the stack.
		if char == ',':
			op2 = ops.pop()
			op1 = ops.pop()
			ops.append(regConcat(op1, op2))
		elif char == '|':
			op2 = ops.pop()
			op1 = ops.pop()
			ops.append(regOr(op1, op2))
		elif char == '*':
			op1 = ops.pop()
			ops.append(regZeroOrMore(op1))
		elif char == '+':
			op1 = ops.pop()
			ops.append(regOneOrMore(op1))
		elif char == '?':
			op1 = ops.pop()
			ops.append(regZeroOrOne(op1))
		else:
			ops.append(regChar(char))

	return(ops.pop())


def regChar(a):
	"""
	converts a non-operator character into an NFA

	a: the input character

	returns: the resulting NFA
	"""
	start, end = State(), State()

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
	a.inState.addConnection('e', b.inState)
	b.outState.addConnection('e', a.outState)

	return Nfa(a.inState, a.outState)

def regZeroOrMore(a):
	"""
	converts an NFA into a zero-or-more NFA

	a: the input NFA

	returns: the resulting NFA
	"""
	a.outState.addConnection('e', a.inState)

	return Nfa(a.inState, a.inState)

def regOneOrMore(a):
	"""
	converts an NFA into a one-or-more NFA

	a: the input NFA

	returns: the resulting NFA
	"""
	a.outState.addConnection('e', a.inState)

	return Nfa(a.inState, a.outState)

def regZeroOrOne(a):
	"""
	converts an NFA into a zero-or-one NFA

	a: the input NFA

	returns: the resulting NFA
	"""
	a.inState.addConnection('e', a.outState)

	return Nfa(a.inState, a.outState)

print(regexToNfa('abc|,'))