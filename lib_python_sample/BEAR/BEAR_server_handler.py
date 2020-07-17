# ===================================================================
# TITLE:	BEAR - Server Handler
# PURPOSE:	Checks server port for new messages, creates socket handler(object) based on HDLC-like protocol with tags
#			BEAR's primary purpose is to setup nonblocking sockets with poll(), along with checking that message was received at server's end.
# INPUT:	Checks server port for new connections/messages
# OUTPUT:	socket handler(object), reply to client message received and valid
# UPDATED:	2020-05-10, rev_3
# AUTHOR:	Johnson Chu
# CHANGE LOG:
#	2020-05-12		Started BEAR - Server Handler
#	2020-05-15		Changing timeout such that there are two timeouts - Changes to check_message_complete(),
#					1) client fails to send request in time
#					2) Server is Bogged down and will take time getting to connection (rare)
#	2020-05-24		Removed comments about delimiter
#					Moved checks and verification to poll_response
#					Removed kill comments
#					Fixed demo to continue working after crash
#	2020-07-16		Modified for Windowshop, removed non standard dependencies
# ===================================================================

# https://docs.python.org/2/howto/sockets.html
# https://pymotw.com/2/socket/nonblocking.html

# ===================================================================
# Imports
# ===================================================================
import socket, time, collections, hashlib, json

DEFAULT_CONFIG = {
	'address'			: 'localhost',
	'port'				: 8094,
	'buffer'			: 1023,	# Read length
	'max_connections'	: 300,	# Max Number of concurrent connections
	'server_timeout'	: 5,	# Max time server itself will hold a connection open for client to send request (down stream operations must also respond in this time! Otherwise server closes connection for other connections)
}
# https://docs.python.org/2/howto/sockets.html

