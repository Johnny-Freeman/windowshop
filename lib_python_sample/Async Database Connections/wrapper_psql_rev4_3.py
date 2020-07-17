"""
Wrapper to psql in multi-threaded application

https://stackoverflow.com/questions/32182405/how-to-use-postgresql-in-multi-thread-python-program

How psycopg2 backend response state works:
	See accompanying draw chart (WIP)

	3 main types of responses:
		1) INSERT
			Cursor description = None
			Cursor status_message = INSERT 0 #rows
			Sets connection.poll() = True
		2) SELECT
			Cursor descriptions = Schema/structure of information
			Cursor status_message = SELECT #rows
			Sets connection.poll() = True
		3) ERROR (duplicate tables, bad keys, etc)
			Cursor descriptions = None
			Cursor status_message = None
			connection.poll() -> raises exception with error
		4) CONNECTING
			Cursor description -> raises exception with error
			Cursor status_message -> raises exception with error
			connection.poll() = 0 (state == psycopg2.extensions.POLL_OK)
			
	
	How to handle responses:
		Flag response is ready (even if conne.poll() > exception)
			Here I'm using a class function poll_state(self,) to return True/False to indicate response from query.
			Even if it fails. The response/failure is documented in GET_response()
			
		return a dict{
			success:
				True
					INSERT / SELECT succeded in committing
				False
					Error in committing or other exception raised
			content:
				[<blank>]
					INSERT statements
				[select response (rows), numbers, etc.]
					SELECT statements
				[Error string]
					Exception Raised
		}

	Rev 4 change log:
	Problem:
		Issue with Rev3
		fetchall() clears fetchall() cache, must be cached locally if running async_connection.get_db_response() multiple times and just grabbing the one response
		This^^ issue is rare but solution would actually make async faster and more organized, since less logic, and ONLY looks for update if query is submitted
		
	Solution: A-sync methods:
		Define:
			transaction_status = module level status tracking of query state (connection.poll() already tracks underlying module state)
			transaction_time_start = start time for any communication with server ()
			
		poll_state() -> define heavy lifting function
	
		1) Initiate connection first
			Connect() (cursor not defined yet, so can't call description)
				transaction_status = Open
				transaction_time_start = now()
				Check poll_state  == if poll_okay(TRUE)
					if exception, log as connection issue
					else continue
				transaction_status = Closed
				
		2) Running a query and committing
			i) Set transaction_status = OPEN
			ii) transaction_time_start = now()
			iii) submit query
		
		3) poll_response()
			i) check poll_state == if poll_okay(TRUE) (notice that poll_okay just means NO TRANSACTIONS)
				if poll okay -> check new transactions [skip to (ii)]
				if exception -> query exception issue [skip to (iii)]
				
			ii) Check new transactions (poll_okay = True)
					Check Cursor status_message
						INSERT/SELECT -> Cache response
						ERROR -> cache response, also set bookmark function to log later
					transaction_status = CLOSED
			
			iii) Exception handling
				ERROR (duplicate tables, bad keys, etc) -> Cache response
					
			iv) error logging
				Rev5, for next time
		
		4) wait()
			loop poll_state till
			or transaction_time_start + timeout
		
		5) GET_response()
			check poll <- first, duh, this cache's response
			check transaction status
				-> general wait statement
				-> return cached response
"""

import psycopg2
import time, select

DEFAULT_CONFIG = {
	"username"		:	"NANA",
	"password"		:	"NANA",
	"server_address":	"192.168.1.3", # over LAN
	"database"		:	"test_vault",
	"port"			:		5432,
	"connection_timeout":	1000,
	"server_tick"	:		0.01,
}
class PSQL_BLOCKING_Connection():
	# By default makes persistent PSQL connection and keeps open,
	# must call RESTART_connection, or DISCONNECT to break connection
	def __init__(self, config=DEFAULT_CONFIG):
		self.database	= config["database"]
		self.user		= config["username"]
		self.password	= config["password"]
		self.host		= config["server_address"]
		self.port		= config["port"]
		
		self.conn		= None # actual psql connection
		self.cursor		= None # grabs psql focus
		
		self.CONNECT()

	def CONNECT(self):
		self.conn = psycopg2.connect(
						database	= self.database	, \
						user		= self.user		, \
						password	= self.password	, \
						host		= self.host		, \
						port		= self.port		)
		self.cursor = self.conn.cursor()
	
	def CHANGE_database(self, DB):
		self.database = DB
		self.RESTART_connection()
	
	def CHANGE_user(self,username, password):	
		self.user		= username
		self.password	= password
		self.RESTART_connection()
	
	def DISCONNECT(self):
		# Shutdown connection
		if not (self.cursor == None):
			self.cursor.close()
			self.cursor = None
		if not (self.conn == None):
			self.conn.close()
			self.conn = None
	
	def RESTART_connection(self):
		self.DISCONNECT()
		self.CONNECT()

	def SEND_command(self, sql_command):
		# print sql_command
		self.cursor.execute(sql_command)
		
	def SET_command(self, sql_command):
		# print sql_command
		self.cursor.execute(sql_command)
		self.cursor.commit()
		
	def QUERY_DB(self, query):
		# print query
		self.cursor.execute(query)
		return self.cursor.fetchall() # fetches list (line delimited) responses, what happens if just one entry?

