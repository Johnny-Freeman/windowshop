'''
	Defines a session and possible manager to handle multiple future OAuth1 sessions
'''

''' Example Usage

	DIRECT
	pie = OAuth1Session(username				= 'blah',
						userpass				= 'blah',
						client_Consumer_Key		= 'blah',
						client_Consumer_Secret	= 'blah',
						client_Token			= None, #optional, for static tokens
						client_Token_Secret		= None, #optional
						token_filename			= token_filename #fixed
						**kwargs):				
	-or-
	
	CONFIG FILE
	CONFIG_UR2 = {	'sandboxMode'			: False,
					'username'				: 'flamingpope',
					'userpass'				: '785754Jf15!',
					'client_Consumer_Key'	: 'FFkTdt5Yxv1qoi9b9LGuKCG0SaJoKWkyoza8UrmRueQ8',
					'client_Consumer_Secret': 'fu8PCRJTntjVqiufjlSg0EYBKe54l4OMJSRs5xelCDg4',
					'client_Token'			: '4o49P1NZCTPoHPx8EMopZbtEuV1jq81dCp7oi5JGRtE1', #optional, for static tokens
					'client_Token_Secret'	: '3z8l1ZiHjfCD14dQlpZhfRp6BKvC89zLvuz3ClVySZY3', #optional
					'token_filename'		: token_filename,
	}
	pie = OAuth1Session(CONFIG_UR2)
'''
import pickle

class OAuth1_Credentials(object):
	def __init__(self,
					config = None,
					username = None,
					userpass = None,
					client_Consumer_Key=None,
					client_Consumer_Secret=None):
		
		if config == None:
			# check for proper arguments
			for k,v in locals().items():
				if v ==None:
					print'Warning without config, must have argument: ',k
			
			self.username = username
			self.userpass = userpass
			self.client_Consumer_Key = client_Consumer_Key
			self.client_Consumer_Secret = client_Consumer_Secret
			
		else:
			self.username = config['username']
			self.userpass = config['userpass']
			self.client_Consumer_Key = config['client_Consumer_Key']
			self.client_Consumer_Secret = config['client_Consumer_Secret']

class OAuth1Session(OAuth1_Credentials):
	def __init__(self,
					config = None,
					client_Token = None,
					client_Token_Secret = None,
					token_filename = 'None.p',
					**kwargs):
		
		self.initiated = False
		OAuth1_Credentials.__init__(self, config=config, **kwargs)
		
		# Initiate variables
		self.client_Token = client_Token
		self.client_Token_Secret = client_Token_Secret
		self.token_filename = token_filename
		
		# Connection Type
		self.sessionType = 'undefined'
		self.SET_session_type(config=config)
		
	def UPDATE_token(self, client_Token, client_Token_Secret):
		self.client_Token = client_Token
		self.client_Token_Secret = client_Token_Secret
		
	def SET_session_type(self, config=None, session_type=None):
		if not config == None:
			try:
				self.token_filename = config['token_filename']
				self.client_Token = config['client_Token']
				self.client_Token_Secret = config['client_Token_Secret']
			except:
				pass
	
		if not session_type == None:
			self.sessionType = session_type
		
		elif self.initiated==False:
			if self.client_Token == None:
				self.sessionType = 'DYNAMIC'
			else:
				self.sessionType = 'STATIC'
			
			self.initiated = True
	
	def save_session(self):
		'''
			This should write token to directed self.filename
		'''
		oauth_tokens_dict = {
				'oauth_token' : self.client_Token,
				'oauth_token_secret' : self.client_Token_Secret
			}
		pickle.dump( oauth_tokens_dict, open( self.token_filename, "wb" ) )
		return
	
	def load_session(self):
		'''
			This should read tokens from self.filename
			Currently not handled so don't use
		'''
		try:
			user_tokens = pickle.load( open( self.token_filename, "rb" ) )
			
			self.client_Token = user_tokens['oauth_token']
			self.client_Token_Secret = user_tokens['oauth_token_secret']
		
		except IOError:
			# if the token file does not exist, it should be created
			#return {'Error: ' + self.token_filename + ' file missing, will be created/handled later'}
			return False
		
		return True
		