#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Converts postfix regex strings into regexes.


class Regex:
	"""
	a regex based on a nondeterministic finite automaton. Takes the form of a 
	black box around a set of connected states, exposing only the input state 
	and the output states used to match strings.
	"""

	def __init__(self, postfixRegex):
		"""
		creates a regex based on a regex string in postfix notation

		postfixRegex: the regex string in postfix notation
		"""
		# A stack of pairs of states, representing the input and output states 
		# of notional NFAs.
		ops = []

		for char in postfixRegex:
			# Each character is linked to a function which uses the top 
			# element(s) of the stack to return the appropriate input/output 
			# pair.
			if char == '&':
				(bIn, bOut), (aIn, aOut) = ops.pop(), ops.pop()
				aOut.addConnection('ε', bIn)
				ops.append((aIn, bOut))

			elif char == '|':
				(bIn, bOut), (aIn, aOut) = ops.pop(), ops.pop()
				aIn.addConnection('ε', bIn)
				bOut.addConnection('ε', aOut)
				ops.append((aIn, aOut))

			elif char == '*':
				(aIn, aOut) = ops.pop()

				aOut.addConnection('ε', aIn)

				ops.append((aIn, aIn))

			elif char == '+':
				(aIn, aOut) = ops.pop()
				aOut.addConnection('ε', aIn)
				ops.append((aIn, aOut))

			elif char == '?':
				(aIn, aOut) = ops.pop()
				aIn.addConnection('ε', aOut)
				ops.append((aIn, aOut))

			else:
				start, end = State(), State()
				start.addConnection(char, end)
				ops.append((start, end))

		self.inState, _ = ops.pop()
		self.outStates = self._removeEpsilonConnections()


	def __repr__(self):
		"""
		prints the input state, which will recursively print the other states.
		"""
		return str(self.inState)


	def _removeEpsilonConnections(self):
		"""
		from an NFAs start state, moves through the network removing all epsilon 
			connections

		startState: the start-state for the NFA

		returns: a list of end-states for the pruned NFA
		"""
		statesToTraverse, outStates = [self.inState], set()

		for currentState in statesToTraverse:
			# An ε-closure is the set of all the states reachable via ε-
			# connections of the current state. The new connections are all the 
			# external connections of the ε-closure.
			eClosure, newConnections = [currentState], set()
			for state in eClosure:
				for (value, connectedState) in state.connections:
					# If a connection is an ε-connection, we add it to the ε-
					# closure.
					if value == 'ε':
						eClosure.append(connectedState)
					# Otherwise, we add it to the set of new connections, and to 
					# the list of states to traverse (if not already present).
					else:
						newConnections.add((value, connectedState))
						if connectedState not in statesToTraverse:
							statesToTraverse.append(connectedState)

			# If a state's ε-closure has no external connections, that means that 
			# it's an end-state.
			if not newConnections:
				outStates.add(currentState)
			currentState.connections = newConnections

		return outStates


	def match(self, string):
		"""
		determines whether the regex matches the input string, and the amount 
			of characters it consumes 

		string: the string to match

		returns: 
			1. whether a match occured
			2. the number of characters consumed
		"""
		match, munch, currentStates = False, 0, [self.inState]

		# The process the string character-by-character.
		for i, char in enumerate(string):
			newStates = []

			for state in currentStates:
				for (value, connectedState) in state.connections:
					# If we find a connection whose value is the current 
					# character, we set the munch and add the connected state 
					# to the set of states to explore for the next character.
					if value == char:
						munch = i + 1
						newStates.append(connectedState)
					# If we find a connection whose value is epsilon, we add 
					# the connected state to the set of states to explore for 
					# this character.
					elif value == 'ε':
						currentStates.append(connectedState)
								
			currentStates = newStates

		# There is a match if, after stepping through all the characters in 
		# the regex, we end up at either the out-state or a state connected to 
		# the out-state by an epsilon connection.
		for state in currentStates:
			if state in self.outStates:
				match = True
				# One state being the out-state is enough.
				break
			for (value, connectedState) in state.connections:
				if value == 'ε':
					currentStates.append(connectedState)

		return match, munch


class State:
	"""
	a state of a nondeterministic finite automaton. Holds connections to other 
	states
	"""
	def __init__(self):
		"""
		initializes the state with an empty set of connections
		"""
		self.connections = set()

	def addConnection(self, value, state):
		"""
		adds a connection to another state.

		value: the input consumed by the connection
		state: the state the connection leads to

		returns: void
		"""
		self.connections.add((value, state))

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

		# We clear the visited list for future function calls.
		visited[:] = []

		return rep


# Tests
regex1 = Regex('ab|c*&d&')
regex2 = Regex('ad|c|')
tests = [regex1.match('acccd')[0]==True,
		regex1.match('bcccd')[0]==True,
		regex1.match('a')[0]==False,
		regex1.match('ad')[0]==True,
		regex1.match('ab')[0]==False,
		regex2.match('a')[0]==True,
		regex2.match('d')[0]==True,
		regex2.match('c')[0]==True,
		regex2.match('ad')[0]==False,
		regex2.match('dc')[0]==False]
if all(tests):
	print("Tests pass")
else:
	print("Tests fail")


