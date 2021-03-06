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

'''This is an interpreter module that prompts for input when it doesn't
know what to do with a QIF record.  You can vendors and accounts to
each transaction.

The transactions are parsed from a QIF export file and encoded as a
Python class in the qif module.

	>>> import qif
	>>> q = qif.checkingtransaction()
	>>> q.payee = 'My Test Payee'
	>>> q.amount_in_pennies = 2000
	>>> q.date = '2010-03-01'

The first thing the interpreter does is to see if this vendor (AKA
payee) is on file.  (Note that by do this manually we over-ride the
default data file used to store the vendors.)

	>>> fn = 'testvendor.iif'
	>>> fp = open(fn, 'w')
	>>> fp.write('VEND\\tA Vendor\\n')
	>>> fp.write('VEND\\tWalmart\\n')
	>>> fp.write('VEND\\tKmart\\n')
	>>> fp.close()
	>>> vendors.stovendors(q.payee, fn)
	Loaded 3 vendors from testvendor.iif
	[]

Note that the vendor matching logic works with partial strings.

	>>> v = vendors.stovendors('Ven', fn)
	>>> [x.name for x in v]
	['A Vendor']

The QifTransaction does this vendor lookup whenever a qif is loaded.
If the vendor on the transaction is not found, we are left in the state
named '<picking_vendor>'.

	>>> qt = qiftransaction()
	>>> qt.state()
	'<picking_vendor>'
	>>> qt.setqif(q)
	>>> qt.vendor_prospects
	[]

If we find a match, and there is only one match, the interpreter advances
to the next state, which is named '<picking_account>'.

	>>> q.payee = 'A Vendor'
	>>> qt.setqif(q)
	>>> qt.vendor.name
	'A Vendor'
	>>> qt.state()
	'<picking_account>'

If there are multiple vendor matches, we load them as prospects, and
state is '<picking_vendor>'.

	>>> q.payee = 'mart'
	>>> qt.setqif(q)
	>>> v = qt.vendor_prospects
	>>> [x.name for x in v]
	['Walmart', 'Kmart']
	>>> qt.state()
	'<picking_vendor>'

We keep track of the last account that was associated with a vendor in a
tab-delimited file (with column headings). 

	>>> g_vendoraccount = None
	>>> fn = './testva.csv'
	>>> fp = open(fn, 'w')
	>>> fp.write('vendor\\taccount\\n')
	>>> fp.write('Walmart\\tHousehold\\n')
	>>> fp.write('Dunkin Donuts\\tRestaurant\\n')
	>>> fp.close()
	>>> vendornametoaccount('Dunkin Donuts', fn)
	'Restaurant'

If we have a qif record that matches one vendor, and that vendor has an
default account on file, we skip ahead to the '<pending_approval>' state.

	>>> q.payee = 'Walmart'
	>>> qt.setqif(q)
	>>> qt.vendor.name
	'Walmart'
	>>> qt.account
	'Household'
	>>> qt.state()
	'<pending_approval>'

If we have a qif record that matches one vendor, but that vendor does
not have a default account on file, once we enter an account that
vendor/account combo is saved to disk.

	>>> q.payee = 'Kmart'
	>>> qt.setqif(q)
	>>> qt.vendor.name
	'Kmart'
	>>> qt.state()
	'<picking_account>'
	>>> qt.account = 'Kids:Games'
	>>> qt.state()
	'<pending_approval>'
	>>> qt.approve()
	>>> qt.state()
	'<done>'
	>>> va = vendoraccount()
	>>> va.get(qt.vendor.name)
	'Kids:Games'

Note that as a first defense against getting the state confused, the
class does not allow you to set the vendor directly---you must set it
via the setqif() method.

	>>> qt.vendor = 'abc'
	Traceback (most recent call last):
	    ...
	AttributeError: set vendor by calling setqif()

If you assign an account to a transaction that has already been approved,
it's state reverts to '<pending_approval>'.

	>>> qt.state()
	'<done>'
	>>> qt.account = 'Gifts'
	>>> qt.state()
	'<pending_approval>'

And finally, the vendor/account mapping only stores the latest pair.

	>>> qt.approve()
	>>> qt.state()
	'<done>'
	>>> va = vendoraccount()
	>>> va.get(qt.vendor.name)
	'Gifts'

'''

#	>>> p = parser()
#	>>> l = lexer()
#	>>> p.parse(qt.state() + s, lexer=l)

import sys

import ply.yacc as yacc
import ply.lex as lex

import coa
import vendors
from vendoraccount import \
	vendornametoaccount, \
	vendoraccount, \
	g_vendoraccount

#-----------------------------------------------------------------------------
#
#                               State
#
#-----------------------------------------------------------------------------

g_trx = None
g_indent = 4

def qiftransaction():
	global g_trx
	if g_trx == None:
		g_trx = QifTransaction()
	return g_trx

