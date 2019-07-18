'''
	IEX is primarily Stock only data
		Wrapper returns raw-data object
'''

# API for IEX's data
import re

from utils import list_management
import api_IEX_rev4 as IEX
from classes import API_Thresholds

# *******START****IEX settings*************
from config import IEX__SETTINGS
ratelimits = API_Thresholds.RateLimits('IEX', IEX__SETTINGS.CONFIG_API)

Debug = False

# ************START Single Call Functions*****************
def GET_singleQuote(tick, *args, **kwargs):
	ratelimits.accessPublic()
	return IEX.GET_singleQuote(tick, requestRawData=True, *args, **kwargs)

def GET_singleChart(tick, *args, **kwargs):
	ratelimits.accessPublic()
	return IEX.GET_singleChart(tick, requestRawData=True, *args, **kwargs)

def GET_singleQuoteChart(tick, *args, **kwargs):
	ratelimits.accessPublic()
	return IEX.GET_singleQuoteChart(tick, requestRawData=True, *args, **kwargs)

# ****Data with Data Verification**********************************************************
def VET_ERROR_IEX_single_respString(respString):
	'''
		Similar to VET_IEX_batch_respString
	
		This function ONLY checks for format errors in the front and back of batch response strings
		front	= {"symbol"		9 characters at beginning,	re_pattern ='\{\s*"symbol"'
		rear	= }
	'''
	if not type(respString) == type('str'):
		print'Warning48: possible timeout by IEX'
		# Error found = True
		return True
	
	# buffer zone to search for key, about 50% more
	# Intra-Bracket locations [1,2,3 ,..... ,-3,-2,-1]
	loc_front = 15
	
	# Rare for these to change, unless IEX updates their API
	# Strings to test data quality, reject string if fails
	test_frontpattern = re.compile('\{\s*"symbol"')
	
	data_front = respString[:loc_front]
	
	if (	re.search(test_frontpattern, data_front)	==None):
		# Error found = True
		return True
	else:
		# no Error
		return False
	
# **********END Single Call Functions*********************


# **********START******Batch Functions******************
def GET_batchQuote(batch, types='quote'):
	return GET_batch(batch,types)

def GET_batchChart(batch, types='chart&range=1d', range=None):
	if not range == None:
		types = 'chart&range=' + range
	
	return GET_batch(batch,types)

def GET_batchQuoteChart(batch, types='quote,chart&range=1d', range=None):
	'''
		batch = ['1','2']
	'''
	if not range == None:
		types = 'chart&range=' + range
	
	return GET_batch(batch,types)

def GET_100batch(batch, *args, **kwargs):
	'''
		Returns raw string Response
		No Assumptions
	'''
	if len(batch) > IEX__SETTINGS.CONFIG_API['num_BatchSymbols']:
		raise ValueError('Length of batch exceeds IEX batch size limit')

	return IEX.GET_100batch(batch, requestRawData=True, *args, **kwargs)
	
# Return a compiled(simulated) of IEX's 100 request limit, will remove surrounding character's and concatontate the responses as if it was one huge request
def GET_batch(batch, types, *args, **kwargs):
	'''
		Makes NO assumption about data integrity
	'''
	# first instance
	resp_concat = "{}"	#/ the first '}' gets removed in loop
	rear = batch
	front = None
	seperator = ''		# (A) set in loop after used once, slightly faster than if.
	
	#loop, when rear returns empty = whole batch has been processed
	while not(rear == []):
		# 1) make =<100 list chunks
		front, rear = list_management.split_list_byInt(rear, IEX__SETTINGS.CONFIG_API['num_BatchSymbols'])
		
		# 2) retrieve 100batch chunk
		ticks = front
		ratelimits.accessPublic()
		resp_green = IEX.GET_100batch(ticks, types, requestRawData=True)
		
		# 3) concatonate
		resp_concat = resp_concat[:-1]	# removes previous '}'
		resp_green = resp_green[1:]		# removes leading '{'
		
		resp_concat += seperator + resp_green	# concats
		seperator = ','							#(A) set after being run once
	
	return resp_concat

