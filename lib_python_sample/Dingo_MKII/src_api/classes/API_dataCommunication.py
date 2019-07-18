'''
	Small, simple classes to handle Data and messages between API processes
'''
import time

FORMAT_Message = {
	"command"	:'',
	"payload"	:None,
}

class Datagram(object):
	'''
		Purpose of the Datagram is to relay dumb information directly to main processes through pipe
	'''
	def __init__(self):
		self.rawData = None
		self.parsedData = None
		
		self.error = False
		
		# Epoch_time
		self.localtime_requested = 0
		self.localtime_received = 0
		
		# Data mode and Source
		self.source = None
		self.mode = None
		self.tag = None
		
	def SET_DataRequested(self):
		self.localtime_requested = time.time()
		
	def SET_DataReceived(self, data, error_bull=False):
		self.localtime_received = time.time()
		
		# Standardize to array of data
		if type(data)== type([]):
			self.rawData = data
		else:
			self.rawData = [data]
		
		if type(error_bull)== type([]):
			self.error = error_bull
		else:
			self.error = [error_bull]
	
	def UPDATE_ParsedData(self, parsedData):
		if type(parsedData)== type([]):
			self.parsedData = parsedData
		else:
			self.parsedData = [parsedData]

	def VET_DataIntegrity(self, error_bull):
		if type(data)== type([]):
			self.error = error_bull
		else:
			self.error = [error_bull]