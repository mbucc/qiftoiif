# Define a limited but valid grammar for a QIF.
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
	'''qif	: checking_qif	
		| investment_qif'''
	p[0] = g_qiflist
	d('p_qif')

def p_checking_qif(p):
	'checking_qif : CHECKING checking_records'
	p[0] = p[2]
	g_qiflist.type = 'CHECKING'
	d('p_checking_qif')

def p_investment_qif(p):
	'investment_qif : INVESTMENT investment_records'
	p[0] = p[2]
	g_qiflist.type = 'INVESTMENT'
	d('p_investment_qif')

def p_checking_records(p):
	'''checking_records : checking_record
			| checking_records checking_record'''
	d('p_checking_records')
	
def p_investment_records(p):
	'''investment_records : investment_record
			| investment_records investment_record'''
	d('p_investment_records')
	
def p_checking_record(p):
	'checking_record : checking_attrs END_RECORD'
	global g_cqif
	g_qiflist.transactions.append(g_cqif)
	g_cqif = qif.checkingtransaction()
	d('p_checking_record')

def p_investment_record(p):
	'investment_record : investment_attrs END_RECORD'
	global g_cqif
	g_qiflist.transactions.append(g_cqif)
	g_cqif = qif.investmenttransaction()
	d('p_investment_record')

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

def p_investment_attrs(p):
	'''investment_attrs : investment_attr
			| investment_attrs investment_attr'''
	if not p[0]:
		p[0] = []
	if len(p) == 2:
		p[0].append(p[1])
	else:
		p[0].append(p[2])
	d('p_investment_attrs')

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

def p_investment_attr(p):
	'''investment_attr : amount
			| cleared_status 
			| date
			| memo
			| investment_action
			| security_name
			| security_price
			| share_quantity
			| commission_cost'''
	p[0] = p[1]
	d('p_investment_attr: %s' % p[1])

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

def p_investment_action(p):
	'investment_action : INVESTMENT_ACTION'
	g_cqif.investment_action = p[1]
	d('p_investment_action: %s' % p[1])

def p_security_name(p):
	'security_name : SECURITY_NAME'
	g_cqif.security_name = p[1]
	d('p_security_name: %s' % p[1])

def p_security_price(p):
	'security_price : SECURITY_PRICE'
	g_cqif.security_price = float(p[1].replace(',',''))
	d('p_security_price: %0.4f' % (g_cqif.security_price,))

def p_share_quantity(p):
	'share_quantity : SHARE_QUANTITY'
	g_cqif.share_quantity = float(p[1].replace(',',''))
	d('p_share_quantity: %.4f' % (g_cqif.share_quantity,))

def p_commission_cost(p):
	'commission_cost : COMMISSION_COST'
	g_cqif.commission_cost = float(p[1].replace(',',''))
	d('p_commission_cost: %.4f' % (g_cqif.commission_cost,))

def p_error(p):
    raise ValueError("Syntax error in input!")

def parser():
	return yacc.yacc(errorlog=yacc.NullLogger())
