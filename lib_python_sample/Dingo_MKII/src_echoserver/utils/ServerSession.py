import socket
import time

class EchoServerSession(object):
	def __init__(self, config):
		self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.s_socket.bind(	(config['address'], config['port'])	)
		self.s_socket.listen(config['num_sockets'])
		
		self.s_socket.setblocking(0)
		
		print 'server is now listening...'
		
	def UPDATE_Log(self, list_addr):
		file = open('EchoServer_Log.txt', 'a+')
		file.write(str(time.time()) + '\t' + str(list_addr) + '\n')
		file.close()
		
	def GRAB_Connections(self):
		"""
			Returns List of new connection attempts
		"""
		new_connections = []
		new_addresses = []
		# non blocking call
		while(True):
			try:
				conn, addr = self.s_socket.accept()
				new_connections.append(conn)
				new_addresses.append(addr)
				
				# UPDATE_Log(new_addresses)
			except:
				break

		return new_connections

	def CLOSE_session(self):
		self.s_socket.close()