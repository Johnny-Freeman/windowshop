'''
	API specific json stuff
'''
import json, re

def string2bool(input):
	if type(input)==type([]):
		list_bools=[]
		for bool in input:
			if bool == 'True' or bool == 'true' or bool == 'TRUE' or bool=='1':
				list_bools.append(True)
			else:
				list_bools.append(False)
		return list_bools
		
	else:
		if bool == 'True' or bool == 'true' or bool == 'TRUE' or bool=='1':
			return True
		else:
			return False

def parse_string2list(input, delimiter = ',', brackets=False):
	"""
		brackets indicates length of bounding notations, True = 1, or any number of bounding characters
	"""
	list_input = input.split(delimiter)
	
	if not brackets==False:
		if brackets==True:
			brackets=1
		
		# Remove brackets '[' and ']'
		int_end = len(list_input) - 1
		
		list_input[0] = list_input[0][brackets:]
		list_input[int_end] = list_input[int_end][:-brackets]
	
	return list_input

def parse_json2dict(input):
	'''
		input is r = requests.post(url = ) response object <string>
	'''
	try:
		return json.loads(input.encode('ascii', 'ignore')	)
	except:
		print 'problem parsing response as json...', "length: ", len(input), "input: ", input
		return input
		
def CHECK_quickError(json_string, length=255, terminal='FRONT'):
	'''
		to prevent unnecessary parsing, we use regular expressions to quickly check the front or back of the response for error keywords
		True = Error found, response should be parsed and looked into more deeply
		False = No error keyword found, probable good response 
	'''
	
	if terminal =='FRONT':
		string2search = json_string[:length]
	else:
		string2search = json_string[-length:]
	
	# Search for error keywords:
	pattern = re.compile('[E,e]rror')
	match = re.findall(pattern, string2search)
	
	if len(match) > 0:
		return True
	else:
	 return False
