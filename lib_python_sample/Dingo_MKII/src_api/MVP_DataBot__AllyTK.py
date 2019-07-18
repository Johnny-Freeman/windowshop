'''
	MVP version of AllyTK's API, acts as multi-State dummy Data generator
	This is an alternative to writing a real-time OS just for this limited simple task
'''
from threading import Thread
import time
# from random import uniform

import processAPI_AllyTK as API_AllyTK
from config import AllyTK__SETTINGS
from classes import API_dataCommunication

# Globals ********************************************
#_StockDataFunction = API_AllyTK.GET_batch_1minCandle
#_OptionDataFunction = API_AllyTK.GET_batchOptionNweekData

_proc_delay = AllyTK__SETTINGS.CONFIG_API['processDelay']

_N_weeklyOptions = 0
_list_stocks = []
_list_options =[]
_mode = None

Debug = False

# *************************************************************
def init(mode='BOTH', list_stocks=[], list_options=[], N_weeklyOptions=None, **kwargs):

	global _list_stocks
	global _list_options
	
	if not list_stocks ==[]:
		_list_stocks = list_stocks
	if not list_options ==[]:
		_list_options =list_options
	
	global _N_weeklyOptions
	if not N_weeklyOptions==None:
		_N_weeklyOptions = N_weeklyOptions
	
	global _mode
	_mode = mode
	
	API_AllyTK.init(_list_stocks, _list_options, _N_weeklyOptions)
		
	print'AllyTK BOT says Helloworld'
	print'AllyTK BOT _mode: ', _mode
	
def Mode(mode='BOTH', list_stocks=[], list_options=[], N_weeklyOptions=None, **kwargs):
	global _list_stocks
	global _list_options
	
	if not list_stocks ==[]:
		_list_stocks = list_stocks
	if not list_options ==[]:
		_list_options =list_options
	
	global _N_weeklyOptions
	if not N_weeklyOptions==None:
		_N_weeklyOptions = N_weeklyOptions
	
	global _mode
	_mode = mode
	
def shutdown():
	print'AllyTK BOT says good-bye'
	
def RUN_StockDataFunction(PipeOUT):
	datagram = API_dataCommunication.Datagram()
	datagram.SET_DataRequested()
	
	# respString and error_found, *can also be a LIST* of respStrings and corresponding list of error_founds, when handling option objects
	# I'm trusting these functions, the pythreadpool has a join(terminate) to each thread
	respString, error_found = API_AllyTK.GET_batch_1minCandle(_list_stocks)
	
	datagram.SET_DataReceived(respString, error_found)
	datagram.mode = _mode
	datagram.source = 'ALLYTK'
	datagram.tag = 'Stock_Chart_Minute_Candle'
	PipeOUT.send(datagram)

def RUN_OptionDataFunction(PipeOUT):
	datagram = API_dataCommunication.Datagram()
	datagram.SET_DataRequested()
		
	# respString and error_found, *can also be a LIST* of respStrings and corresponding list of error_founds, when handling option objects
	# I'm trusting these functions, the pythreadpool has a join(terminate) to each thread
	respString, error_found = API_AllyTK.GET_batchOptionNweekData(_list_options, _N_weeklyOptions)
	
	datagram.SET_DataReceived(respString, error_found)
	datagram.mode = _mode
	datagram.source = 'ALLYTK'
	datagram.tag = 'Option_Chart'
	PipeOUT.send(datagram)

