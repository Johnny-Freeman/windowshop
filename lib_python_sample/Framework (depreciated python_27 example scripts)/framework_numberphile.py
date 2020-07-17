'''
	Functions to simulate random math utilities such as random wait periods, with a certain level of probable of execution
'''

import math, random

Debug = False

def integrate1overExp(init, fina):
	initial = math.sinh(init) - math.cosh(init)
	final = math.sinh(fina) - math.cosh(fina)
	integral = final - initial
	return integral
	
def generate_randomString():
	return lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])

def main():
	#starttime = time.time()
	i = 0
	while(not CHECK_execute_HumanCondition(1,10)):
		i +=1
	#print (time.time()-starttime)
	
if Debug:
	main()