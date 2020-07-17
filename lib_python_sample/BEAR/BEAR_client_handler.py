# ===================================================================
# TITLE:	BEAR - Client handler
# PURPOSE:	Provides non-blocking socket handler(object) that tracks message status to server (spins off any number of possible connections)
#			BEAR's primary purpose is to setup nonblocking sockets with poll(), along with checking that message was received at server's end.
# INPUT:	Message to send
# OUTPUT:	non-blocking socket handler(object) 
# UPDATED:	2020-05-10, rev_3
# AUTHOR:	Johnson Chu
# CHANGE LOG:
#	2020-05-12		Started BEAR - Client handler
#	2020-05-24		Enabled connection initiation timeout using settimeout() >> connection_latency
#					Moved checks and verification to poll_response
#					Removed kill comments
#	2020-05-26		Added _export function for logging
#	2020-07-16		Modified for Windowshop, removed non standard dependencies
# ===================================================================

# https://docs.python.org/2/howto/sockets.html
# https://pymotw.com/2/socket/nonblocking.html

# ===================================================================
# Imports
# ===================================================================
import socket, time, hashlib

DEFAULT_CONFIG = {
	'address'			: 'localhost',
	'port'				: 8094,
	'buffer'			: 1023,	# Read length
	'max_connections'	: 64,
	'client_timeout'	: 6,	# Max time client itself will hold a connection open for server to respond (down stream operations must also respond in this time! Otherwise server closes connection for other connections)
	'connection_latency': 0.01, # Max expected latency to get connection reply from server (take ping * 2.7)
}

class BEAR_client_connection():
	# Connection trackers
	max_connections = 0
	active_connections = 0
	
	def __init__(self, conn, buffer, timeout=0):
		self.connection = conn
		self.buffer = buffer
		self.client_timeout = timeout	# unused for now, self.timeout is used for connection timeouts
		
		# Connection Handle
		self.payload_byte_length = None	# used to track if header received and length of message (minus 16 byte header)
		self.md5_hash = None			# md5 to check final encoded message against
		
		self.flag_header = False		# tracks if header information avaiable
		self.flag_complete = False		# flag to indicate response is finished and should instead grab the finished response
		self.flag_valid = False			# by default request is invalid, use a checking method to validate
		self.flag_killed = False
		
		self.__class__.active_connections +=1
		
		self.timeout = timeout
		self.time_timeout = time.time() + timeout
		
		# Request Handle
		self.byte_response = b''
		self.string_request = None
		self.string_response = None
	
	#-------------------------------------------
	# Status Checks
	#-------------------------------------------
	def check_active_conn_available():
		if __class__.active_connections < __class__.max_connections:
			return True
		else:
			return False
	
	def kill(self):
		if not self.flag_killed:
			self.connection.close()
			self.__class__.active_connections -= 1
			self.flag_killed = True
		return True
			
	def isAlive(self):
		return not self.flag_killed
			
	def check_timeout(self):
		if self.isAlive() and self.timeout > 0 and time.time() > self.time_timeout:
			return True
		else:
			return False
			
	def _export(self):
		_dict = {
			"max_connections"		: self.__class__.max_connections,
			"active_connections"	: self.__class__.active_connections,
			"payload_byte_length"	: self.payload_byte_length,
			"md5_hash"				: self.md5_hash,
			"flag_header"			: self.flag_header,
			"flag_complete"			: self.flag_complete,
			"flag_valid"			: self.flag_valid,
			"flag_killed"			: self.flag_killed,
			"timeout"				: self.timeout,
			"time_timeout"			: self.time_timeout,
			"byte_response"			: self.byte_response.decode('utf-8'),
			"string_request"		: self.string_request,
			"string_response"		: self.string_response,
		}
		return _dict
			
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
		self.string_request = string_send
		try:
			self.connection.send(self.generate_byte_message(string_send))
			return True
		except Exception as err:
			print("WARNING: send error, ", str(err))
			self.kill()
			return False
	
	def check_header_length(self):
		# HARDCODED header protocol here
		if len(self.byte_response) > 16:
			return True
		else:
			return False
	
	def check_header(self):
		# Does two things in regards to request message
		# 	Check to see if enough bytes exsist in message so far to check the header metadata
		# 	Hardcoded HERE for 16 byte headers
		
		# Message format >> [4 bytes length] [4 bytes length parity] [8 bytes md5 hash] [message payload]
		decode_lead = int.from_bytes(self.byte_response[:4], 'big')
		decode_parity = int.from_bytes(self.byte_response[4:8], 'little')
		
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
			self.md5_hash = self.byte_response[8:16].decode('utf-8')
			# set header flag
			self.flag_header	= True
			return True
	
	def check_message_length(self):
		# Assumes self.flag_header == True
		# now just checking for end of message HARDCODED +16 bytes in addition to length of 
		if len(self.byte_response) >= self.payload_byte_length + 16:
			return True
		else:
			return False
	
	def validate_response(self):
		# only needs to check to make sure message length is equal to statement
		# otherwise returns false and kills connection
		# http://atodorov.org/blog/2013/02/05/performance-test-md5-sha1-sha256-sha512/
		
		# Message format >> [4 bytes length] [4 bytes length parity] [8 bytes md5 hash] [message payload]
		# Checks:
		#	length parity	(self.check_header)
		#	message length	(self.check_header)
		#	md5 hash check	(HERE)
		
		encoded_payload = self.byte_response[16:]
		
		# Check length of message
		if not len(encoded_payload) == self.payload_byte_length:
			return False
		
		# Check md5_hash of message
		if not hashlib.md5(encoded_payload).hexdigest()[:8] == self.md5_hash:
			return False
		
		# Else all checks out
		self.flag_valid = True
		self.string_response = encoded_payload.decode('utf-8')
		return True
	
	def check_message_complete(self):
		# Checks if finished grabbing data from server
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
					# Header failed, terminate connection
					return True
			else:
				# message not long enough yet for header, continue
				pass
		else:
			# Header information is logged
			# Check obtained message current length
			if self.check_message_length():
				# Great! message is of proper legnth for validation
				if self.validate_response():
					# End of request
					self.flag_complete = True
					return True
				else:
					# Failed validation
					self.flag_valid = False
					return True
			else:
				# Full message not received yet, continue
				pass
		
		# Message polling by default should continue (return False)
		return False
		
	def POLL_response(self):
		# Grab as much information in one go as possible
		while(1):
			# Check if communication has ended (in between each read to prevent buffer overflow issues):
			if not self.isAlive():
				return True
			
			# check if data avaiable and processed
			if self.flag_complete:
				self.kill()
				return True
			
			# Check timeout
			if self.check_timeout():
				self.kill()
				return True
			
			# check ongoing message for completion, and subsenquent validation
			if self.check_message_complete():
				self.kill()
				return True
			
			# else grab as many bytes in one go as possible (while checking inbetween grabs)
			try:
				more_byte_data = self.connection.recv(self.buffer)
				if more_byte_data == b'':
					# break and return False (No additional data to add)
					break
				else:
					# Append[copy] data to self.byte_request
					self.byte_response += more_byte_data
			except Exception as err:
				# print(err)
				break
		return False
	
	def GET_response(self):
		if self.string_response == None:
			# return current byte message instead
			return self.byte_response
		# if decoded string available, return that
		return self.string_response
		
