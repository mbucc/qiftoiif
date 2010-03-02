'''This is the interpreter module.  It prompts for input and 
modifies the state of the current QIF transaction based on
what you enter.

The interpreter processes QIF data.

	>>> import qif
	>>> q = qif.checkingtransaction()
	>>> q.payee = 'My Test Payee'
	>>> q.amount_in_pennies = 2000
	>>> q.date = '2010-03-01'

First step is to look and see if this vendor is on file.  (We do it here
manually to over-ride the default data file used.)

	>>> fn = 'testvendor.iif'
	>>> fp = open(fn, 'w')
	>>> fp.write('VEND\\tA Vendor\\n')
	>>> fp.write('VEND\\tWalmart\\n')
	>>> fp.write('VEND\\tKmart\\n')
	>>> fp.close()
	>>> vendors.stovendors(q.payee, fn)
	Loaded 3 vendors.
	[]

Note that the vendor matching logic works with partial strings.

	>>> v = vendors.stovendors('Ven', fn)
	>>> [x.name for x in v]
	['A Vendor']

The QifTransaction does this vendor lookup whenever a qif is loaded.

	>>> qt = qiftransaction()
	>>> qt.state()
	'<picking_vendor>'
	>>> qt.setqif(q)
	>>> qt.vendor_prospects
	[]

If there is only one vendor match, we progress to next state.

	>>> q.payee = 'A Vendor'
	>>> qt.setqif(q)
	>>> qt.vendor.name
	'A Vendor'
	>>> qt.state()
	'<picking_account>'

If there are multiple matches, we load them as prospects.

	>>> q.payee = 'mart'
	>>> qt.setqif(q)
	>>> v = qt.vendor_prospects
	>>> [x.name for x in v]
	['Walmart', 'Kmart']
	>>> qt.state()
	'<picking_vendor>'

We keep track of the last account that was associated with a vendor in a
tab-delimited file (with column headings). 

	>>> fn = './testva.csv'
	>>> fp = open(fn, 'w')
	>>> fp.write('vendor\\taccount\\n')
	>>> fp.write('Walmart\\tHousehold\\n')
	>>> fp.write('Dunkin Donuts\\tRestaurant\\n')
	>>> fp.close()
	>>> vendornametoaccount('Dunkin Donuts', fn)
	'Restaurant'

If we send a qif record that matches one vendor, and that vendor has an
account, we skip to the <pending_approval> state.

	>>> q.payee = 'Walmart'
	>>> qt.setqif(q)
	>>> qt.vendor.name
	'Walmart'
	>>> qt.account
	'Household'
	>>> qt.state()
	'<pending_approval>'

'''

#	>>> p = parser()
#	>>> l = lexer()
#	>>> p.parse(qt.state() + s, lexer=l)

import sys

import ply.yacc as yacc
import ply.lex as lex

import coa
import vendors
from vendoraccount import vendornametoaccount

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
	PENDING_APPROVAL = '<pending_approval>'
	DONE = '<done>'
	def __init__(self):
		self.clear()
	def clear(self):
		self.qifdata = None
		self.vendor = ''
		self.vendor_prospects = [] 
		self.account = ''
		self.account_prospects = []
		self.approved = False
	def setqif(self, qifdata):
		self.clear()
		self.qifdata = qifdata
		self.vendor_prospects = vendors.stovendors(self.qifdata.payee)
		if len(self.vendor_prospects) == 1:
			self.vendor = self.vendor_prospects[0]
			self.vendor_prospects = []
			self.account = vendornametoaccount(self.vendor.name)
	def pending(self):
		return not self.account 
	def state(self):
		if not self.vendor:
			return QifTransaction.PICKING_VENDOR
		elif not self.account:
			return QifTransaction.PICKING_ACCOUNT
		elif not self.approved:
			return QifTransaction.PENDING_APPROVAL
		else:
			return QifTransaction.DONE
	def prompt(self):
		'''Return text to use for interpreter prompt.'''
		a = []
		if self.qifdata:
			a.append(str(self.qifdata))
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
