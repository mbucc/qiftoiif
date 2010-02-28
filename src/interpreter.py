# Assign a vendor and account to each QIF transaction.

import sys

import ply.yacc as yacc
import ply.lex as lex

import coa
import vendors

#-----------------------------------------------------------------------------
#
#                               State
#
#-----------------------------------------------------------------------------

g_trx = None

def qiftransaction():
	global g_trx
	if g_trx == None:
		g_trx = QifTransaction()
	return g_trx

class QifTransaction:

	#
	# In next three, first character must not be [a-z].  See t_CHARS.
	#

	PICKING_VENDOR = '<picking_vendor>'
	PICKING_ACCOUNT = '<picking_account>'
	DONE = '<done>'
	def __init__(self):
		self.qiftrx = None
		self.vendor = ''
		self.vendor_prospects = [] 
		self.account = ''
		self.account_prospects = []
	def setqif(self, qiftrx):
		self.qiftrx = qiftrx
	def pending(self):
		return not self.account 
	def state(self):
		if not self.vendor:
			return QifTransaction.PICKING_VENDOR
		elif not self.account:
			return QifTransaction.PICKING_ACCOUNT
		else:
			return QifTransaction.DONE
	def prompt(self):
		'''Return text to use for interpreter prompt.'''
		a = []
		if self.qiftrx:
			a.append(str(self.qiftrx))
		if self.state() == QifTransaction.PICKING_VENDOR:
			if self.vendor_prospects:
				a.append('Vendor Prospects:' )
				i = 0
				for p in self.vendor_prospects:
					i += 1
					a.append("    %2d: %s" % (i, p))
				s = 'Pick number (or type in letters '
				s += 'for another list): '
				a.append(s)
			else:
				s = 'Type in some letters of the '
				s += 'vendor you want: '
				a.append(s)
		elif self.state() == QifTransaction.PICKING_ACCOUNT:
			if self.account_prospects:
				a.append('Account Prospects:' )
				i = 0
				for p in self.account_prospects:
					i += 1
					a.append("    %2d: %s" % (i, p))
				s = 'Pick number (or type in letters '
				s += 'for another list): '
				a.append(s)
			else:
				s = 'Type in some letters of the '
				s += 'account you want: '
				a.append(s)
		else: 
			a.append('qif> ')
		return '\n'.join(a)

#-----------------------------------------------------------------------------
#
#                                Tokens
#
#-----------------------------------------------------------------------------

#states = (
#    ('account', 'exclusive'),
#    ('vendor', 'exclusive'),
#    )
tokens = (
    #
    # Actions
    #

    'HELP',
    'QUIT',
    'ACCOUNT',
    'CHARS',
    'NUMBER',
    'PICKING_VENDOR',
    'PICKING_ACCOUNT',
    )
t_HELP			= r'\?'
t_QUIT			= r'\.q'
t_CHARS			= r'[a-z].*$'
t_ANY_NUMBER		= r'\d+'
t_PICKING_VENDOR	= QifTransaction.PICKING_VENDOR
t_PICKING_ACCOUNT	= QifTransaction.PICKING_ACCOUNT

def t_error(t):
	t.lexer.skip(len(t.value))

def printtokens(lexer):
	while 1:
		tok = lexer.token()
		if not tok:
			break
		# tok.type, tok.value, tok.line, tok.lexpos
		print tok.type

def lexer():
	'''
	Parses free text into a sequence of known tokens.

	The most basic unit test is that the lexer recognizes one token.
		>>> l = lexer()
		>>> s = QifTransaction.PICKING_VENDOR
		>>> l.input(s)
		>>> printtokens(l)
		PICKING_VENDOR

	It should also recognize two tokens.
		>>> s = QifTransaction.PICKING_VENDOR + '.q'
		>>> l.input(s)
		>>> printtokens(l)
		PICKING_VENDOR
		QUIT

	It should recognize the help token.
		>>> s = QifTransaction.PICKING_VENDOR + '?'
		>>> l.input(s)
		>>> printtokens(l)
		PICKING_VENDOR
		HELP
	'''

        return lex.lex()


#-----------------------------------------------------------------------------
#
#                               Grammar
#
#-----------------------------------------------------------------------------

def p_command(p):
	'''command : quit
		| vendor_help
		| account_help
		| entered_vendor_string
		| picked_a_vendor
		| entered_account_string
		| picked_an_account'''
	p[0] = p[1]

def p_entered_vendor_string(p):
	'entered_vendor_string : PICKING_VENDOR CHARS' 
	global g_trx
	g_trx.vendor_prospects = vendors.stovendors(str(p[2]))
	if len(g_trx.vendor_prospects) == 0:
		print "   *****  No vendor matches found!"

def p_picked_a_vendor(p):
	'picked_a_vendor : PICKING_VENDOR NUMBER'
	i = int(p[2])
	if i < len(g_trx.vendor_prospects):
		g_trx.vendor = g_trx.vendor_prospects[i]
	else:
		print "%d not in list" % i

def p_entered_account_string(p):
	'entered_account_string : PICKING_ACCOUNT CHARS' 
	global g_trx
	g_trx.account_prospects = coa.stoaccts(str(p[2]))
	if len(g_trx.account_prospects) == 0:
		print "   *****  No account matches found!"

def p_picked_an_account(p):
	'picked_an_account : PICKING_ACCOUNT NUMBER'
	i = int(p[2])
	if i < len(g_trx.account_prospects):
		g_trx.account = g_trx.account_prospects[i]
	else:
		print "%d not in list" % i

def p_account_help(p):
	'account_help : PICKING_ACCOUNT HELP'
	msg = '''
    Type a few letters of the account name and hit enter.

    Then enter then number of the account you would
    like to assign to this transaction.

Commands:
	?  - display this help message.
	.q - exit qif interpreter.
'''
	print msg

def p_vendor_help(p):
	'vendor_help : PICKING_VENDOR HELP'
	msg = '''
    Type a few letters of the vendor name and hit enter.

    Then enter then number of the vendor you would
    like to assign to this transaction.

Commands:
	?  - help
	.q - exit
'''
	print msg

def p_quit(p):
	'''quit : QUIT
		| PICKING_VENDOR QUIT
		| PICKING_ACCOUNT QUIT
	''' 
	raise EOFError

def p_error(p):
    print "Invalid input---type .h for help."

def parser():
	return yacc.yacc()