def RUN_ThreadCycle_DataFunction(PipeOUT, time_cyclestart):
	'''
		Run every cycle, must have time check to segment each individual thread target call
		 * by far the most complicated version since we're collecting data across the entire minute, at irregular intervals
	'''	
	# Tracking the time to wait for each data grab
	list_time_stock = AllyTK__SETTINGS.CONFIG_API['sync_stock_1minChart']
	list_time_option = AllyTK__SETTINGS.CONFIG_API['sync_option_tables']
	len_stock = len(list_time_stock)
	len_option = len(list_time_option)
	interval_timeNoise = AllyTK__SETTINGS.CONFIG_API['sync_noiseRequest']
	
	# Track location in list of times
	idx_time_stock = 0
	idx_time_option = 0
	
	# Generating random wait for stocks and options
	# List of times to grab corresponding data
	#	for i in range(len_stock):
	#		list_time_stock[i] = list_time_stock[i] + round(	uniform(interval_timeNoise[0],interval_timeNoise[1])	,2)
		
	#	for i in range(len_option):
	#		list_time_option[i] = list_time_option[i] + round(	uniform(interval_timeNoise[0],interval_timeNoise[1])	,2)
	
	''' Eric says bad programming practice
	# Internal MODE functions:
	def modeFunction_Stocks():
		# check time
		if dtime_cycle > list_time_stock[idx_time_stock]:
		
			# Check finished
			if idx_time_stock >=len_stock:
				# Finished all stock symbols
				# break
				return True
			else: # more to do
				_t = Thread(target=RUN_StockDataFunction, args=[PipeOUT])
				_t.start()
				idx_time_stock +=1
				return False
	
	def modeFunction_Options():
		# check time
		if dtime_cycle > list_time_stock[idx_time_option]:
		
			# Check finished
			if idx_time_option >=len_option:
				# Finished all option symbols
				# break
				return True
				
			else: # more to do
				_t = Thread(target=RUN_OptionDataFunction, args=[PipeOUT])
				_t.start()
				idx_time_option +=1
				return False
	'''
	
	# list_manageThreads = []
	while(True):
		# To keep track of time since the last cycle
		dtime_cycle = time.time() - time_cyclestart
		
		if _mode =='STOCKS':
			if idx_time_stock < len_stock:
				# check time, stocks
				if dtime_cycle > list_time_stock[idx_time_stock]:
					_t = Thread(target=RUN_StockDataFunction, args=[PipeOUT])
					_t.start()
					idx_time_stock +=1
					# list_manageThreads.append(_t)
			else:
				# Finished
				#for _thread in # list_manageThreads:
				#	_thread.join()
				break
		
		elif _mode =='OPTIONS':
			if idx_time_option < len_option:
				# check time, options
				if dtime_cycle > list_time_option[idx_time_option]:
					_t = Thread(target=RUN_OptionDataFunction, args=[PipeOUT])
					_t.start()
					idx_time_option +=1
					# list_manageThreads.append(_t)
			else:
				# Finished
				#for _thread in # list_manageThreads:
				#	_thread.join()	< parasidic! likely due to constant polling on the single process between this and the main thread join! <stack exchange>, you should only EVER join main thread
				break

		else: # Assume BOTH
			# Check if both done
			if (idx_time_stock >=len_stock) and (idx_time_option >=len_option):
				# Finished All
				#for _thread in # list_manageThreads:
				#	_thread.join()
				break
			else: # more to do
				
				# Stocks
				if idx_time_stock < len_stock:
					# check time, stocks
					if dtime_cycle > list_time_stock[idx_time_stock]:
						_t = Thread(target=RUN_StockDataFunction, args=[PipeOUT])
						_t.start()
						idx_time_stock +=1
						# list_manageThreads.append(_t)
					
				# Options
				if idx_time_option < len_option:
					# check time, options
					if dtime_cycle > list_time_option[idx_time_option]:
						_t2 = Thread(target=RUN_OptionDataFunction, args=[PipeOUT])
						_t2.start()
						idx_time_option +=1
						# list_manageThreads.append(_t2)
		
		time.sleep(_proc_delay)

