# Tokens for "qif> " prompt interpreter.

import sys
import ply.lex as lex

tokens = (

	#
	# Actions
	#

	'HELP',
	'QUIT',
	'ACCOUNT',
	'NUMBER',
)


t_HELP		= r'^\?'
t_QUIT		= r'^\.q'
t_ACCOUNT	= r'^[a-z].*$'
t_NUMBER	= r'^[0-9]+$'


def t_error(t):
	#
	# When I was debugging, I found it more convenient to send
	# errors to stdout, as the errors came out after the last
	# successful token parse.
	#
	#print >> sys.stderr, "Illegal character '%s'" % t.value[1]
	#print "Invalid input", t.value
	t.lexer.skip(len(t.value))

def lexer():
        return lex.lex()

