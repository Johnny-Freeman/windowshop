"""
	Classes to hold active stream connections per data set type
"""
class StreamConnectionManager(object):
	list_connections = []
	
	def __init__(self, delimiter, acceptance_message = None):
		self.delimiter = delimiter
		self.acceptance_message = acceptance_message
	
	def ADD_connection(self, conn):
		self.list_connections.append(conn)
		
		if type(self.acceptance_message) == type('str'):
			# Send a reply to connection saying connection established
			try:
				conn.send(self.acceptance_message)
				conn.send(self.delimiter)
			except:
				print'Connection rejected: ', conn
				self.list_connections.pop()
				pass
		
	def CLOSE_All_Connections(self):
		for conn in self.list_connections:
			try:
				conn.close()
				
			except:
				print"Issue with closing zombie connection: ",conn
				print"Removing reference anyway"
		
		# reset references
		self.list_connections = []
	
	def SEND_message(self, message):
		for i in range(len(self.list_connections)):
			try:
				self.list_connections[i].send(message)
				self.list_connections[i].send(self.delimiter)
				
			except:
				print'Connection lost for any number of reasons, connection removed from stream list: ', self.list_connections[i]
				self.list_connections.pop(i)