class _psql_response(dict):
	# to Hold response characteristics
	# https://stackoverflow.com/questions/1325673/how-to-add-property-to-a-class-dynamically
	__getattr__= dict.__getitem__
	__setattr__= dict.__setitem__
	__delattr__= dict.__delitem__
	#status = None
	#content = []
	
class PSQL_NON_BLOCK_Connection():	
	# By default makes persistent PSQL connection and keeps open,
	# must call RESTART_connection, or DISCONNECT to break connection
	# http://initd.org/psycopg/docs/advanced.html (see asynchronous support)
	# similar to Blocking except, runs in async mode, everything is auto commited
	
	# Low level objects
	conn			= None # actual psql connection
	cursor			= None # grabs psql focus
	
	# Tracking transactions
	transaction_status = "OPEN" # Closed when no on going transactions
	transaction_time_start = 0
	transaction_time_end = 1
	
	# Storing response for retrevial
	response_object	= _psql_response()	# Holds response if exception polled, maynot even be called later
	
	def __init__(self, config):
		self.database	= config["database"]
		self.user		= config["username"]
		self.password	= config["password"]
		self.host		= config["server_address"]
		self.port		= config["port"]
		self.timeout	= config["connection_timeout"]
		self.delay		= config["server_tick"]
		
		self.CONNECT()
	
	# ========================================================
	# Tracking transaction endpoints
	# ========================================================
	def SET_transaction_start(self):
		self.transaction_time_start = time.time()
		self.transaction_status = "OPEN"
		self.response_object.status = False
		self.response_object.content = ['Transaction in progress']
	
	def SET_transaction_end(self):
		self.transaction_time_end = time.time()
		self.transaction_status = "CLOSED"
		
	def GET_transaction_time(self):
		if self.transaction_status == "OPEN":
			return time.time() - self.transaction_time_start
		else:
			# self.transaction_status = "CLOSED"
			return self.transaction_time_end - self.transaction_time_start
	
	# ========================================================
	# Polling for responses
	# ========================================================
	def poll_state(self):
		state = self.conn.poll()
		# conn.poll() can raise exception if bad connection issues, to be handeled in calling function
		#	Error on calling query -> bad query or diplicate table, etc.
		#	Error on calling connect -> connection failed
		
		if state == psycopg2.extensions.POLL_OK:
			# At this point cursor is connected, and response obtained
			return True
		elif state == psycopg2.extensions.POLL_WRITE:
			select.select([], [self.conn.fileno()], [])
		elif state == psycopg2.extensions.POLL_READ:
			select.select([self.conn.fileno()], [], [])
		else:
			raise psycopg2.OperationalError("poll() returned %s" % state)
			
		# nothiing polled, no response yet
		return False
	
	def poll_response(self):
		# i) check poll_state == if poll_okay(TRUE) (notice that poll_okay just means NO TRANSACTIONS)
		# 		if poll okay -> check new transactions [skip to (ii)]
		# 		if exception -> query exception issue [skip to (iii)]
		try:
			status = self.poll_state()
		except Exception as err:
			# query exception issue, handled in 
			status = self.GET_response_error(err)
			pass
		
		if status:
			# poll finished, Log reply
			self.GET_response_reply()
		
		return status # True(all finished), or False(still waiting for response)
	
	def GET_response_reply(self):
		if self.transaction_status == "CLOSED":
			# Transaction has finished
			return
		str_response_type = str(self.cursor.statusmessage)[:6]
		if str_response_type == 'INSERT':
			self.response_object.status = True
			self.response_object.content = []
		elif str_response_type == 'SELECT':
			self.response_object.status = True
			self.response_object.content = self.cursor.fetchall()
		elif str_response_type == 'CREATE':
			self.response_object.status = True
			self.response_object.content = []
		elif str_response_type == 'DROP S':
			self.response_object.status = True
			self.response_object.content = []
		else:
			# some other problem
			self.response_object.status = False
			self.response_object.content = "Poll failed status_message verification, status_message received: %s" % str_response_type
		
		self.SET_transaction_end()
	
	def GET_response_error(self, err):
		# Handles how exception is handled
		string_exception = str(err)
		
		# Check connection (Disconnect issue: when looking for response after disconnecting)
		if self.conn == None:
			# Do nothing, and continue
			return True
		
		# Exception classes:
		exception_class = type(err)
		if exception_class == psycopg2.errors.DuplicateTable:
			self.response_object.status = False
			self.response_object.content = string_exception[:-1]
			self.SET_transaction_end()
			return True
		else:
			self.response_object.status = False
			self.response_object.content = "undocumented exception: " + string_exception[:-1]
			self.SET_transaction_end()
			return True
		
		self.SET_transaction_end()
	
	# ========================================================
	# Wait and time functions
	# ========================================================
	def wait(self, timeout = None, delay = None):
		# Defaults
		if timeout == None:
			timeout = self.timeout
		if delay == None:
			delay = self.delay

		while(1):
			status = self.poll_response()
			if status:
				break
			elif self.GET_transaction_time() > timeout:
				print("conn.wait() timed out")
				break
			time.sleep(delay)
	
	def _wait_connecting(self, timeout = None, delay = None):
		# Defaults
		if timeout == None:
			timeout = self.timeout
		if delay == None:
			delay = self.delay

		while(1):
			try:
				status = self.poll_state()
			except Exception as err:
				print("Error when trying to connect: ", err)
				return False

			if status:
				break
			elif self.GET_transaction_time() > timeout:
				print("conn.wait() timed out")
				break
			time.sleep(delay)
		return True
	
	# ========================================================
	# Connections and Frontend
	# ========================================================
	def CONNECT(self):
		self.SET_transaction_start()
		
		self.conn = psycopg2.connect(
						database	= self.database	, \
						user		= self.user		, \
						password	= self.password	, \
						host		= self.host		, \
						port		= self.port		, \
						async_		= 1				)
		# Special wait when trying to connect
		self._wait_connecting()
		self.cursor = self.conn.cursor()
		
		self.SET_transaction_end()
		
	def DISCONNECT(self):
		# Shutdown connection
		if not (self.cursor == None):
			self.cursor.close()
			self.cursor = None
		if not (self.conn == None):
			self.conn.close()
			self.conn = None
		
		# All transactions must end
		self.SET_transaction_end()
		
	def RESTART_connection(self):
		self.DISCONNECT()
		self.CONNECT()
		
	def QUERY_DB(self, query):
		if self.transaction_status == "OPEN":
			print("Ongoing query, please use CHECK poll_response first! Query not ran.")
			return False
		
		self.SET_transaction_start()
		self.cursor.execute(query)
		# Able to run
		return True
		
	def CHANGE_database(self, DB):
		self.database = DB
		self.RESTART_connection()
	
	def CHANGE_user(self,username, password):	
		self.user		= username
		self.password	= password
		self.RESTART_connection()
		
	def GET_response(self): # GET_DB_QUERY
		status = self.poll_response()		
		if not status:
			print("No response yet! Make sure to CHECK poll_response first!")

		return self.response_object

