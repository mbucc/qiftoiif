# Read qif file passed as first argument.
#

import sys

import coa
import grammar
import interpreter
import tokens
import vendoraccount
import vendors
import iif

def printtokens(lexer):
	while 1:
		tok = lexer.token()
		if not tok:
			break
		print tok

def usage():
	usage = "usage: %s [-l] <qiffn> <iiffn> <acct>"
	print >> sys.stderr, usage % (sys.argv[0],)
	sys.exit(1)

def parseargs():
	qiffn = ''
	printtokens = False
	if len(sys.argv) == 4:
		qiffn = sys.argv[1]
		iiffn = sys.argv[2]
		acct = sys.argv[3]
	elif len(sys.argv) == 5:
		arg = sys.argv[1]
		if arg  == '-l':
			printtokens = True
		else:
			usage()
		qiffn = sys.argv[2]
		iiffn = sys.argv[3]
		acct = sys.argv[4]
	else:
		usage()
	return qiffn, printtokens, iiffn, acct

def runinterpreter(qiflist, iiffp, acct):

	#
	# The yacc.parse() function is bound to the last parser loaded.
	# Now that qif file is parsed, we load the grammar for the 
	# interpreter.
	#

	p = interpreter.parser()
	l = interpreter.lexer()
	cancel = False
	qt = interpreter.qiftransaction()
	iiffp.write(iif.header())
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
		iiffp.write(iif.qiftrxtoiif(qt, acct))
		iiffp.flush()

if __name__ == '__main__':

	qiffn, dumptokens, iiffn, acct = parseargs()

	#
	# Read in QIF data and input to lexer.
	#

	fp = open(qiffn, 'r')
	s = fp.read()
	fp.close()
	lexer = tokens.lexer()
	parser = grammar.parser()
	lexer.input(s)

	if dumptokens:
		printtokens(lexer)
	else:

		qiflist = parser.parse()

		#
		# Force data files to load.
		#

		bogus = 'zzz123abcxyz'
		coa.stoaccts(bogus)
		vendors.stovendors(bogus)
		vendoraccount.vendornametoaccount(bogus)

		fp = open(iiffn, 'w')
		runinterpreter(qiflist, fp, acct)
		fp.close()
