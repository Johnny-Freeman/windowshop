'''
	Classes to Hold Data pertaining to various thresholds imposed on the API
	-Rate Limits, helps monitor and keep track of the number of API requests
'''
import time

Debug = False

CONFIG_API={
	'heartbeat'			: 3,	# seconds
	
	'allowance_Public'	: 10,	# number per heartbeat
	'allowance_Private'	: 20,
	}

class RateLimits(object):
	def __init__(self, owner, config):
		self.owner = owner
	
		# Refresh period of rate allowance, in seconds
		self.heartbeat = config['heartbeat']
		self.time_prevHeartbeat = 0
		if self.heartbeat > 60:
			print'Warning: config.heartbeat specified is greater than 60 seconds, just a warning, still valid'
		
		# Allowance per heartbeat
		self.allowance_Public = config['allowance_Public']
		self.allowance_Private = config['allowance_Private']
		
		# Amount of allowance used
		self.used_Public = 0
		self.used_Private = 0
		
		self.update_allowance()
	
	def update_allowance(self):
		now = time.time()
		if now - self.time_prevHeartbeat > self.heartbeat:
			self.time_prevHeartbeat = now
			self.used_Public = 0
			self.used_Private = 0
	
	def accessPublic(self):
		self.update_allowance()
		self.used_Public+=1
		
		if self.used_Public > self.allowance_Public:
			print'Warning: '+self.owner+'_ Public Rate allowance exceeded by: ',(self.used_Public-self.allowance_Public)
			return False
			
	def accessPrivate(self):
		self.update_allowance()
		self.used_Private+=1

		if self.used_Private > self.allowance_Private:
			print'Warning: '+self.owner+'_ Private Rate allowance exceeded by: ',(self.used_Private-self.allowance_Private)
			return False
			
	def Remaining(self):
		'''
			Returns dictionary indicating number of calls remaining
		'''
		remain_public = self.allowance_Public - self.used_Public
		if remain_public < 0:
			remain_public = 0
			
		remain_private = self.allowance_Private - self.used_Private
		if remain_private < 0:
			remain_private = 0
		
		remain={
			'public'		: remain_public,
			'private'		: remain_private,
			'nextHeartbeat'	: (self.time_prevHeartbeat + self.heartbeat - time.time()),
		}
		return remain
	
if Debug:
	print 'API_threshold Debug MODE on!'
	test = RateLimits('ALLYTK',CONFIG_API)
	for i in range(21):
		test.accessPrivate()
	print test.Remaining()
	time.sleep(2)
	for i in range(21):
		test.accessPrivate()
	print test.Remaining()
	time.sleep(2)
	for i in range(21):
		test.accessPrivate()
	print test.Remaining()
	