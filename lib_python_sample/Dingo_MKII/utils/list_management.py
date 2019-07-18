'''
	Functions found to be useful across more-than-one API
'''
# *** Globals (includes classes)*******************

# *** END Globals *********************************
def combine_lists(first_list,second_list):
	resulting_list = list(first_list)
	resulting_list.extend(x for x in second_list if x not in resulting_list)
	return resulting_list

def reverse(seq):
	'''
		https://stackoverflow.com/questions/39502915/reverse-a-list-without-using-built-in-functions
	'''
	return seq[::-1]
	
def split_list_byInt(a_list, int):
	'''
		splits list at specified int ("split added to int position, while the int'th index is moved to next list")
		returns BOTH lists
	'''
	# If list is longer than desired int
	if int < len(a_list):
		b = a_list[:int]
		c = a_list[int:]
	
	# If list is <= int, meaning no point in splitting
	else:
		b = a_list
		c = []
	
	return b,c

from itertools import compress, count, imap, islice
from functools import partial
from operator import eq
def index_nth_item(iterable, item, n=1):
	# https://stackoverflow.com/questions/8337069/find-the-index-of-the-nth-item-in-a-list
	# requires imports
	
	n = n -1
	indicies = compress(count(), imap(partial(eq, item), iterable))
	return next(islice(indicies, n, None), -1)

def insert_gen(a_list, position, item):
	'''
		inserts item AT a_list[position], shifts right
	'''
	b,c = split_list_byInt(a_list, position)
	return (b + item + c)

def insert_atTrigger(a_list, trigger, item, indexorder=1, ba='AFTER'):
	'''
		Searches a_list for trigger
		After so many <trigger> are counted (indexorder), inserts <insert> AFTER the trigger
		
		Params:
		a_list		list to be edited
		trigger		element to search for, will NOT change if direction reversed
		item		element to insert <before or after> (+-1, in reverse it does same thing)
		indexorder	direction of search and number:
						Positive numbers search forward from origin
						Negative numbers search backwards from origin
		ba			insert before or after trigger
		origin		TBD later, it's messing up the logic big time, and it's not needed at the moment
	'''
	
	# 1) Going forward or reverse (r,relative)?
	#	 Reverse operations will need to be reversed later before concat
	r_indexorder = abs(indexorder)
	r_str = ""								# faster to wait to set later
	r_baNum = (1 if ba=='AFTER' else 0)		# number representing index shift if inserting before(0) or after(1)
	
	# 2) forward / reverse search
	if indexorder > 0:
		r_str = a_list
	else:										# If reverse
		r_str = reverse(a_list)
		r_baNum = (0 if r_baNum == 1 else 1)	# must also reverse the insert direction
	
	# 3) Work with relative direction	
	# insert <item> at nth_index
	nth_index = index_nth_item(r_str, trigger, r_indexorder)
	
	if not (nth_index == -1):
		nth_index = nth_index + r_baNum
		r_str = insert_gen(r_str, nth_index, item)
	
	# 4) Forward / reverse Undo mapping
	if indexorder > 0:
		return r_str
	else:
		return reverse(r_str)