class BEAR_Connection():
	def __init__(self, conn, addr, buffer, timeout=0, max_lag=None):
		self.connection = conn
		self.address = addr
		self.buffer = buffer
		
		# Connection Handle
		self.payload_byte_length = None	# used to track if header received and length of message (minus 16 byte header)
		self.md5_hash = None			# md5 to check final encoded message against
		
		self.flag_header = False		# tracks if header information avaiable
		self.flag_complete = False		# flag to indicate response is finished and should instead grab the finished response
		self.flag_valid = False			# by default request is invalid, use a checking method to validate
		self.flag_killed = False		# Unlike client, check fails for some reason.
		
		self.timeout = timeout
		self.time_timeout = time.time() + timeout
		
		# Server addons
		if max_lag == None:
			max_lag = timeout
		self.max_lag = max_lag			# max_lag indicates time after connection created to start terminating requests due to lag (raises error)
		self.time_lagging = time.time() + max_lag
		
		# Request Handle
		self.byte_request = b''
		self.string_request = None
		self.string_response = None
	
	#-------------------------------------------
	# Status Checks
	#-------------------------------------------	
	def kill(self):
		if not self.flag_killed:
			self.connection.close()
			self.flag_killed = True
			
	def isAlive(self):
		return not self.flag_killed
			
	def check_timeout(self):
		if self.isAlive() and self.timeout > 0 and time.time() > self.time_timeout:
			return True
		else:
			return False
			
	def check_server_lag(self):
		if self.isAlive() and self.max_lag > 0 and time.time() > self.time_lagging:
			return True
		else:
			# Once server has checked and passed lag, it means server has started processing request (no lag!)
			self.max_lag = -1
			return False
			
	#-------------------------------------------
	# Connection handler
	#-------------------------------------------
	def generate_byte_message(self, string_message):
		# Message format >> [4 bytes length] [4 bytes length parity] [8 bytes md5 hash] [message payload]
		encoded_payload = string_message.encode('utf-8')
		length = len(encoded_payload)
		lead = (length).to_bytes(4, byteorder='big')
		parity = (length).to_bytes(4, byteorder='little')
		md5_hash = hashlib.md5(encoded_payload).hexdigest()[:8].encode('utf-8')
		return  lead + parity + md5_hash + encoded_payload
	
	def send(self, string_send):
		# Sends reply and closes connection afterward
		# Oddly enough, socket's still check target machine for connection
		# This will error if not handled -> server side does NOT care if recepiant has received message or not
		self.string_response = string_send
		try:
			self.connection.send(self.generate_byte_message(string_send))
			return True
		except Exception as err:
			print("WARNING: send error, ", str(err))
			self.kill()
			return False
	
	def reply_payload(self, payload):
		_dict = {
			"status"	: True,
			"payload"	: str(payload),
		}
		return self.send(json.dumps(_dict))
		
	def reply_error(self, error_payload):
		_dict = {
			"status"	: False,
			"payload"	: error_payload,
		}
		return self.send(json.dumps(_dict))
	
	def check_header_length(self):
		# HARDCODED header protocol here
		if len(self.byte_request) > 16:
			return True
		else:
			return False
	
	def check_header(self):
		# Does two things in regards to request message
		# 	Check to see if enough bytes exsist in message so far to check the header metadata
		# 	Hardcoded HERE for 16 byte headers
		
		# Message format >> [4 bytes length] [4 bytes length parity] [8 bytes md5 hash] [message payload]
		decode_lead = int.from_bytes(self.byte_request[:4], 'big')
		decode_parity = int.from_bytes(self.byte_request[4:8], 'little')
		
		if not decode_lead == decode_parity:
			# bad header length specified
			self.flag_header	= False
			self.flag_valid		= False
			# self.kill() moved to calling poll
			return False
		
		else:
			# save message length
			self.payload_byte_length = decode_lead
			# set md5_hash
			self.md5_hash = self.byte_request[8:16].decode('utf-8')
			# set header flag
			self.flag_header	= True
			return True
	
	def check_message_length(self):
		# Assumes self.flag_header == True
		# now just checking for end of message HARDCODED +16 bytes in addition to length of 
		if len(self.byte_request) >= self.payload_byte_length + 16:
			return True
		else:
			return False
	
	def validate_request(self):
		# only needs to check to make sure message length is equal to statement
		# otherwise returns false and kills connection
		# http://atodorov.org/blog/2013/02/05/performance-test-md5-sha1-sha256-sha512/
		
		# Message format >> [4 bytes length] [4 bytes length parity] [8 bytes md5 hash] [message payload]
		# Checks:
		#	length parity	(self.check_header)
		#	message length	(self.check_header)
		#	md5 hash check	(HERE)
		
		encoded_payload = self.byte_request[16:]
		
		# Check length of message
		if not len(encoded_payload) == self.payload_byte_length:
			return False
		
		# Check md5_hash of message
		if not hashlib.md5(encoded_payload).hexdigest()[:8] == self.md5_hash:
			return False
		
		# Else all checks out
		self.flag_valid = True
		self.string_request = encoded_payload.decode('utf-8')
		return True
	
	def check_message_complete(self):
		# Checks if finished grabbing data from client (Exit condition from calling loop)
		# Not (finished, timedout, or dead)
		# Else check partial data for headers (indicating response length), and validation problems
		if not self.flag_header:
			# No header received yet
			# Enough information recorded for header?
			if self.check_header_length():
				# check current message for valid header information
				if self.check_header():
					# return False (at end of checks)
					pass
				else:
					# Header failed, server raise exception
					raise ValueError("Header incorrect")
					return True
			else:
				# message not long enough yet for header, continue
				pass
		else:
			# Header information is logged
			# Check obtained message current length
			if self.check_message_length():
				# Great! message is of proper legnth for validation
				if self.validate_request():
					# End of request
					self.flag_complete = True
					return True
					
				else:
					# Failed validation
					raise ValueError("Message not properly Formatted or message failed md5 validation, try again.")
			else:
				# Full message not received yet, continue
				pass
		
		# Message polling by default should continue (return False)
		return False
		
	def POLL_request(self):
		# Grab as much information in one go as possible
		while(1):
			# Check if communication has ended (in between each read to prevent buffer overflow issues):
			try:
				if not self.isAlive():
					return True
				
				# check if data avaiable and processed
				if self.flag_complete:
					return True
			
				# Check if server is falling behind on processing requests, if so raise error and drop request
				if self.check_server_lag():
					raise ValueError("Server busy, try again later.")
					return True
				
				# Check timeout
				if self.check_timeout():
					raise ValueError("Client failed to submit request in time")
					return True
				
				# check ongoing message for completion, and subsenquent validation
				if self.check_message_complete():
					return True
					
			except Exception as err:
				self.reply_error(str(err))
				print(err)	# debugging
				self.kill() # kill after msg error is sent
				return True
			
			# else grab as many bytes in one go as possible (while checking inbetween grabs)
			try:
				more_byte_data = self.connection.recv(self.buffer)
				if more_byte_data == b'':
					# break and return False (No additional data to add)
					break
				else:
					# Append[copy] data to self.byte_request
					self.byte_request += more_byte_data
			except:
				break
		return False
	
	def GET_request(self):
		if self.string_request == None:
			# return current byte message instead
			return self.byte_request
		# if decoded string available, return that
		return self.string_request

