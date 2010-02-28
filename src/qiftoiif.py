# Read qif file passed as first argument.
#

import sys

import tokens
import grammar
import interpreter

def printtokens(lexer):
	while 1:
		tok = lexer.token()
		if not tok:
			break
		print tok

def usage():
	usage = "usage: %s [-l] <qiffn>"
	print >> sys.stderr, usage % (sys.argv[0],)
	sys.exit(1)

def parseargs():
	qiffn = ''
	printtokens = False
	if len(sys.argv) == 2:
		qiffn = sys.argv[1]
	elif len(sys.argv) == 3:
		arg = sys.argv[1]
		if arg  == '-l':
			printtokens = True
		else:
			usage()
		qiffn = sys.argv[2]
	else:
		usage()
	return qiffn, printtokens

def runinterpreter(parser):

	qiflist = parser.parse()

	#
	# The yacc.parse() function is bound to the last parser loaded.
	# Now that qif file is parsed, we load the grammar for the 
	# interpreter.
	#

	p = interpreter.parser()
	l = interpreter.lexer()
	cancel = False
	for t in qiflist.transactions:
		interpreter.setqif(t)
		prompt = 'qif> '
		while interpreter.qifpending() and not cancel:
			try:
				print interpreter.qifprompt()
				s = raw_input(prompt)
				p.parse(s, lexer=l)
				if interpreter.hasprospect():	
					prompt = 'Pick number (or type in '
					prompt += 'letters for another list): '
				else: 
					prompt = 'qif> '
			except EOFError:
				cancel = True
		if cancel:
			break
				

#	account = ''
#	for t in qiflist.transactions:
#		prospect = ''
#		while not account:
#			print "  ", t
#			if prospect:
#				print "  ", prospect
#			chars = raw_input('qif > ')
#			if len(chars) > 0:
#				prospect = 'Some account'
#			else:
#
#				#
#				# User hit return to accept suggestion.
#				# 
#
#				account = prospect
#		print "assigning", account, "to", t
#		account = ''

if __name__ == '__main__':

	qiffn, printtokens = parseargs()

	fp = open(qiffn, 'r')
	s = fp.read()
	fp.close()

	lexer = tokens.lexer()
	parser = grammar.parser()

	lexer.input(s)

	if printtokens:
		printtokens(lexer)
	else:
		runinterpreter(parser)