# MAIN FUNCTION TO CALL**********************************
def Slave_DataBotProcess(PipeIN, PipeOUT, *args, **kwargs):
	'''
		This is the Function to call in it's own process
		Does only a few state things.
	'''	
	
	# Process sync variables
	time_cyclestart = 0
	_run = True
	_run_Num = 0			# Run N number of times
	
	_run_cycle_period = 0		# Time between each consecutive cycle
	_run_cycle_timeout = 0		# Cycle Timeout, None = block and wait for thread to finish
	'''_run_cycle_timeout =
			none		> block until cycle finished
			positive	> maximum cycle time
			negative,0	> continue immediately onto the next cycle (This is used when threads need to be syncronized to clock)
	'''
	
	while(_run):
		if PipeIN.poll():
			message = PipeIN.recv()
			
			if message['command'] =='SHUTDOWN':
				_run = False
				break
				
			elif message['command'] =='INITIATE' or message['command'] =='SET':
				# Initiates variables but doesn't START!
				init(**message['payload'])
				response = {
					'command':'INITIATED'
				}
				PipeOUT.send(response)
				
			elif message['command'] =='CHANGE_MODE' or message['command'] =='MODE':
				# Changes mode without initiation, run with caution
				Mode(**message['payload'])
				
			elif message['command'] =='RUN_ONCE':
				_run_Num = 1
				try:
					if type(message['payload']) == type(1):
						_run_cycle_timeout = message['payload']
					elif type(message['payload']) == type([]):
						_run_cycle_timeout = message['payload'][2]
					else:
						_run_cycle_timeout = None
				except:
					_run_cycle_timeout = None
				
			elif message['command'] =='RUN_MULTIPLE':
				if not type(message['payload']) == type([]):
					if not len(message['payload'])==3:
						raise ValueError('For RUN_MULTIPLE, message["payload"] needs to be of type [<number of times to run>, <cycle period> ,<timeout_per_cycle for each cycle to finish>]')

				_run_Num			= message['payload'][0]
				_run_cycle_period	= message['payload'][1]
				_run_cycle_timeout	= message['payload'][2]

			elif message['command'] =='RUN_CONTINUOUS' or message['command'] =='RUN_CONTINUE':
				if not type(message['payload']) == type([]):
					if not len(message['payload'])==2:
						raise ValueError('For RUN_CONTINUOUS, message["payload"] needs to be of type [ <cycle period> ,<timeout_per_cycle for each cycle to finish>]')
				# This number for corresponds to a Century of 1 second cycles
				_run_Num			= 42000000000
				_run_cycle_period	= message['payload'][0]
				_run_cycle_timeout	= message['payload'][1]

			elif message['command'] =='SYNC_CYCLE' or message['command'] =='SYNC_START':
				'''
					I need an event to syncronize the start of a new minute between processes
						, random internet latency will cause the processes to d-sync
				'''
				_run_Num = 1
				_run_cycle_timeout = 0
				
			elif message['command'] =='STOP' or message['command'] =='HALT':
				'''
					When you have many cycles remaining and you want to stop the looping immediately
				'''
				_run_Num = -1
				print"AllyTK's DataBot process is now idle, ~ready for orders~"
		
		if _run_Num > 0:
			
			# Time between cycles:
			now = time.time()
			if (now - time_cyclestart > _run_cycle_period):
			
				# Do a new cycle
				# Cycle Start Time
				_run_Num -=1
				time_cyclestart=time.time()
			
				# The mode handles what the process does, not the main loop
				_t = Thread(target=RUN_ThreadCycle_DataFunction, args=[PipeOUT, time_cyclestart])
				_t.start()
			
			
				'''_run_cycle_timeout =
						none		> block until cycle finished
						positive	> maximum cycle time
						negative,0	> continue immediately onto the next cycle (This is used when threads need to be syncronized to clock <SYNC_CYCLE>)
				'''
				if (_run_cycle_timeout==None):
					# block until cycle finished
					_t.join()
					
				elif _run_cycle_timeout > 0:
					# maximum cycle time
					_t.join(_run_cycle_timeout)
					
				else: # (_run_cycle_timeout <= 0)
					''' Do nothing, continue
						This is used when threads need to be syncronized to clock'''
			
		else:
			# reset initial values
			_run_cycle_timeout=0
			_run_cycle_period = 0

		# Save CPU cycles for main thread processes
		if _run_cycle_period > 0.0:
			time_till_next_cycle = time_cyclestart + _run_cycle_period - time.time()
			if time_till_next_cycle > 0.0:
				time.sleep(	min(_proc_delay,time_till_next_cycle)	)
			else:
				"""Don't sleep"""
		else:
			time.sleep(_proc_delay)
	
	#try:
	#	time.sleep(10) # main program's heart beat + 9 (run one full cycle)
	#except:
	#	print'Warning: RUN_ThreadCycle_DataFunction collision in AllyTK MVP'
	#	pass
	
	shutdown()
	return True

