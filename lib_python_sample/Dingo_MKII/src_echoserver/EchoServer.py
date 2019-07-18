'''
	Primary Purpose is to echo and stream data back out
	Future versions may use database and return SQL through REST protocol
'''
import time, re

from config.EchoServer__SETTINGS import CONFIG_SERVER1 as CONFIG_SERVER
from utils import ConnectionManager
from utils import ServerSession
from classes import global_variables

# Globals *******************************************
Debug = False

_globals = global_variables.EchoServerSession()
"""
class EchoServerSession():
	server = None
	connection_streams = {}
"""	

# ***************************************************
def init():
	_globals.server = ServerSession.EchoServerSession(CONFIG_SERVER)
	
	# A random regular expression that needs to be compiled
	_globals.re_space = re.compile(r'\s*')
	
	print'EchoServer active'	
	
def FORWARD_Data(datagram):
	# Only attempt to forward stream if connection stream exists, saves clock cycles
	if datagram.tag in _globals.connection_streams:
		# Create a text_delimited version of datagram
		msg_datagram_delimited =	str(datagram.localtime_requested) + CONFIG_SERVER['text_delimiter'] + \
									str(datagram.localtime_received) + CONFIG_SERVER['text_delimiter'] + \
									str(datagram.error) + CONFIG_SERVER['text_delimiter'] + \
									datagram.rawData + CONFIG_SERVER['text_delimiter']
	
		_globals.connection_streams[datagram.tag].SEND_message(msg_datagram_delimited)

def ADD_Connection_to_Stream(conn, stream_tag):
	"""
		At this point the connection has already been validated
	
		After new connection is raised
		1) check if stream_tag is active
			if not, start a new stream pipe
			add connection to stream
		2) if connection stream already exist, just add connection to it
	"""
	if not (stream_tag in _globals.connection_streams):
		_globals.connection_streams[stream_tag] = ConnectionManager.StreamConnectionManager(CONFIG_SERVER['delimiter'])
	
	# Add new connection to connection stream
	_globals.connection_streams[stream_tag].ADD_connection(conn)

def CHECK_NewConnections():
	# Grab list of new connections
	new_connections = _globals.server.GRAB_Connections()
	
	# For each new connection, check stream request
	for conn in new_connections:
		request = ''
		
		# Socket timeout
		try:
			# conn.setblocking(CONFIG_SERVER['timeout_socket'])
			request = conn.recv(CONFIG_SERVER['buffer'])
		except:
			# Return immediately and do nothing if something funky happens during the addition of connection to stream
			return
		
		# Check validity of request
		"""
			Currently EchoServer is only coded for streamed information
			GET/POST streamTag
		"""
		# Only do something if request pair is length 2, and valid method:
		request_pair = re.split(_globals.re_space,request)
		if not len(request_pair) == 2:
			return
		
		valid_method = False
		for method in CONFIG_SERVER['allowedMethods']:
			if request_pair[0] == method:
				valid_method = True	
		if not valid_method:
			return
			
		
		# Handle request, also only adds connection to stream if proper stream request
		if request_pair[0] == 'GET':
			for stream_tag in CONFIG_SERVER['allowedStreams']:
				if request_pair[1] == stream_tag:
					ADD_Connection_to_Stream(conn, stream_tag)

# MAIN FUNCTION TO CALL**********************************
def Slave_EchoServer(PipeIN, PipeOUT, *args, **kwargs):
	'''
		This is the Function to call in it's own process
		Does only a few state things.
	'''
	# Initiate Echo Server
	init()
	
	_run = True
	
	while(_run):
		"""
		if PipeIN.poll():
			message = PipeIN.recv()
			
			if Debug:
				print'EchoServer msg received: ', message
		
			if message['command'] =='SHUTDOWN':
				_run = False
				break
		"""
		CHECK_NewConnections()

		time.sleep(0.01)
		
Slave_EchoServer('pie','pie')