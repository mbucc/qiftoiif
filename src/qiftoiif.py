#
# Read qif file passed as first argument.
# 
# Copyright (c) 2010 Mark Bucciarelli <mkbucc@gmail.com>
# 
# Permission to use, copy, modify, and distribute this software
# for any purpose with or without fee is hereby granted, provided
# that the above copyright notice and this permission notice
# appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
# FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
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