class BEAR_Server():
	def __init__(self, config = DEFAULT_CONFIG):
		self.address		= config["address"]
		self.port			= config["port"]
		self.buffer			= config["buffer"]
		self.num_sockets	= config["max_connections"]
		self.server_timeout	= config["server_timeout"]	# implementing message length communication method instead, this is backup
		
		# Deque lists to contain requests (calls are requested )
		# https://docs.python.org/2/library/collections.html#collections.deque
		self.list_connection_queue = collections.deque()
		
		# start nonblocking server
		self.s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s_socket.setblocking(0)
		self.s_socket.bind(	(self.address, self.port),	)
		self.s_socket.listen(self.num_sockets)
		
		print ('server is now listening...')
	
	#-------------------------------------------
	# Checks for new server connections
	#-------------------------------------------
	def CHECK_new_connections(self):
		# process to check for new incoming requests
		num_new_connections = 0
		while(1):
			try:
				# Grab all waiting connections
				conn, addr = self.s_socket.accept()
				cub = BEAR_Connection(conn, addr, self.buffer, self.server_timeout)
				self.list_connection_queue.append(cub)
				
				# success
				num_new_connections+=1
			except Exception as socket_err:
				# no more new connections
				return False
		if num_new_connections > 0:
			return True
		else:
			return False
	
	#-------------------------------------------
	# Main Polling and GET procedures
	#-------------------------------------------
	def POLL(self):
		# process to check for new incoming requests
		bool_new_connections = self.CHECK_new_connections()
		
		# Check if connections available for request processing
		if bool_new_connections or len(self.list_connection_queue) > 0:
			return True
		else:
			return False
		
	def GET_connection(self):
		if len(self.list_connection_queue) > 0:
			# Return BEAR server connection handle
			return self.list_connection_queue.popleft()
		else:
			return None
	
def main():
	serve = BEAR_Server()
	while(1):
		# print(serve.POLL())
		if serve.POLL():
			cub = serve.GET_connection()
			while(1):
				if cub.POLL_request():
					print(cub.GET_request())
				time.sleep(.5)
		time.sleep(.5)

def main2():
	# initiate
	import json # to decode and turn into object
	serve = BEAR_Server()
	
	while(1):
		# Check for connnection
		cub = None
		while(1):
			# print(serve.POLL())
			if serve.POLL():
				cub = serve.GET_connection()
				break
		
		# Use connection handler (pass to thread for processing without waiting)
		# Poll for request
		while(1):
			# if response received
			if cub.POLL_request():
				# show response and stats
				#print("Valid request received: ", cub.flag_valid)
				#print(cub.GET_request())
				if not cub.flag_valid:
					#skip if request not valid
					break
				
				request = cub.GET_request()
				print(request)
				
				# replay with a payload of some sort
				#print("server reply send success: ", cub.reply_payload("This is the server's reply"))
				cub.reply_payload(int(number) * int(number))
				#print()
				break
				
			# time.sleep(.5) # << remove for speed test and PROD
			
		# repeat for next message to show full working server

if __name__ == "__main__":
	main2()