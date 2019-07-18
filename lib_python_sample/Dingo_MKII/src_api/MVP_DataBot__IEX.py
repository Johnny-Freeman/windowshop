'''
	MVP version of IEX's API, acts as multi-State dummy Data generator
	This is an alternative to writing a real-time OS just for this limited simple task
	
	** Due to the single process bound nature of this Module and Python <this outlines a general process setup and interface>
		, we implement a process manager class to handle the in/out - bound_pipes into this API process
		, the Global states included with logins
'''
from threading import Thread
import time

import processAPI_IEX as API_IEX
from config import IEX__SETTINGS
from classes import API_dataCommunication

# Globals ********************************************
#_targetDataFunction = API_IEX.GET_batchQuote
#_targetDataFunction = GETLIST_OptionNweekData

_proc_delay = IEX__SETTINGS.CONFIG_API['processDelay']

_N_weeklyOptions = 0
_list_stocks = []
_list_options =[]
_mode = None

Debug = False

# *************************************************************
def init(mode='STOCKS', list_stocks=[], **kwargs):
	print'Starting IEX Symbol Check'
	
	global _list_stocks
	if not list_stocks==[]:
		_list_stocks = list_stocks
	
	global _mode
	_mode = mode

	API_IEX.init(_list_stocks)
			
	print'IEX BOT says Helloworld\n'
	
def Mode(mode):
	global _mode
	_mode = mode
	
def shutdown():
	print'IEX BOT says good-bye'
	
def RUN_StockDataFunction(PipeOUT):
	'''
		Run once a second for mode = STOCKS
	'''
	datagram = API_dataCommunication.Datagram()
	datagram.SET_DataRequested()
	
	# respString and error_found, can also be a List of respStrings and corresponding list of error_founds, when handling option objects
	respString, error_found = API_IEX.MultiThread_GET_batchQuoteChart(_list_stocks)
	
	datagram.SET_DataReceived(respString, error_found)
	datagram.mode = _mode
	datagram.source = 'IEX'
	datagram.tag = 'Stock_Chart_Minute_Average'
	PipeOUT.send(datagram)

def RUN_ThreadCycle_DataFunction(PipeOUT, time_cyclestart):
	'''
		<enter user defined cycle>
		mode controller, when time_cyclestart is passed in.
		Up to user to decide if it should even be sub_threaded
	'''
	if _mode == 'STOCKS':
		RUN_StockDataFunction(PipeOUT)
		
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
				Mode(message['payload'])
				
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
				print"IEX's DataBot process is now idle, ~ready for orders~"
		
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
	#	print'Warning: RUN_ThreadCycle_DataFunction collision in IEX MVP'
	#	pass
	
	shutdown()
	return True
	
# TESTING ************************************************************************
if Debug:
	from multiprocessing import Pipe, Process
	from utils.framework import epochtime
def test_stocks():
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
	
	'''
	# startup message
	kwargs={'mode':'STOCKS', 'list_symbols':['aapl','tsla']}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	'''
	
	# Initiate
	payload ={'mode':'STOCKS', 'list_stocks':list_symbols}	#'''kwargs'''
	message = {
		"command"	: 'INITIATE',
		"payload"	: payload,
	}
	PipeOUTBOUND.send(message)
	
	# Time seperations
	time.sleep(120)
	

		
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
	time2gatherData = 600 #seconds
	
	file = open('IEX_test.dat', 'a+')
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
		test_stocks()