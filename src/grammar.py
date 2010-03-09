# Define a limited but valid grammar for a QIF.

import ply.yacc as yacc

from tokens import tokens
import trace
import qif

g_qiflist = qif.list()
g_cqif = qif.checkingtransaction()

def d(s):
	if trace.grammar:
		print 'TRACE_GRAMMAR:', s

def p_qif(p):
	'qif	: checking_qif'	
	p[0] = g_qiflist
	d('p_qif')

def p_checking_qif(p):
	'checking_qif : CHECKING checking_records'
	p[0] = p[2]
	g_qiflist.type = 'CHECKING'
	d('p_checking_qif')

def p_checking_records(p):
	'''checking_records : checking_record
			| checking_records checking_record'''
	d('p_checking_records')
	
def p_checking_record(p):
	'checking_record : checking_attrs END_RECORD'
	global g_cqif
	g_qiflist.transactions.append(g_cqif)
	g_cqif = qif.checkingtransaction()
	d('p_checking_record')

def p_checking_attrs(p):
	'''checking_attrs : checking_attr
			| checking_attrs checking_attr'''
	if not p[0]:
		p[0] = []
	if len(p) == 2:
		p[0].append(p[1])
	else:
		p[0].append(p[2])
	d('p_checking_attrs')

def p_checking_attr(p):
	'''checking_attr : amount
			| cleared_status 
			| date
			| memo
			| payee
			| payee_address
			| category_or_transfer
			| check_number'''
	p[0] = p[1]
	d('p_checking_attr: %s' % p[1])

def p_amount(p):
	'amount : AMOUNT'
	s = '%s' % p[1]
	g_cqif.amount_in_pennies = int(s.replace('.', '').replace(',', ''))
	d('p_amount: %s' % p[1])

def p_date(p):
	'date : DATE'
	g_cqif.date = p[1]
	d('p_date: %s' % p[1])

def p_memo(p):
	'memo : MEMO'
	g_cqif.memo = p[1]
	d('p_memo: %s' % p[1])

def p_cleared_status(p):
	'cleared_status : CLEARED_STATUS'
	g_cqif.cleared_status  = p[1]
	d('p_cleared_status: %s' % p[1])

def p_payee(p):
	'payee : PAYEE'
	g_cqif.payee = p[1]
	d('p_payee: %s' % p[1])
	
def p_payee_address(p):
	'payee_address : PAYEE_ADDRESS'
	g_cqif.payee_address = p[1]
	d('p_payee_address: %s' % p[1])
	
def p_category_or_transfer(p):
	'category_or_transfer : CATEGORY_OR_TRANSFER'
	g_cqif.category_or_transfer = p[1]
	d('p_category_or_transfer: %s' % p[1])

def p_check_number(p):
	'check_number : CHECK_NUMBER'
	global g_cqif
	if p[1]:
		g_cqif.check_number = int(p[1])
	else:
		g_cqif.check_number = None
	d('p_check_number: %s' % p[1])

def p_error(p):
    print "Syntax error in input!"


def parser():
	return yacc.yacc(errorlog=yacc.NullLogger())