# ====================================================================================
# Non-Class connection methods
# ====================================================================================
def connectDB(config=DEFAULT_CONFIG):
	conn = psycopg2.connect(database	=config["database"], \
							user		=config["username"], \
							password	=config["password"], \
							host		=config["server_address"], \
							port		=config["port"])
	return conn

def CREATE_TABLE_DB(sql_command):
	conn = connectDB()
	
	# sql_command = """CREATE TABLE captain_keys.days_est (
	# 						market_day INTEGER PRIMARY KEY NOT NULL,
	# 						year INTEGER NOT NULL,
	# 						month INTEGER NOT NULL,
	# 						day INTEGER NOT NULL
	# 					);"""
	print(sql_command)
	
	try:
		# Table may already exist, do nothing
		cur = conn.cursor()
		cur.execute(sql_command)
	except:
		pass
	
	# close out connection
	cur.close()
	conn.commit()
	conn.close()
	
	return

def INSERT_DB(sql_command):
	conn = connectDB()
	
	#sql_command = """INSERT INTO day_0.tsla_1min VALUES(0,1,2,3,4)"""
	print(sql_command)
	
	
	cur = conn.cursor()
	cur.execute(sql_command)
	
	# close out connection
	cur.close()
	conn.commit()
	conn.close()

def SELECT_DB(sql_command):
	conn = connectDB()
	
	# sql_command = """SELECT id, "open", "close", high, low FROM day_0.tsla_1min;"""
	print(sql_command)
	
	cur = conn.cursor()
	cur.execute(sql_command)
	
	# Response
	list_response = cur.fetchall() # fetches list (line delimited) responses, what happens if just one entry?
	
	# close out connection
	cur.close()
	conn.commit()
	conn.close()

