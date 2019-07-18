import socket
import re

class StreamManager(object):
	"""
		Initiates and Holds stream with EchoServer
	"""
	list_connectionSockets = {}
	
	def __init__(self, config):
		self.config_server = config
		self.repattern_delimiter = re.compile(config['delimiter'])
	
	def CHECK_StreamRequest(self, method, streamTag):
		valid_method = False
		for meth in self.config_server['allowedMethods']:
			if meth == method:
				valid_method = True
		if valid_method == False:
			raise ValueError("Invalid request Method")
			
		valid_streamTag = False
		for tag in self.config_server['allowedStreams']:
			if tag == streamTag:
				valid_streamTag = True
		if valid_streamTag == False:
			raise ValueError("Invalid streamTag")
	
	def START_Stream(self, streamTag, method='GET', **kwargs):
		self.CHECK_StreamRequest(method, streamTag)
	
		c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# c_socket.setblocking(0)
		try:
			c_socket.connect(	(self.config_server['address'], self.config_server['port'])	)
			raw_input(1)
			message_request = method + " " + streamTag
			c_socket.send(message_request)
			print'Stream sucessfully started with server: ', streamTag
			
		except:
			print'Connection Rejected by Server'
			return
		
		self.list_connectionSockets[streamTag] = c_socket
		
	def READ_Stream(self, streamTag, **kwargs):
		"""
			Returns a LIST of Server Responses, empty if not a single response
		"""
		list_responses = []
		
		try:
			# Currently Set to Non-blocking
			message_incoming = ''
			while(True):
				# collecting data through persistent socket
				data_buffer = self.list_connectionSockets[streamTag].recv(self.config_server['buffer'])
				split_resp = re.split(self.repattern_delimiter, data_buffer)
					
				# First instance
				if not split_resp[0] == '':
					# Optimization - no need to create a new string if just appending empty string.
					message_incoming += split_resp[0]
				
				# for each additional index
				for i in range(1,len(split_resp)):
					chunk = split_resp[i]
					
					# message finished
					if not message_incoming =='':
						# only count non empty strings as finished data
						list_responses.append( message_incoming )			# <<<<<<<<<<<<<<<<<<<<< Final data message!
			
					# reset with new data
					message_incoming = chunk
			
		except:
			print'Stream seems to be offline, attempting to restart stream'
			self.START_Stream(streamTag, **kwargs)
			
		return list_responses