class BEAR_client():	
	def __init__(self, config = DEFAULT_CONFIG):
		self.address 		= config["address"]
		self.port 			= config["port"]
		self.buffer 		= config["buffer"]
		self.client_timeout	= config["client_timeout"]
		self.max_connections= config["max_connections"]
		self.connection_latency = config["connection_latency"]
		
		BEAR_client_connection.max_connections = self.max_connections
	
	def GET_active_connections(self):
		return BEAR_client_connection.active_connections
	
	def GET_client_connection(self):
		# try to make a connection and return BEAR_client_connection object
		c_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		c_socket.settimeout(self.connection_latency) # settimeout() causes a low level response issue, becoems unstable and sometimes hangs .1 seconds. Keep eye out for fix
		
		try:
			c_socket.connect( (self.address, self.port) )
			c_socket.setblocking(0) # sets timeout to zero, no need to wait anymore after
			return BEAR_client_connection(c_socket, self.buffer, self.client_timeout)
		
		# if server refuses for some reason
		except Exception as err:
			print("Initial connection timed out") #debug
			# return Nothing
			try:
				c_socket.close()
			except:
				return None
			return None
	
	def CHECK_connections_available():
		return BEAR_client_connection.check_active_conn_available()
	
	def GET_connection(self):
		# Connection granted on two checks:
		# 1) active connection allowed by local limit
		if not BEAR_client_connection.check_active_conn_available():
			return None
			
		# 2) client is able to attempt a connection
		return self.GET_client_connection()


def main1(loop_num = 32):
	client = BEAR_client()
	
	last_fail = time.time()
	for i in range(loop_num):
		cub = client.GET_connection()
		
		# check if connection made:
		#if cub == None:
		#	now = time.time()
		#	print("last fail: ", now - last_fail)
		#	last_fail = now
		#	continue
		
		if cub == None:
			continue
		
		cub.send("this is my payload " + str(i))
		
		while(1):
			# if response received
			if cub.POLL_response():
				# show response and stats
				#print("Valid response received: ", cub.flag_valid)
				#print(cub.GET_response())
				cub.GET_response()
				#print(BEAR_client_connection.active_connections)
				#print()
				
				break
			# time.sleep(.2)
		
		if i == loop_num-1:
			print(cub._export())
			print()

def main2():
	# test how long it takes to open up 32 connections
	handle = BEAR_client()
	timestart = time.time()
	
	cub_list = []
	for i in range(32):
		cub = handle.GET_connection()
		cub.send("this is my payload" + str(i))
		cub_list.append(cub)
	print("time taken: ", (time.time()-timestart))

if __name__ == "__main__":
	timestart = time.time()
	main1(2000)
	print("time taken: ", (time.time()-timestart))
	# On localhost - back and forth took 1/4 seconds for 100 requests, that's 400 requests a second, or 24000 requests a minute!
	# If we remove print statements, it jumps to 100K requests a minute, not bad (also restricted by print statements, but lets assume that's representive of APP)