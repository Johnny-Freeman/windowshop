'''
	Further wrapper around IEX wrapper to manage python multi-thread functions within a *singe bound* process
	
	IEX Doesn't have nearly all that much useful data thus no real reason to multithread the data grab
		, I go ahead and define a thread based data grab from IEX here
		, also a transparent GET_Batch direct to IEX wrapper
'''
from threading import Thread
import time

from utils import list_management
import api_IEX_wrapper_rev4 as IEX_wrapper
from utils.framework import pythreadpool

# *******START****IEX settings*************
from config import IEX__SETTINGS

Debug = False

def init(list_stocks):
	# Check Stock list
	list_good_stocks, list_bad_stocks = IEX_wrapper.CHECK_IEX_symbolsList(list_stocks)
	if len(list_bad_stocks) > 0:
		print'Warning: Some IEX_STOCKS failed to return good string data see IEX_failed_Stocks.txt'
		_file = open('IEX_failed_Stocks.txt', 'a+')
		_file.write(str(list_bad_stocks))
		_file.close()
		
	print'IEX initiated'
	time.sleep(1)
	
# *****Transparent single Threaded access	*************************************
'''
	These return concated respStrings, and should only be used for small requests as concatenation of large strings is IO intensive
	
	Returns: duple(single_concat_respString, single_error_found summary)
'''
def SingleThread_GET_batchQuote(batch, types='quote'):
	return IEX_wrapper.VET_ERROR_GET_batch(batch,types)

def SingleThread_GET_batchChart(batch, types='chart&range=1d', range=None):
	if not range == None:
		types = 'chart&range=' + range
	
	return IEX_wrapper.VET_ERROR_GET_batch(batch,types)

def SingleThread_GET_batchQuoteChart(batch, types='quote,chart&range=1d', range=None):
	'''
		batch = ['1','2']
	'''
	if not range == None:
		types = 'chart&range=' + range
	
	return IEX_wrapper.VET_ERROR_GET_batch(batch,types)
	
# ***MultiThreaded Methods***************************************************************************
def MultiThread_GET_batchQuote(batch, types='quote'):
	# returns duple(list respStrings, list_error_found)
	return MultiThread_GET_batch_List(batch,types)

def MultiThread_GET_batchChart(batch, types='chart&range=1d', range=None):
	if not range == None:
		types = 'chart&range=' + range

	# returns duple(list respStrings, list_error_found)
	return MultiThread_GET_batch_List(batch,types)

def MultiThread_GET_batchQuoteChart(batch, types='quote,chart&range=1d', range=None):
	'''
		batch = ['1','2']
	'''
	if not range == None:
		types = 'chart&range=' + range

	# returns duple(list respStrings, list_error_found)
	return MultiThread_GET_batch_List(batch,types)
	
def MultiThread_GET_batch_List(batch, types, *args, **kwargs):
	'''
		Uses pythreadpool to grab all IEX data in one go
		Due to size of final string, we leave as individual response list rather than attempting to Concat such large strings
			, still checks string for preliminary errors
	'''
	# first instance
	rear = batch
	front = None
	list_chunk_args = []
	
	while not(rear == []):
		# make =<25 list chunks, recursive
		front, rear = list_management.split_list_byInt(rear, IEX__SETTINGS.CONFIG_API['num_BatchSymbols'])
	
		list_chunk_args.append([front,types])
	
	# 2) Parallel grab chunk quotes using framework_pyprocess, this would work just as well as to 
	list_respString = pythreadpool.Blocking_ThreadPool_wReturn(	target=IEX_wrapper.GET_100batch, 
																args_list=list_chunk_args, 
																que_delay= IEX__SETTINGS.CONFIG_API['minDelay'], 
																timeout=IEX__SETTINGS.CONFIG_API['request_timeout'])
	
	list_error_found = []
	for respString in list_respString:
		list_error_found.append(	IEX_wrapper.VET_ERROR_IEX_100batch_respString(respString)	)
	
	return list_respString, list_error_found

# **********************************************************************
if Debug:
	import gzip
	
	list_symbols 	= ['AAPL','FB','BABA','MSFT','NVDA','NFLX']
	# list_symbols 	= ['AAPL','FB','BABA','MSFT','NVDA','NFLX','JPM','WMT','AMZN','TSLA','IBM','BA','TWX','UPS','UNP','ABBV','CAT','DIS','EA','V','CVX','HD','JNJ','CELG','GS','JNUG','MCD','WYNN','BIDU','AGN','SWKS','LOW','CRM','GOOGL','UTX','FDX','WDC','GLD','ADBE','AMGN','MMM','AXP','HAS','MAR','AVGO','PEP','VLO','VMW','MA','KMB','STZ','COST']

	respString = MultiThread_GET_batchQuoteChart(list_symbols)

	starttime = time.time()
	file = open('IEX_process_test.dat','a+')
	file.write (	str(respString ) + '\n'	)
	file.close()
	print time.time()-starttime
	
	starttime = time.time()
	file = gzip.open("IEX_process_test.dat.gz", "a+", 5)
	file.write (	str(respString ) + '\n'	)
	file.close()
	print time.time()-starttime
	
	raw_input()