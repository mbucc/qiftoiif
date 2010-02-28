# Assign a vendor and account to each QIF transaction.

import sys

import ply.yacc as yacc
import ply.lex as lex

import trace
import coa

#-----------------------------------------------------------------------------
#
#                               State
#
#-----------------------------------------------------------------------------

g_trx = None

class QifTransaction:
	qiftrx = None
	account = ''
	prospects = []
	def __init__(self, qiftrx):
		self.qiftrx = qiftrx
		self.account = ''
		self.prospect = ''
	def done(self):
		if not self.account:
			return 0
		else:
			return 1

def d(s):
	if trace.interpreter:
		print 'TRACE_INTERP:', s

#-----------------------------------------------------------------------------
#
#                                Tokens
#
#-----------------------------------------------------------------------------

states = (
    ('vendor', 'exclusive'),
    ('account', 'exclusive'),
    )
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


#-----------------------------------------------------------------------------
#
#                               Grammar
#
#-----------------------------------------------------------------------------

def p_command(p):
	'''command : help
		| quit
		| account
		| pick_a_number'''
	p[0] = p[1]
	d('p_command')

def p_pick_a_number(p):
	'pick_a_number : NUMBER'
	i = int(p[1])
	if i < len(g_trx.prospects):
		g_trx.account = g_trx.prospects[i]
	else:
		print "%d not in list" % i

def p_help(p):
	'help : HELP' 
	d('p_help')
	helpmsg = '''
    To assign an account type the first few letters of
    the account and hit enter.

    Then enter then number of the account you would
    like to assign to this transaction.

Commands:
	?  - display this help message.
	.q - exit qif interpreter.
'''
	print helpmsg

def p_quit(p):
	'quit : QUIT' 
	d('p_quit')
	raise EOFError

def p_account(p):
	'account : ACCOUNT' 
	d('p_account')
	global g_trx
	g_trx.prospects = coa.stoaccts(str(p[1]))

def p_error(p):
    print "Invalid input---type .h for help."

def parser():
	return yacc.yacc()

#-----------------------------------------------------------------------------
#
#                                API
#
#-----------------------------------------------------------------------------

def setqif(qiftrx):
	global g_trx
	g_trx = QifTransaction(qiftrx)

def qifprompt():
	'''Return a prompt for interpreter so user can pick account.'''
	global g_trx
	a = []
	if g_trx:
		if g_trx.qiftrx:
			a.append(str(g_trx.qiftrx))
		if hasprospect():
			a.append('Prospects:' )
			i = 0
			for p in g_trx.prospects:
				i += 1
				a.append("    %2d: %s" % (i, p))
	return '\n'.join(a)

def hasprospect():
	global g_trx
	s = None
	if g_trx:
		s = g_trx.prospects
	return s

def qifpending():
	'''A QIF is pending if we hasn't been assigned an account.'''
	global g_trx
	s = None
	if g_trx:
		s = g_trx.account
	return not s

def prospects():
	global g_trx
	a = []
	if g_trx:
		a = g_trx.prospects
	return a