# ====================================================================================
# DEBUG
# ====================================================================================
if __name__ == '__main__':
	# Create connection
	new_connection = PSQL_NON_BLOCK_Connection(DEFAULT_CONFIG)
	
	### Example sql_commands
	# sql_command = """SELECT id, "open", "close", high, low FROM day_0.tsla_1min;"""
	# sql_command = """INSERT INTO day_0.tsla_1min VALUES(0,1,2,3,4)"""
	# sql_command = """CREATE TABLE captain_keys.days_est (
	# 						market_day INTEGER PRIMARY KEY NOT NULL,
	# 						year INTEGER NOT NULL,
	# 						month INTEGER NOT NULL,
	# 						day INTEGER NOT NULL
	# 					);"""
	
	# sql_command = """CREATE TABLE estate.mls_metadata_cincinnati (
	# 						market_day INTEGER REFERENCES captain_keys.days_est(market_day) ON DELETE RESTRICT,
	# 						num_home_general_ask INTEGER,
	# 						num_home_singlefamily_ask INTEGER,
	# 						num_home_singlefamily_rent INTEGER,
	# 						cost_home_general_sqft_median INTEGER
	# 					); """
	
	
	try:
		print('Testing create table, and query error')
		sql_command = """CREATE TABLE captain_keys.days_est (
							market_day INTEGER PRIMARY KEY NOT NULL,
							year INTEGER NOT NULL,
							month INTEGER NOT NULL,
							day INTEGER NOT NULL
						);"""
		new_connection.QUERY_DB(sql_command)
		print('Prior poll_response: ', new_connection.poll_response())
		print('Prior wait response: ', new_connection.GET_response())
		print('Prior transaction_status: ', new_connection.transaction_status)
		new_connection.wait()
		print('After poll_response: ', new_connection.poll_response())
		print('After transaction_status: ', new_connection.transaction_status)
		print('After wait response: ')
		print(new_connection.GET_response()['content'])
		print(new_connection.GET_response().content)
		print(new_connection.GET_response())
		print('===================================')
		
		
		print('Testing insert into table, and insert response')
		sql_command = """INSERT INTO day_0.tsla_1min VALUES(0,1,2,3,4)"""
		new_connection.QUERY_DB(sql_command)
		print('Prior poll_response: ', new_connection.poll_response())
		print('Prior wait response: ', new_connection.GET_response())
		print('Prior transaction_status: ', new_connection.transaction_status)
		new_connection.wait()
		print('After poll_response: ', new_connection.poll_response())
		print('After transaction_status: ', new_connection.transaction_status)
		print('After wait response: ')
		print(new_connection.GET_response()['content'])
		print(new_connection.GET_response().content)
		print(new_connection.GET_response())
		print('===================================')
		
		
		print('Testing select from table, and select response')
		sql_command = """SELECT id, "open", "close", high, low FROM day_0.tsla_1min;"""
		new_connection.QUERY_DB(sql_command)
		print('Prior poll_response: ', new_connection.poll_response())
		print('Prior wait response: ', new_connection.GET_response())
		print('Prior transaction_status: ', new_connection.transaction_status)
		new_connection.wait()
		print('After poll_response: ', new_connection.poll_response())
		print('After transaction_status: ', new_connection.transaction_status)
		print('After wait response: ')
		print(new_connection.GET_response()['content'])
		print(new_connection.GET_response().content)
		print(new_connection.GET_response())
		print('===================================')
		new_connection.DISCONNECT()
	except Exception as err:
		# close out connection before raising error
		new_connection.DISCONNECT()
		raise err