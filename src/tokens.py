import sys
import ply.lex as lex

#
# QIF Tokens:
#
#	ref: http://en.wikipedia.org/wiki/Quicken_Interchange_Format
#	     read on Sun Jan 31 13:05:15 EST 2010
#

tokens = (

	#
	# Record types.  Currently, we only support checking.
	#

	'ASSET',
	'CASH',
	'CHECKING',
	'CREDIT_CARD',
	'END_RECORD',
	'INVESTMENT',
	'LIABILITY',
	'QUICKEN_ACCOUNT',
	'QUICKEN_CATEGORY_LIST',
	'QUICKEN_CLASS_LIST',
	'QUICKEN_MEMORIZED_TRANSACTION_LIST',

	#
	# Used in all record types
	#

	'AMOUNT',
	'CLEARED_STATUS',
	'DATE',
	'MEMO',

	#
	# Used in Banking and Investment
	#

	'PAYEE',
	'PAYEE_ADDRESS',

	#
	# Used in Banking and Splits
	#

	'CATEGORY_OR_TRANSFER',
	'CHECK_NUMBER',

	#
	# Used in Investment.
	#

	'COMMISSION_COST',
	'INVESTMENT_ACTION',
	'SECURITY_NAME',
	'SECURITY_PRICE',
	'SHARE_QUANTITY',

	#
	# Used in Splits
	#

	'SPLIT_CATEGORY',
	'SPLIT_MEMO',
	'SPLIT_PERCENT',

	#
	# Used in Investment or Splits
	#

	'SPLIT_OR_TRANSER_AMOUNT'
)


#
# Header tokens
#

t_CASH 		= r'^!Type:Cash\s*'
t_CHECKING	= r'^!Type:Bank\s*'
t_CREDIT_CARD	= r'^!Type:CCard\s*'
t_INVESTMENT	= r'^!Type:Invst\s*'
t_ASSET		= r'^!Type:Oth A\s*'
t_LIABILITY	= r'^!Type:Oth L\s*'

#
# Quicken-specific types--currently not supported by parser.
#

t_QUICKEN_ACCOUNT			= r'^!Account\s*'
t_QUICKEN_CATEGORY_LIST			= r'^!Type:Cat\s*'
t_QUICKEN_CLASS_LIST			= r'^!Type:Class\s*'
t_QUICKEN_MEMORIZED_TRANSACTION_LIST	= r'^!Type:Memorized\s*'

#
# Detail tokens
#

# Date. Leading zeroes on month and day can be skipped. Year can
# be either 4 digits or 2 digits or '6 (=2006). 
#
#		Used in all types.
#		D12/25/2006
#

def t_DATE(t):
	r'D[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}\s*'
	s = t.value
	s = s[1:]
	s = s.rstrip()
	month, day, year = s.split('/')
	t.value = '%s-%02d-%02d' % (year, int(month), int(day))
	return t

#
# Amount of the item. For payments, a leading minus sign is required.
# For deposits, either no sign or a leading plus sign is accepted.
# Do not include currency symbols ($, , , etc.). Comma separators
# between thousands are allowed. 
#
#		Used in all types.
#		T-1,234.50
#

def t_AMOUNT(t):
	r'T-?([0-9]{1,3},?)*([0-9]{1,3}).[0-9]{2}\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Memo -- any text you want to record about the item. 
#
#		Used in all types.
# 		Mgasoline for my car
#

def t_MEMO(t):
	r'M.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Cleared status. Values are blank (not cleared), "*" or "c" (cleared)
# and "X" or "R" (reconciled).
#
#		Used in all types.
#		CR
#

def t_CLEARED_STATUS(t):
	r'C.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Number of the check. Can also be "Deposit", "Transfer", "Print",
# "ATM", "EFT".        
#
#		Used in Banking, Splits
#		N1001
#

def t_CHECK_NUMBER(t):
	r'N[0-9]*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t


# Also, Investment Action (Buy, Sell, etc).
#
#		Used in Investment
#		NBuy
#

def t_INVESTMENT_ACTION(t):
	r'N(Buy|ReinvDiv|Div|Sell)\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Payee. Or a description for deposits, transfers, etc.         
#
#		Used in Banking, Investment
#		PStandard Oil, Inc.
#

def t_PAYEE(t):
	r'P.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Address of Payee. Up to 5 address lines are allowed. A 6th address
# line is a message that prints on the check. 1st line is normally
# the same as the Payee line -- the name of the Payee.      
#
#		Used in Banking, Splits
#		A101 Main St.
#

def t_PAYEE_ADDRESS(t):
	r'A.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Category or Transfer and (optionally) Class. The literal values
# are those defined in the Quicken Category list. SubCategories can
# be indicated by a colon (":") followed by the subcategory literal.
# If the Quicken file uses Classes, this can be indicated by a slash
# ("/") followed by the class literal. For Investments, MiscIncX or
# MiscExpX actions, Category/class or transfer/class.         
#
#		Used in Banking, Splits
#		LFuel:car
#

def t_CATEGORY_OR_TRANSFER(t):
	r'L.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Split category. Same format as L (Categorization) field.
#
#		Used in Splits
#		Sgas from Esso

def t_SPLIT_CATEGORY(t):
	r'S.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Split memo -- any text to go with this split item.    
#
#		Used in Splits
#		Ework trips
#

def t_SPLIT_MEMO(t):
	r'E.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Amount for this split of the item. Same format as T field.
#
#		Used in Splits
#		$1,000.50
#
# Also, amount transferred, if cash is moved between accounts.
#
#		Used in Investment
#		$25,000.00
#
#

def t_SPLIT_OR_TRANSER_AMOUNT(t):
	r'\$-?([0-9]{1,3},)*([0-9]{1,3}).[0-9]{2}\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Percent. Optional -- used if splits are done by percentage.
#
#		Used in Splits
#		%50
#

def t_SPLIT_PERCENT(t):
	r'%[0-9]\{1,}\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Security name. 	
#
#		Used in Investment
#	 	YIDS Federal Income

def t_SECURITY_NAME(t):
	r'Y.*\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Price.
#
#		Used in Investment
#		I5.125
#

def t_SECURITY_PRICE(t):
	r'I([0-9]{1,3},?)*([0-9]{1,3}).[0-9]{1,}\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Quantity of shares (or split ratio, if Action is StkSplit). 	
#
#		Used in Investment
#		Q4,896.201
#

def t_SHARE_QUANTITY(t):
	r'Q([0-9]{1,3},?)*([0-9]{1,3})*.[0-9]{1,}\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# Commission cost (generally found in stock trades)
#
#		Used in Investment
#		O14.95
#		O.95
#

def t_COMMISSION_COST(t):
	r'O([0-9]{1,3},?)*([0-9]{1,3})*.[0-9]{2}\s*'
	t.value = t.value[1:]
	t.value = t.value.rstrip()
	return t

#
# F, Flag this transaction as a reimbursable business expense.
# Banking         F???
#


t_END_RECORD		= r'\^\s*'


def t_error(t):
	#
	# When I was debugging, I found it more convenient to send
	# errors to stdout, as the errors came out after the last
	# successful token parse.
	#
	#print >> sys.stderr, "Illegal character '%s'" % t.value[1]
	print "Illegal character '%s'" % t.value[1]
	t.lexer.skip(1)


def lexer():
	return lex.lex(errorlog=lex.NullLogger())
