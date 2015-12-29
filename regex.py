# Converts normal regexes to postfix notation.

# To create postfix regexes, we need a postfix concatenation operator. We 
# choose to use the comma, since it has no special regex meaning.
CONCAT_SYMBOL = ','


def regexInfixToPostfix(infixRegex):
	"""
	converts an infix regex to postfix notation

	infixRegex: a regex in infix notation

	returns: a regex in postfix notation
	"""
	# We use a variant of the shunting-yard algorithm, requiring an operator 
	# stack and an output queue. 
	postfixList, ops = [], []

	for i, char in enumerate(infixRegex):

		if char in ['|', CONCAT_SYMBOL]:
			# If the operator stack is not empty and we encounter a new binary 
			# operator, we push the existing binary operator into the queue 
			# first, unless the existing operator is a left-bracket, which we 
			# treat as the beginning of a new list.
			if ops and ops[-1] != '(':
				postfixList.append(ops.pop())
			ops.append(char)

		elif char == '(':
			ops.append(char)

		elif char == ')':
			try:
				# Upon encountering a right-bracket, we check if there is a 
				# binary operator on the top of the stack, and if so, we pop 
				# it onto the queue. We then pop the left-bracket.
				if ops[-1] != '(':
					postfixList.append(ops.pop())
				ops.pop()
			# If we hit the start of the operator stack without encountering a 
			# matching left-bracket, we raise an error.
			except IndexError:
				raise RuntimeError('Unmatched brackets')

		else:
			# This case handles both the unary operators and any literals, 
			# which can both be added directly to the queue.
			postfixList.append(char)

	# If there is an operator left on the stack, we pop it onto the queue.
	if ops:
		postfixList.append(ops.pop())

	postfixRegex = ''.join(postfixList)

	return postfixRegex


def regexAddConcatOps(noConcatRegex):
	"""
	adds explicit concatenation operators to a regex

	noConcatRegex: a regex without explicit concatenation operators

	returns: a regex with explicit concatenation operators
	"""
	withConcatList = []

	for i, char in enumerate(noConcatRegex):
		withConcatList.append(char)

		# We only add concatenation operators between certain combinations of 
		# characters.
		if (char not in ['(', '|'] and i + 1 < len(noConcatRegex) and 
		  noConcatRegex[i+1] not in ['*','+','?',')','|']):

			withConcatList.append(CONCAT_SYMBOL)

	withConcatRegex = ''.join(withConcatList)

	return withConcatRegex


# Tests
testRegexIn = "a?bc|(d|e+)f"
testRegexOut = "a?b,c,de+||f,"

if(regexInfixToPostfix(regexAddConcatOps(testRegexIn))==testRegexOut):
	print("Tests pass")
else:
	print("Tests fail")
