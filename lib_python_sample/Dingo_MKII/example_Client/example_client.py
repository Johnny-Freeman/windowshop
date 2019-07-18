"""
	Requires a few overlapping imports as server
	-Datagram class (to help facilitate data transportation through client program)
	-Server configuration and delimitation settings
"""
import time
import re

from utils.connection_manager import StreamManager
from config.EchoServer__SETTINGS import CONFIG_SERVER1 as CONFIG_SERVER
from classes import global_variables

_globals = global_variables.EchoClientSession()

def init():
	_globals.streamManager = StreamManager(CONFIG_SERVER)
	
	for tag in CONFIG_SERVER['allowedStreams']:
		_globals.streamManager.START_Stream(tag)
	

def DELIMIT_response(streamTag):
	"""TBD"""
	
# Main function to call in process
def SLAVE_clientProcess(PipeIN, PipeOUT, *args, **kwargs):
	"""
		1) Initiates a bunch of active streams with server
		2) polls through streams constantly for data
		3) when data received make a datagram and send datagram up chain through pipe (for future multiprocessing parse and usage)
	"""
	init()
	
	while(True):
	
		for tag in CONFIG_SERVER['allowedStreams']:
			list_responses = _globals.streamManager.READ_Stream(tag)
			
			if len(list_responses) > 0:
				print len(list_responses)
	
		time.sleep(0.01)
		
SLAVE_clientProcess('pie','pie')