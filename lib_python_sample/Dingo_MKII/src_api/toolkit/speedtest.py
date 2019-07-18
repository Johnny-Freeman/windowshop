import time

def retmillis():
	millis = int(round(time.time() * 1000))
	return millis
	
def printmillis():
	millis = int(round(time.time() * 1000))
	print millis

def run_it(funct, iterations):
	start = retmillis()

	newinstfunct = funct

	for i in range(iterations):
		newinstfunct()

	end = retmillis()
	time =  end-start
	return time

def testit(funct, i):
	tottime = run_it(funct,i)
	avg = float(tottime) / float(i)

	print ('Your program took: ' + str(tottime) + ' milliseconds Total')
	print ('Your program took: ' + str(avg) + ' milliseconds Average')

# ************** Testing grounds *****************************

'''
bull = True
prob=0.31
oneminus=1.00-prob
def testing_grounds1():
	global prob
	global bull

	bull = not bull
	if bull:
		prob = 1.00- prob
	
	
def testing_grounds2():
	global prob
	global bull
	
	newvar = 1
	bull = not bull
	if bull:
		newvar=prob
	else:
		newvar=oneminus
		

testit(testing_grounds1, 1000000)
testit(testing_grounds2, 1000000)
'''