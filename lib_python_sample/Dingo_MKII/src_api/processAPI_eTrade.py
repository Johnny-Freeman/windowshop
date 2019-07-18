'''
	Further wrapper around eTrade wrapper to manage python multi-thread functions within a *singe bound* process
	
	Similar class is to be used in handling all API's
	Each processAPI_Provider.py must include import and export handlers:
		export:
			Packs global variables, credentials, instances into a self contained class
			Is able to then attach that to the process manager class
			SETS_outbound Pipe connection
			
		import:
			unpacks the above exported package
			mirrors instance within it's own process.
			SETS_inbound Pipe connection
	
	** in the spirit of MVPs, here we leave out this Real
'''
import time

from utils import marketTime as MarketTimeManager
from utils import list_management
from utils.framework import pythreadpool

import api_eTrade_wrapper_rev5 as eTrade_wrapper

# **Globals **************
from config import eTrade__SETTINGS

Debug = False
# **END Globals*************


# *****General Functions*****************************************************
def init(list_stocks, list_options, N_weeklyOptions):
	# Log into eTrade and start session within current process
	eTrade_wrapper.login()
	
	# Check Stock list
	list_good_stocks, list_bad_stocks = CHECK_StockList(list_stocks)
	if len(list_bad_stocks) > 0:
		print'Warning: Some eTrade_STOCKS failed to return good string data see eTrade_failed_Stocks.txt'
		_file = open('eTrade_failed_Stocks.txt', 'a+')
		_file.write(str(list_bad_stocks))
		_file.close()
	
	# Pre-load strike list for faster reference later AND check option chart integrity from eTrade
	list_good_options, list_bad_options = eTrade_wrapper.PREcompileStrikePriceStore(list_options,N_weeklyOptions)
	if len(list_bad_options) > 0:
		print'Warning: Some options failed to generate strike list see eTrade_failed_options.txt'
		_file = open('eTrade_failed_options.txt', 'w+')
		_file.write(str(list_bad_options))
		_file.close()
		
	print'eTrade Initiated'
	time.sleep(1)

# *****Thread General Functions*******************************************

# *****Thread Functions******************
def CHECK_StockList(symbols):
	'''
		A Thread based init() style function to check eTrade's tracker for these stock symbols
	'''
	good_stocks=[]
	bad_stocks=[]
	
	# I use this function since it is pretty robust, and returns error_found = True if there's an issue in the response
	for symbol in symbols:
		respString, error_found = GET_batchQuote([symbol])
		if error_found:
			bad_stocks.append(symbol)
		else:
			good_stocks.append(symbol)
	
	return good_stocks, bad_stocks
		
def GET_OptionNweekData(symbol, N):
	'''
		Get N-weeks of option order data
		For now lets just try to get the Data all in one go
			, in the future may need to think about dividing up the week grab
				1) Initiate store of week strike values desired
				2) Set some update priority thing or firing order
				3) Let it cycle through
		For now:
		1) Generate huge list of all option symbols for N weeks
		2) Feed into GET_batchOptionQuote, and return object
	'''
	# 1) Accounts for holidays too, by checking if error is generated during the expiration list compile!
	dmy_Fridaylist = eTrade_wrapper.StrikePriceStore.GRAB_dmy_nextNExpirations(N)
	strikechart = eTrade_wrapper.GET_Option_NweekStrikeList(symbol,N)
	
	list_req_string=[]
	# For each Friday i
	for i in range(0,N):
		
		# Calls first
		# [symbol, 2018, 01, 26, 'CALL']
		req_prepblock = [symbol,str(dmy_Fridaylist[i][2]),str(dmy_Fridaylist[i][1]), str(dmy_Fridaylist[i][0]), 'CALL']
		
		# For each strike j, SPEED!!!
		# https://waymoot.org/home/python_string/
		for j in range(len(strikechart[i])):
			req_block = req_prepblock + [strikechart[i][j]]

			# req_string = string.join(req_block,':')
			req_string = ':'.join(req_block)
			
			# Add to growing list
			list_req_string.extend([req_string])

		# Now puts
		req_prepblock = [symbol,str(dmy_Fridaylist[i][2]),str(dmy_Fridaylist[i][1]), str(dmy_Fridaylist[i][0]), 'PUT']
		
		# For each strike j, SPEED!!!
		for j in range(len(strikechart[i])):
			req_block = req_prepblock + [strikechart[i][j]]
			
			# req_string = string.join(req_block,':')
			req_string = ':'.join(req_block)
			
			# Add to growing list
			list_req_string.extend([req_string])
	
	# Note Returns a duple, the first is respString, the second is error_found=bool
	return GET_batchOptionQuote(list_req_string)

def GET_batchOptionQuote(symbols, detailFlag ='ALL', **kwargs):
	# Optionsquote = "FDX:2018:01:26:CALLPUT:267.500000"
	# Note Returns a duple, the first is respString, the second is error_found=bool
	return Get_batch(symbols, detailFlag)

def GET_batchQuote(ticks, detailFlag ='ALL', **kwargs):
	# Note Returns a duple, the first is respString, the second is error_found=bool
	return Get_batch(ticks, detailFlag)
	
def Get_batch(ticks, detailFlag):
	'''
		This one is a little bit more involved than IEX's batch api since they add a bracket after stating the detailFlag specific request
		Also they have different formats for single versus batch quotes unlike IEX with the same format regardless of number
			Addressed in Get_25batchObject() above.
		
		1) Make limited chunks >> generate list of chunks
			
		Multithreading method(rev5)
		2) parallel grab all chunk quotes into chart using framework_pyprocess (process manager)
		3) cycle through list_resp and concat list
	'''
	
	# Error checks:
	if not type(ticks) == type([]):
		raise ValueError('This is general function: <ticks> must be a list of symbols and/or tickers!')
		return False
	if detailFlag == None:
		raise ValueError('This is general function: <detailFlag> must be defined')
		return False

	'''
		copying IEX's method of chunking up request
	'''
	# First instance
	rear = ticks
	front = None
	list_chunk_args = []
	
	# 1) Generate list of Chunks to split into multiprocess
	#loop, when rear returns empty = whole batch has been processed
	while not(rear == []):
		# make =<25 list chunks, recursive
		front, rear = list_management.split_list_byInt(rear, eTrade__SETTINGS.CONFIG_API['num_BatchSymbols'])
	
		list_chunk_args.append([front,detailFlag])
	
	# 2) Parallel grab chunk quotes using framework_pyprocess, this would work just as well as to 
	list_respString = pythreadpool.Blocking_ThreadPool_wReturn(	target=eTrade_wrapper.Get_25batchString, 
																args_list=list_chunk_args, 
																que_delay= eTrade__SETTINGS.CONFIG_API['minDelay'], 
																timeout=eTrade__SETTINGS.CONFIG_API['request_timeout'])
	
	# 3) Cycle through and concat values
	# Note Returns a duple, the first is respString, the second is error_found=bool
	return eTrade_wrapper.VETCONCAT_eTrade_respStrings(list_respString)