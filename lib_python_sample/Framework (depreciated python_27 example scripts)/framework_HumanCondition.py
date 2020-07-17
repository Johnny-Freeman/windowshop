import random
import time
from scipy.stats import t

def HumanCondition(a,b, display=True):
	'''
		Waits a random period of time interval (a,b), display message is optional
	'''
	rand = random.uniform(a,b)
	if display:
		print('Human Condition, waiting: ' + str(rand) + ' sec')
	time.sleep(rand)
	return True
	
def CHECK_HumanCondition(prob, pow2):
	'''
		Similar in function to Human Condition, but this gives a dice roll True/False instead of blocking a timed interval
	'''
	population = 2.0**pow2
	
	winstat = population * prob
	
	# Generate random number
	lottery = random.uniform(0,population)
	
	if lottery < winstat:
		return True
	else:
		return False

def CHECK_execute_HumanCondition(number_standard_deviations,iterations):
	'''
		Provides a True or False depending on number of times (iterations) this function is called in total
		, the probability of a True being returned at least once during these iterations is given by the number of standard deviations passed in
		
		https://stackoverflow.com/questions/23879049/finding-two-tailed-p-value-from-t-distribution-and-degrees-of-freedom-in-python
		Degrees of freedom = 3, 1st = marketprice, 2nd = loss condition, 3rd # of taker fees
	'''
	
	# num_STD > percent (p-value)
	final_not_prob = t.sf(number_standard_deviations,2)
	
	# per iteration not probability, itera_root(final_not_prob)
	init_not_prob = final_not_prob **(1.0/iterations)
	
	# do simulation to see if should execute:
	return CHECK_HumanCondition(1.0-init_not_prob, iterations)