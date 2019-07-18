'''
	Further wrapper around AllyTK wrapper to manage thread and process bound functions
	
	** Due to the single process bound nature of this Module and Python
		, we implement a process manager class to handle the in/out - bound_pipes into this API process
		, the Global states included with logins
	
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

from utils import list_management
from utils.framework import pythreadpool

import api_AllyTK_wrapper_rev2 as AllyTK_wrapper

# **Globals **************
from config import AllyTK__SETTINGS

Debug = False
# **END Globals*************

def init(list_stocks, list_options, N_weeklyOptions):
	# Log into eTrade and start session within current process
	AllyTK_wrapper.init()
	
	# PreCheck all lists
	list_good_stocks, list_bad_stocks = AllyTK_wrapper.PRECHECK_StocksList(list_stocks)
	list_good_options, list_bad_options = AllyTK_wrapper.PRECHECK_OptionsList(list_options, N_weeklyOptions)
	
	if len(list_bad_stocks) > 0:
		print'Warning: Some AllyTK_STOCKS failed to return good string data see AllyTK_failed_Stocks.txt'
		_file = open('AllyTK_failed_Stocks.txt', 'a+')
		_file.write(str(list_bad_stocks))
		_file.close()
		
	if len(list_bad_options) > 0:
		print'Warning: Some AllyTK_OPTIONS failed to generate strike list see AllyTK_failed_Options.txt'
		_file = open('AllyTK_failed_Options.txt', 'a+')
		_file.write(str(list_bad_options))
		_file.close()
		
	print'AllyTK Initiated'
	time.sleep(1)
	
def GET_batch_1minCandle(symbols, **kwargs):
	'''
		Unfortunate, but AllyTK only allows for a single 1 min chart at a time
		Here we use Threading to grab them at relatively the same time
	'''
	list_args = []
	list_kwargs = []
	# compile kwargs list
	for ticker in symbols:
		list_args.append([ticker])
		list_kwargs.append(kwargs)
	
	# 2) Parallel grab quotes using framework_pyprocess, this would work just as well as to 
	list_respString = pythreadpool.Blocking_ThreadPool_wReturn(	target=AllyTK_wrapper.GET_1minCandle, 
																args_list=list_args,
																kwargs_list = list_kwargs,
																que_delay= AllyTK__SETTINGS.CONFIG_API['minDelay'], 
																timeout=AllyTK__SETTINGS.CONFIG_API['request_timeout'])
	
	# Note Returns a duple, the first is respString, the second is error_found=bool
	return list_respString, AllyTK_wrapper.VET_ERROR_multi_respStrings(list_respString)
	
def GET_batchOptionNweekData(symbols, N, **kwargs):
	'''
		copying IEX's method of chunking up request
	'''
	# First instance
	rear = symbols
	front = None
	list_chunk_args = []
	list_chunk_kwargs = []
	
	# 1) Generate list of Chunks to split into multiprocess
	#loop, when rear returns empty = whole batch has been processed
	while not(rear == []):
		# make =<26 list chunks, recursive
		front, rear = list_management.split_list_byInt(rear, AllyTK__SETTINGS.CONFIG_API['num_BatchSymbols'])
	
		list_chunk_args.append([front,N])
		list_chunk_kwargs.append(kwargs)
	
	# 2) Parallel grab chunk quotes using framework_pyprocess, this would work just as well as to 
	list_respString = pythreadpool.Blocking_ThreadPool_wReturn(	target=AllyTK_wrapper.GET_OptionNweekData, 
																args_list=list_chunk_args,
																kwargs_list = list_chunk_kwargs,
																que_delay= AllyTK__SETTINGS.CONFIG_API['minDelay'], 
																timeout=AllyTK__SETTINGS.CONFIG_API['request_timeout'])

	# Note Returns a duple, the first is respString, the second is error_found=bool
	return list_respString, AllyTK_wrapper.VET_ERROR_multi_respStrings(list_respString)
	
if Debug:
	list_symbols 	= ['AAPL','TSLA','AMZN','MSFT','GS','IBM']
	init(list_symbols,list_symbols,2)
	raw_input()
	print GET_batch_1minCandle(list_symbols)
	print GET_batchOptionNweekData(list_symbols,2)