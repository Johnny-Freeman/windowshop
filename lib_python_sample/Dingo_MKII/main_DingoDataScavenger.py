'''
	Dingo Data Data Scavenger
	
	 - Coordinates a clock between each API process (1 minute sync cycle)
	 - Initiates processes, both for IntraDay Data and EOD
		+ Librarian process > writes data to file
		+ EchoServer process > streams incoming data to client (in the future will also employ database to lookup data)

	 - Poll's list of INBOUND Pipes for incoming Datagram from each API
	 
	 - Forwards copy of Datagram to Librarian OUTBOUND Pipe
	 - Forwards copy of Datagram to EchoServer OUTBOUND Pipe
	 
	 
	 http://fortune.com/2016/07/07/hedge-fund-jim-simons-hft/
	 there's another article from a friend of Simon that posts exactly what he does which is model the non equalibrium movements (stocastic processes) and trades on that
'''
from multiprocessing import Pipe, Process
import time

from src_api import MVP_DataBot__AllyTK as DataAPI_AllyTK
from src_api import MVP_DataBot__eTrade as DataAPI_eTrade
from src_api import MVP_DataBot__IEX as DataAPI_IEX
from src_librarian import Librarian_writetofile as Librarian
# from src_echoserver import EchoServer

from utils.list_management import split_list_byInt
from utils.framework import epochtime
from utils import marketTime # import marketdatetime

# ***Global Settings ******************
from config.Dingo__SETTINGS import CONFIG_INTRADAY
from config.Dingo__SETTINGS import CONFIG_EOD
from classes.global_variables import DingoSession

_global = DingoSession()
#class DingoSession():
#	dict_Pipes_INBOUND	= [AllyTK,eTrade,IEX]
#	dict_Pipes_COMMAND	= [AllyTK,eTrade,IEX]

#	dict_Pipes_RESPOND	= [Librarian, EchoServer]
#	dict_Pipes_FORWARD	= [Librarian, EchoServer]

#	list_Processes		= []

def init_process():
	'''
		Initiates Processes
		Sets up communication Pipes
	'''
	# initiate AllyTK process
	PipeINBOUND, PipeOUT = Pipe()
	PipeIN, PipeOUTBOUND = Pipe()
	p = Process(target= DataAPI_AllyTK.Slave_DataBotProcess, args=[PipeIN, PipeOUT])
	p.start()
	_global.list_Processes.append(p)
	_global.dict_Pipes_INBOUND['ALLYTK'] =PipeINBOUND
	_global.dict_Pipes_COMMAND['ALLYTK'] =PipeOUTBOUND
	
	# initiate eTrade Process
	PipeINBOUND, PipeOUT = Pipe()
	PipeIN, PipeOUTBOUND = Pipe()
	p = Process(target= DataAPI_eTrade.Slave_DataBotProcess, args=[PipeIN, PipeOUT])
	p.start()
	_global.list_Processes.append(p)
	_global.dict_Pipes_INBOUND['ETRADE'] =PipeINBOUND
	_global.dict_Pipes_COMMAND['ETRADE'] =PipeOUTBOUND
	
	# initiate IEX Process
	PipeINBOUND, PipeOUT = Pipe()
	PipeIN, PipeOUTBOUND = Pipe()
	p = Process(target= DataAPI_IEX.Slave_DataBotProcess, args=[PipeIN, PipeOUT])
	p.start()
	_global.list_Processes.append(p)
	_global.dict_Pipes_INBOUND['IEX'] =PipeINBOUND
	_global.dict_Pipes_COMMAND['IEX'] =PipeOUTBOUND
	
	# initiate Librarian Process
	PipeINBOUND, PipeOUT = Pipe()
	PipeIN, PipeOUTBOUND = Pipe()
	p = Process(target= Librarian.Slave_WriteProcess, args=[PipeIN, PipeOUT])
	p.start()
	_global.list_Processes.append(p)
	_global.dict_Pipes_RESPOND['LIBRARIAN'] =PipeINBOUND
	_global.dict_Pipes_FORWARD['LIBRARIAN'] =PipeOUTBOUND
	
	# initiate EchoServer Process
	# PipeINBOUND, PipeOUT = Pipe()
	# PipeIN, PipeOUTBOUND = Pipe()
	# p = Process(target= EchoServer.Slave_EchoServer, args=[PipeIN, PipeOUT])
	# p.start()
	# _global.list_Processes.append(p)
	# _global.dict_Pipes_RESPOND['ECHOSERVER'] =PipeINBOUND
	# _global.dict_Pipes_FORWARD['ECHOSERVER'] =PipeOUTBOUND
	
	print _global.list_Processes
	print'Processes and Pipes Initiated'
	
	
