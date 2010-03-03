# Read qif file passed as first argument.
#

import sys

import coa
import grammar
import interpreter
import tokens
import vendoraccount
import vendors
		

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
	qt = interpreter.qiftransaction()
	for t in qiflist.transactions:
		qt.setqif(t)
		while qt.pending() and not cancel:
			try:
				prompt = qt.prompt()
				s = raw_input(prompt)
				p.parse(qt.state() + s, lexer=l)
			except EOFError:
				cancel = True
		if cancel:
			break

if __name__ == '__main__':

	qiffn, dumptokens = parseargs()

	fp = open(qiffn, 'r')
	s = fp.read()
	fp.close()

	lexer = tokens.lexer()
	parser = grammar.parser()

	lexer.input(s)

	if dumptokens:
		printtokens(lexer)
	else:
		#
		# Force data file to load.
		#

		bogus = 'zzz123abcxyz'
		coa.stoaccts(bogus)
		vendors.stovendors(bogus)
		vendoraccount.vendornametoaccount(bogus)

		runinterpreter(parser)