# *************************************************************************
if Debug:
	from multiprocessing import Pipe, Process
	from utils.framework import epochtime
def test():
	PipeINBOUND, PipeOUT = Pipe()
	PipeIN, PipeOUTBOUND = Pipe()
	
	'''
		message = {
			"command"	:'',
			"payload"	:None,
		}
	'''
	
	_p = Process(target=Slave_DataBotProcess, args=[PipeIN, PipeOUT])
	_p.start()
	
	# list_symbols 	= ['AAPL','TSLA','AMZN','MSFT','GS','IBM']
	list_symbols 	= ['AAPL','FB','BABA','MSFT','NVDA','NFLX','JPM','WMT','AMZN','TSLA','IBM','BA','TWX','UPS','UNP','ABBV','CAT','DIS','EA','V','CVX','HD','JNJ','CELG','GS','JNUG','MCD','WYNN','BIDU','AGN','SWKS','LOW','CRM','GOOGL','UTX','FDX','WDC','GLD','ADBE','AMGN','MMM','AXP','HAS','MAR','AVGO','PEP','VLO','VMW','MA','KMB','STZ','COST']
	
	# startup message (init)
	kwargs={'mode':'BOTH', 'list_stocks':list_symbols, 'list_options':list_symbols, 'N_weeklyOptions':2}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	PipeOUTBOUND.send(message)
	
	print'Giving time for init, and rate limits to catch up'
	time.sleep(300)
	print'Running Test'
	
	# Run condition
	message = {
		# "command"	: 'RUN_CONTINUOUS',
		"command"	: 'SYNC_CYCLE',
		"payload"	: [5,60,20],
	}
	# PipeOUTBOUND.send(message)

	# Sync clock settings, Waits till next minute starts
	minute_nextclockcycle = epochtime.NEXT_epochMinute()
	mainProcess_delay = 0.05
	time_START_TEST = time.time()
	time2gatherData = 1200 #seconds
	
	file = open('AllyTK_test.dat', 'a+')
	while(True):

		if time.time() > minute_nextclockcycle:
			# Mark *immediate start of next clock cycle
			minute_nextclockcycle = epochtime.NEXT_epochMinute()
		
			# Do stuff at time sync
			PipeOUTBOUND.send(message)
						
	
		# Stuff to do outside time Sync **************
		if PipeINBOUND.poll():
				datagram = PipeINBOUND.recv()
				print datagram
				file.write( str(datagram.localtime_requested) + '\t' + str(datagram.localtime_received) + '\t' + str( time.time() ) + '\n')
		
		# Check if enough data gathered
		if time.time() - time_START_TEST > time2gatherData:
		
			# Halt process
			message = {
				"command"	: 'SHUTDOWN',
			}
			PipeOUTBOUND.send(message)
			time.sleep(20)
			break
		
		# Sleep sometime till next clock cycle
		time_till_next_cycle = minute_nextclockcycle - time.time()
		if time_till_next_cycle > 0.0:
			time.sleep(	min(mainProcess_delay,time_till_next_cycle)	)
		else:
			"""Don't sleep"""

	file.close()
	
if __name__ == '__main__':
	if Debug:
		test()