def shutdown():
	'''
		Only shuts down processes
	'''
	print'Sending SHUTDOWN command to child processes'
	
	# Shutdown message
	message = {
		"command"	: 'SHUTDOWN',
	}
	for key in _global.dict_Pipes_COMMAND:
		_global.dict_Pipes_COMMAND[key].send(message)
	for key in _global.dict_Pipes_FORWARD:
		_global.dict_Pipes_FORWARD[key].send(message)
	
	print'Giving processes 10 seconds to properly shutdown'
	time.sleep(10)
	
	for p in _global.list_Processes:
		p.terminate()
		p.join(0)

def SETUP_API_Intraday():
	print'Preparing Intraday Setup'
	#	dict_Pipes_INBOUND	= [AllyTK,eTrade,IEX]
	#	dict_Pipes_COMMAND	= [AllyTK,eTrade,IEX]
	starttime = time.time()
	
	# AllyTK
	kwargs={'mode':'BOTH', 'list_stocks':CONFIG_INTRADAY['StockCandles_of_interest'], 'list_options':CONFIG_INTRADAY['Options_of_interest'], 'N_weeklyOptions':2}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_COMMAND['ALLYTK'].send(message)
	
	# Wait for AllyTK response
	response = _global.dict_Pipes_INBOUND['ALLYTK'].recv()
	print response
	
	
	
	# eTrade
	kwargs={'mode':'STOCKS', 'list_stocks':CONFIG_INTRADAY['StockTicks_of_interest']}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_COMMAND['ETRADE'].send(message)
	
	# Wait for eTrade response
	response = _global.dict_Pipes_INBOUND['ETRADE'].recv()
	print response
	
	
	# IEX
	kwargs={'mode':'STOCKS', 'list_stocks':CONFIG_INTRADAY['StockAverages_of_interest']}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_COMMAND['IEX'].send(message)
	
	# Wait for IEX response
	response = _global.dict_Pipes_INBOUND['IEX'].recv()
	print response
	
	
	#	dict_Pipes_RESPOND	= [Librarian, EchoServer]
	#	dict_Pipes_FORWARD	= [Librarian, EchoServer]
	# Librarian(setting mode to write to file)
	kwargs={'mode':'INTRADAY',}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_FORWARD['LIBRARIAN'].send(message)
	
	# Wait for Librarian response
	response = _global.dict_Pipes_RESPOND['LIBRARIAN'].recv()
	print response
	
	# Takes about 300 seconds, give 10 minute warmup!
	print'\nTime(seconds) for Intraday Setup Initialization: ',time.time() - starttime

def SETUP_API_EOD():
	print'Preparing EOD Setup\n'
	#	dict_Pipes_INBOUND	= [AllyTK,eTrade,IEX]
	#	dict_Pipes_COMMAND	= [AllyTK,eTrade,IEX]
	starttime = time.time()
	
	
	print'AllyTK EOD init skipped due to size of list, will run iteratively'
	# AllyTK
	#	kwargs={'mode':'STOCKS', 'list_stocks':CONFIG_EOD['StockCandles_of_interest'], 'list_options':CONFIG_EOD['Options_of_interest'], 'N_weeklyOptions':2}
	#	message = {
	#		"command"	: 'INITIATE',
	#		"payload"	: kwargs,
	#	}
	#	_global.dict_Pipes_COMMAND['ALLYTK'].send(message)
	#	
	#	# Wait for AllyTK response
	#	response = _global.dict_Pipes_INBOUND['ALLYTK'].recv()
	#	print response
	
	
	
	# eTrade's OPTIONS mode contains checker
	kwargs={'mode':'OPTIONS', 'list_stocks':CONFIG_EOD['StockTicks_of_interest'], 'list_options':CONFIG_EOD['Options_of_interest'], 'N_weeklyOptions':2}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_COMMAND['ETRADE'].send(message)
	
	# Wait for eTrade response
	response = _global.dict_Pipes_INBOUND['ETRADE'].recv()
	print response
	
	
	# IEX
	kwargs={'mode':'STOCKS', 'list_stocks':CONFIG_EOD['StockAverages_of_interest']}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_COMMAND['IEX'].send(message)
	
	# Wait for IEX response
	response = _global.dict_Pipes_INBOUND['IEX'].recv()
	print response
	
	
	
	
	#	dict_Pipes_RESPOND	= [Librarian, EchoServer]
	#	dict_Pipes_FORWARD	= [Librarian, EchoServer]
	# Librarian(setting mode to write to file)
	kwargs={'mode':'EOD',}
	message = {
		"command"	: 'INITIATE',
		"payload"	: kwargs,
	}
	_global.dict_Pipes_FORWARD['LIBRARIAN'].send(message)
	
	# Wait for Librarian response
	response = _global.dict_Pipes_RESPOND['LIBRARIAN'].recv()
	print response
	
	# Takes about 21 minutes! > 5-7 minutes post market + 21, give it 36 minutes to Setup
	print'\nTime(seconds) for EOD Setup Initialization: ',time.time() - starttime