class QifTransaction:

	#
	# In the state variables, the first character must not be
	# [a-z]. Otherwise, the interpreter grammar will break as the
	# state string will match the t_CHARS token regex.
	#

	PICKING_VENDOR   = '<picking_vendor>'
	PICKING_ACCOUNT  = '<picking_account>'
	PENDING_APPROVAL = '<pending_approval>'
	DONE             = '<done>'
	def __init__(self):
		self.clear()
	def __setattr__(self, attr, val):
		'''Manually setting vendor will screw up state.  So don't
		allow this.'''
		if attr == 'vendor':
			raise AttributeError("set vendor by calling setqif()")
		elif attr == 'account':
			if self.state() == QifTransaction.DONE:
				self.approved = False
		self.__dict__[attr] = val
	def clear(self):
		self.qifdata = None
		self.__dict__['vendor'] = None
		self.account = ''
		self.vendor_prospects = [] 
		self.account_prospects = []
		self.approved = False
		self.lasterror = ''
	def setqif(self, qifdata):
		self.clear()
		self.qifdata = qifdata
		self.vendor_prospects = vendors.stovendors(self.qifdata.payee)
		if len(self.vendor_prospects) == 1:
			self.__dict__['vendor'] = self.vendor_prospects[0]
			self.vendor_prospects = []
			self.account = vendornametoaccount(self.vendor.name)
	def pickvendorprospect(self, i):
		if self.state() != QifTransaction.PICKING_VENDOR:
			msg = "can't set vendor in state %s" % (self.state(),)
			raise AttributeError(msg)
		i -= 1
		if i < len(self.vendor_prospects):
			self.__dict__['vendor'] = self.vendor_prospects[i]
			self.account = vendornametoaccount(self.vendor.name)
			self.approved = False
			self.qifdata.payee = self.vendor.name
		else:
			fmt = 'Choice %d is not in list, try again.'
			self.lasterror = fmt % (i + 1,)
	def pickaccountprospect(self, i):
		i -= 1
		if i < len(self.account_prospects):
			self.__dict__['account'] = self.account_prospects[i]
			self.approved = False
		else:
			fmt = 'Choice %d is not in list, try again.'
			self.lasterror = fmt % (i + 1,)
	def pending(self):
		return not self.approved
	def approve(self):
		self.approved = True
		va = vendoraccount()
		va.set(self.vendor.name, self.account)
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
		indent1 = ' ' * g_indent
		indent2 = ' ' * 2 * g_indent
		promptfmt = '%25s> '
		if self.qifdata:
			s = str(self.qifdata)
			if self.state() == QifTransaction.PENDING_APPROVAL:
				s = s + "    " + str(self.account)
			s = s[:78]	# trim to 78 chars wide
			a.append(s)
		if self.state() == QifTransaction.PICKING_VENDOR:
			if self.vendor_prospects:
				a.append(indent1 + 'Vendor Prospects:' )
				i = 0
				for p in self.vendor_prospects:
					i += 1
					a.append(indent2 + '%2d: %s' % (i, p))
				if self.lasterror:
					fmt = '\n' + indent1 + '**** %s\n'
					a.append(fmt % (self.lasterror,))
				a.append(promptfmt % ('number',))
			else:
				a.append(promptfmt % ('vendor',))
		elif self.state() == QifTransaction.PICKING_ACCOUNT:
			if self.account_prospects:
				a.append(indent1 + 'Account Prospects:' )
				i = 0
				for p in self.account_prospects:
					i += 1
					a.append(indent2 + '%2d: %s' % (i, p))
				if self.lasterror:
					fmt = '\n' + indent1 + '**** %s\n'
					a.append(fmt % (self.lasterror,))
				a.append(promptfmt % ('number',))
			else:
				a.append(promptfmt % ('account',))
		elif self.state() == QifTransaction.PENDING_APPROVAL:
			a.append(promptfmt % ('OK? (y/n)',))
		else: 
			a.append(promptfmt % ('qif',))
		self.lasterror = ''
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
    'CHARS',
    'NUMBER',
    'PICKING_VENDOR',
    'PICKING_ACCOUNT',
    'PENDING_APPROVAL',
    )
t_HELP			= r'\?'
t_QUIT			= r'\.q'
t_CHARS			= r'[a-z].*$'
t_ANY_NUMBER		= r'\d+'
t_PICKING_VENDOR	= QifTransaction.PICKING_VENDOR
t_PICKING_ACCOUNT	= QifTransaction.PICKING_ACCOUNT
t_PENDING_APPROVAL	= QifTransaction.PENDING_APPROVAL

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
        #return lex.lex(debug=1)


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
		| picked_an_account
		| answered_approval_question'''
	p[0] = p[1]

def p_entered_vendor_string(p):
	'entered_vendor_string : PICKING_VENDOR CHARS' 
	global g_trx
	g_trx.vendor_prospects = vendors.stovendors(str(p[2]))
	if len(g_trx.vendor_prospects) == 0:
		print "   *****  No vendor matches found."

def p_picked_a_vendor(p):
	'picked_a_vendor : PICKING_VENDOR NUMBER'
	g_trx.pickvendorprospect(int(p[2]))

def p_entered_account_string(p):
	'entered_account_string : PICKING_ACCOUNT CHARS' 
	global g_trx
	g_trx.account_prospects = coa.stoaccts(str(p[2]))
	if len(g_trx.account_prospects) == 0:
		print "   *****  No account matches found."

def p_picked_an_account(p):
	'picked_an_account : PICKING_ACCOUNT NUMBER'
	g_trx.pickaccountprospect(int(p[2]))

def p_answered_approval_question(p):
	'answered_approval_question : PENDING_APPROVAL CHARS'
	global g_trx
	s = p[2].lower()
	if s in ('y', 'yes', 'ye'):
		g_trx.approve()
	elif s in ('n', 'no'):
		g_trx.account = ''
	else:
		print "   *****  Please enter y[es] or n[o]"


def p_account_help(p):
	'account_help : PICKING_ACCOUNT HELP'
	msg = '''
    Type a few letters of the account name and hit enter.
'''
	print msg

def p_vendor_help(p):
	'vendor_help : PICKING_VENDOR HELP'
	msg = '''
    Type a few letters of the vendor name and hit enter.
'''
	print msg

def p_quit(p):
	'''quit : QUIT
		| PICKING_VENDOR QUIT
		| PICKING_ACCOUNT QUIT
		| PENDING_APPROVAL QUIT
	''' 
	raise EOFError

def p_error(p):
    print "Invalid input---type ? for help or .q to quit."

def parser():
	return yacc.yacc()
	#return yacc.yacc(debug=1)