# ****Data with Data Verification**********************************************************
def CHECK_IEX_symbolsList(list_symbols):
	'''
		Runs through symbols and parses/check for existence of each symbol within returned string
	'''
	respString, error_found = VET_GET_batchQuoteChart(list_symbols)
	
	# Parse the large response (only need to import when running this ONCE, otherwise there's no need parse later in the program such as when running nested thread calls or child processes)
	import json
	respDict = json.loads(	respString.encode('ascii', 'ignore')	)
	
	list_good_symbols = []
	list_bad_symbols = []
	for symbol in list_symbols:
		if symbol in respDict:
			list_good_symbols.append(symbol)
		else:
			list_bad_symbols.append(symbol)
			
	return list_good_symbols, list_bad_symbols

def VET_GET_batchQuote(batch, types='quote'):
	return VET_ERROR_GET_batch(batch,types)

def VET_GET_batchChart(batch, types='chart&range=1d', range=None):
	if not range == None:
		types = 'chart&range=' + range
	
	return VET_ERROR_GET_batch(batch,types)

def VET_GET_batchQuoteChart(batch, types='quote,chart&range=1d', range=None):
	'''
		batch = ['1','2']
	'''
	if not range == None:
		types = 'chart&range=' + range
	
	return VET_ERROR_GET_batch(batch,types)

def VET_ERROR_IEX_100batch_respString(respString):
	'''
		Verifies IEX data integrity, to an extent
			, if bad symbol or bad request, an empty bracket is returned
			, however if part of the request is bad, it will only return the portion that's correct and not generate obvious errors
			, this can only be found after parsing and searching the resulting dictionary for missing key (beyond the scope of this wrapper, will need to be handled by caller/program)
		
		This function ONLY checks for format errors in the front and back of batch response strings
		front	= {"			2 characters at beginning,	re_pattern ='\{"'
		rear	= }}}			3 characters at rear,		re_pattern ='\}\s*\}\s*\}'
	'''
	if not type(respString) == type('str'):
		print'Warning47: possible timeout by IEX'
		# Error found = True
		return True
	
	# buffer zone to search for key, about 50% more
	# Intra-Bracket locations [1,2,3 ,..... ,-3,-2,-1]
	loc_front = 5
	loc_rear = -5
	
	# Rare for these to change, unless IEX updates their API
	# Strings to test data quality, reject string if fails
	test_frontpattern = re.compile('\{"')
	test_rearpattern = re.compile('\}\s*\}')
	
	data_front = respString[:loc_front]
	data_rear = respString[loc_rear:]
	
	check_front = re.search(test_frontpattern, data_front)
	check_rear = re.search(test_rearpattern, data_rear)
	
	if (check_front==None) or (check_rear==None):
		# Error found = True
		return True
	else:
		# no Error
		return False
		
def VET_ERROR_GET_100batch(*args,**kwargs):
	ratelimits.accessPublic()
	respString = IEX.GET_100batch(*args,**kwargs)
	return respString, VET_ERROR_IEX_100batch_respString(respString)

def VET_ERROR_GET_batch(batch, types, *args, **kwargs):
	'''
		Runs serially to grab data
		returns error_found = True if error found during data grab
	'''
	# first instance
	resp_concat = "{}"	#/ the first '}' gets removed in loop
	rear = batch
	front = None
	seperator = ''		# (A) set in loop after used once, slightly faster than if.
	_error_found = False
	
	#loop, when rear returns empty = whole batch has been processed
	while not(rear == []):
		# 1) make =<100 list chunks
		front, rear = list_management.split_list_byInt(rear, IEX__SETTINGS.CONFIG_API['num_BatchSymbols'])
		
		# 2) retrieve 100batch chunk
		ticks = front
		resp_green, error_found = VET_ERROR_GET_100batch(ticks, types, requestRawData=True)
		if error_found:
			# Will not make error_found = False if it is already true
			_error_found = True
		
		# 3) concatonate
		resp_concat = resp_concat[:-1]	# removes previous '}'
		resp_green = resp_green[1:]		# removes leading '{'
		
		resp_concat += seperator + resp_green	# concats
		seperator = ','							#(A) set after being run once
	
	return resp_concat, _error_found

# **************END Batch Functions*********************

if Debug:
	#print type(GET_batchQuoteChart(['aapl','amzn']))
	#print GET_batchQuoteChart(['aapl','amzn'])
	file = open('IEX_test.dat','a+')
	file.write(GET_batchQuote(['aapl','amzn']) + '\n')
	file.write(GET_batchQuote(['aasadl', 'amzn']) + '\n')
	file.close()