def Forward_Datagram():
	"""
		Poll for Data
		Forward Data to next pipes
	"""
	#	dict_Pipes_INBOUND	= [AllyTK,eTrade,IEX]
	
	#	dict_Pipes_RESPOND	= [Librarian, EchoServer]
	#	dict_Pipes_FORWARD	= [Librarian, EchoServer]
	
	for key in _global.dict_Pipes_INBOUND:
		
		# If new datagram in pipe
		if _global.dict_Pipes_INBOUND[key].poll():
			datagram = _global.dict_Pipes_INBOUND[key].recv()
			
			# Loop and forward datagram to all parties
			for key in _global.dict_Pipes_FORWARD:
				_global.dict_Pipes_FORWARD[key].send({'command':'DATAGRAM', 'payload':datagram,})
				
def Halt_API_block_120seconds():
	"""
		Halts API sources
		Clears any items in the pipes
		
		Blocks for 2 minutes to ensure Databot's have finished running grabbing data
	"""
	halt_message = {
		"command"	: 'HALT',
	}
	#	dict_Pipes_COMMAND	= [AllyTK,eTrade,IEX]
	for key in _global.dict_Pipes_COMMAND:
		_global.dict_Pipes_COMMAND[key].send(halt_message)
	
	# Cycle continuously to clear pipes for 1 minute
	endtime = time.time() + 120
	while(time.time() < endtime):
	
		for key in _global.dict_Pipes_INBOUND:
			# If new datagram in pipe
			if _global.dict_Pipes_INBOUND[key].poll():
				# Empty pipe
				_global.dict_Pipes_INBOUND[key].recv()
		
		time.sleep(CONFIG_INTRADAY['main_loop_delay'])

def LOOP_Intraday(time_marketEnd):
	"""
		Main Loop while the market is open
	"""
	
	# Start eTrade Data Collection
	#	dict_Pipes_COMMAND	= [AllyTK,eTrade,IEX]
	message = {
		"command"	: 'RUN_CONTINUOUS',
		"payload"	: [1,-1],
	}
	_global.dict_Pipes_COMMAND['ETRADE'].send(message)
	
	
	# Main program Clock signal
	# Run condition (1 minute sync)
	sync_msg = {
		"command"	: 'SYNC_CYCLE',
		}
	minute_nextclockcycle = epochtime.NEXT_epochMinute()
	while(True):

		now = time.time()
		if now > minute_nextclockcycle:
			# Mark *immediate start of next clock cycle
			minute_nextclockcycle = epochtime.NEXT_epochMinute()
		
			# Do stuff at time sync
			# eTrade is setup for continuous run per second, AllyTK and IEX require 1 minute sync
			_global.dict_Pipes_COMMAND['ALLYTK'].send(sync_msg)
			_global.dict_Pipes_COMMAND['IEX'].send(sync_msg)
	
		# Stuff to do outside time Sync **************
		# Manage and Forward Data as it comes in
		Forward_Datagram()
			
		
		# Check if time to Halt Processes
		if now > time_marketEnd:
			Halt_API_block_120seconds()
			break
		
		
		# Sleep sometime till next clock cycle
		time_till_next_cycle = minute_nextclockcycle - time.time()
		if time_till_next_cycle > 0.0:
			time.sleep(	min(CONFIG_INTRADAY['main_loop_delay'],time_till_next_cycle)	)
		else:
			"""Don't sleep"""

def RUN_End_of_Day():
	"""
		Grab Single large DataSet from each source
		* Assume SETUP_API_EOD() has been ran first > sets up where Librarian writes to, and preloads options lists and verifies symbol availability
	"""
	#	dict_Pipes_INBOUND	= [AllyTK,eTrade,IEX]
	#	dict_Pipes_COMMAND	= [AllyTK,eTrade,IEX]
	print 'Grabbing EOD data'
	
	runonce_msg = {
		"command"	: 'RUN_ONCE',
		"payload"	: 0,
	}
	
	
	
	# AllyTK
	list_stocks = CONFIG_EOD['StockCandles_of_interest']
	list_options = CONFIG_EOD['Options_of_interest']
	
	rear = list_stocks
	while(not rear ==[]):
		front, rear = split_list_byInt(rear,52)
		
		# Grab and Write AllyTK STOCKS
		kwargs={'mode':'STOCKS', 'list_stocks':front, 'list_options':front, 'N_weeklyOptions':2}
		message = {
			"command"	: 'MODE',
			"payload"	: kwargs,
		}
		_global.dict_Pipes_COMMAND['ALLYTK'].send(message)
		_global.dict_Pipes_COMMAND['ALLYTK'].send(runonce_msg)
		
		# Forward Datagram to Librarian
		datagram = _global.dict_Pipes_INBOUND['ALLYTK'].recv()
		_global.dict_Pipes_FORWARD['LIBRARIAN'].send({'command':'DATAGRAM', 'payload':datagram,})
		
		time.sleep(60)
	
	rear = list_options
	while(not rear ==[]):
		front, rear = split_list_byInt(rear,52)
			
		# AllyTK OPTIONS
		kwargs={'mode':'OPTIONS', 'list_stocks':front, 'list_options':front, 'N_weeklyOptions':2}
		message = {
			"command"	: 'MODE',
			"payload"	: kwargs,
		}
		_global.dict_Pipes_COMMAND['ALLYTK'].send(message)
		_global.dict_Pipes_COMMAND['ALLYTK'].send(runonce_msg)
		
		# Forward Datagram to Librarian
		datagram = _global.dict_Pipes_INBOUND['ALLYTK'].recv()
		_global.dict_Pipes_FORWARD['LIBRARIAN'].send({'command':'DATAGRAM', 'payload':datagram,})
		
		time.sleep(60)
	
	# eTrade STOCKS
	message = {
		"command"	: 'MODE',
		"payload"	: 'STOCKS',
	}
	_global.dict_Pipes_COMMAND['ETRADE'].send(message)
	_global.dict_Pipes_COMMAND['ETRADE'].send(runonce_msg)
	
	# Forward Datagram to Librarian
	datagram = _global.dict_Pipes_INBOUND['ETRADE'].recv()
	_global.dict_Pipes_FORWARD['LIBRARIAN'].send({'command':'DATAGRAM', 'payload':datagram,})
	
	# eTrade OPTIONS
	message = {
		"command"	: 'MODE',
		"payload"	: 'OPTIONS',
	}
	_global.dict_Pipes_COMMAND['ETRADE'].send(message)
	_global.dict_Pipes_COMMAND['ETRADE'].send(runonce_msg)
	
	# Forward Datagram to Librarian
	datagram = _global.dict_Pipes_INBOUND['ETRADE'].recv()
	_global.dict_Pipes_FORWARD['LIBRARIAN'].send({'command':'DATAGRAM', 'payload':datagram,})
	
	# IEX STOCKS
	message = {
		"command"	: 'MODE',
		"payload"	: 'STOCKS',
	}
	_global.dict_Pipes_COMMAND['IEX'].send(message)
	_global.dict_Pipes_COMMAND['IEX'].send(runonce_msg)
	
	# Forward Datagram to Librarian
	datagram = _global.dict_Pipes_INBOUND['IEX'].recv()
	_global.dict_Pipes_FORWARD['LIBRARIAN'].send({'command':'DATAGRAM', 'payload':datagram,})

def LIB_Zip_Transfer():
	"""
		Runs Librarian's zip and transfer function
	"""
	message = {
			"command"	: 'ZIP',
	}
	_global.dict_Pipes_FORWARD['LIBRARIAN'].send(message)
	# block until complete message returned
	_global.dict_Pipes_RESPOND['LIBRARIAN'].recv()
	
# ******************************************************************************
def main():
	"""
		Manages Time Progression through out the day
	"""
	init_process()
	
	# Waiting until T-25 for data processes to begin privilege initiation - hotfix to remedy's etrade's nasty token renewal, a lot of parallel data grabs, need a way to stop all the parallel grabs and have a single token grab.
	print'\nWaiting until T-25 for data processes to begin privilege initiation'
	marketTime.wait_MarketOpen(-25)
	
	SETUP_API_Intraday()
	# Reset heartbeat, 1 min
	time.sleep(60)
	
	marketTime.wait_MarketOpen(-5)
	# Start Collecting Data 5 minutes Prior to market open
	
	# Epoch time of market end.
	time_marketEnd = epochtime.to_LOCALepoch(marketTime.CONFIG_MARKETHOURS['MarketClose'])
	
	# Debug
	# time_marketEnd += time_marketEnd
	
	# Run intraday loop while market is open
	LOOP_Intraday(time_marketEnd)
	
	# Wait 7 minutes after market closes before running EOD process
	marketTime.wait_MarketClose(7)
		
	# SETUP_API_EOD() # >ok
	# RUN_End_of_Day() #
	
	# Ask Librarian to Zip and transfer files
	time.sleep(60)
	LIB_Zip_Transfer()
	
	shutdown()
	print'DingoClosed'

if __name__ == '__main__':
	main()