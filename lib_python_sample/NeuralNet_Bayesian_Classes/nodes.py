# Writing Trinary nodes, True, False, Indeterminate, with outputs of H(up), nH(down), D(indeterminate)
# P(H|A) = P(A|H) * prior(H)/ P(A|H) + P(A|nH) + P(A|D), cyclic on P(H|A), P(nH|A), P(D|A) with sum = P(outcomes|A)
# 

num_sigma = 0.9545 # Number of standard deviations we hold for Threshold as a probability. Two-tailed
default_slave_target_value = 0 # If slave_node cannot find target_node (such that it's dead or not located), use this value instead

def Inst2List(inst_or_list):
	# quick helper type
	if type(inst_or_list) == type([]):
		return inst_or_list
	else:
		return [inst]

def CALC_posterior(state, prior, probTrue_wH, probTrue_notH):
	"""
		returns the posterior probability based on the ratios state_given_H and state_given_notH
		
		# The general case of this is probability of edvidence_state, and a list of [prob(edvidence_state) given H'i]
		# The general posterior would then be a submation of the probable diresired outcomes given as list
		
		# Here we focus only on desired outcomes: wH, notH, [D is whatever left over]
	"""
	
	# state = boolean T/F
	try:
		if state == 'INDETERMINATE' or 'NEUTRAL':
			return prior
		if state:
			A = probTrue_wH
			B = probTrue_notH # P(T| notH U D) ) = P(T|notH) + P(T|D) - P(T| notH in D)
		else:
			A = 1 - probTrue_wH
			B = 1 - probTrue_notH
			"""
			if probFalse_wH == None or probFalse_notH == None:
				A = 1 - probTrue_wH
				B = 1 - probTrue_notH
			else:
				A = probFalse_wH
				B = probFalse_notH
			"""
	except:
		print"state must be a boolean"
	
	# posterior = A*prior/(prior*A+(1-prior)*B)
	return A*prior/(prior*A+(1-prior)*B)

"""
Implementing a New Paradigm,
	since each Node contains a list of slave_nodes with tracking:
	slv_node1	slv_node2	slv_node3	slv_node4	slv_node5 > Node;
	Then clearly the running posterior value of Node should be caluclate on the structure of the slv_nodes
	
	For each slv_node type, we will use slv_node.CALC_Posterior(self, edvidence_state, outcome_states, prior): to return the posterior based on the slv.node's value
	Currently we will deal with the following types of slv_nodes:
	- Binary
	- Tristate
	- Multiple Discrete
"""	
class SlaveNode_General():
	"""
		Learning from the trisate slavenode,
		We'll develope a table of binary possibilities of P(A|B), a counting table of [A][B], and total count to subtract numbers from
	"""
	def __init__(self, ID, num_possible_inputs=2, num_possible_outputs=2):
		self.target_ID = ID
		self.num_possible_inputs = num_possible_inputs
		self.num_possible_outputs = num_possible_outputs
		
		# P(A|H)
		self.probMatrix_IN_given_OUT = [[0.5 for i in range(self.num_possible_inputs)] for j in range(self.num_possible_outputs)]
		
		# To calculate P(A|notH) later in calculating prior
		self.countMatrix_IN_given_OUT = [[0 for i in range(self.num_possible_inputs)] for j in range(self.num_possible_outputs)]
		self.count_perOutputs = [0 for j in range(self.num_possible_outputs)]
		self.countTotalObs = 0
		
	def updateCount(self, state_input, state_output):
		# state_input represents the vector input mapped from trainning data
		# state_output or state_feedback represents the output or reinforcement state
		
		self.countMatrix_IN_given_OUT[state_input][state_output] +=1
		self.count_perOutputs[state_output] +=1
		self.countTotalObs +=1
		
	def updateProb(self):
			
		for idx_input in range(self.num_possible_inputs):
			for idx_output in range(self.num_possible_outputs):
				self.probMatrix_IN_given_OUT[idx_input][idx_output] = self.countMatrix_IN_given_OUT[idx_input][idx_output] / self.count_perOutputs[idx_output]
	
	def CALC_Posterior(self, edvidence_state, outcome_states, prior):
		# coeherse a list
		outcome_states = Inst2List(outcome_states)
		
		# If node not triggered
		if self.countTotalObs ==0:
			return prior
		
		# Breaks logic down to binary calculation
		state = True
		
		# edvidence_state = one edvidence point
		# outcome_states = vector union of channels [3,4, etc.] (when looking at possible collection of outcomes) (also mapping probability distributions)
		
		# Find probTrue_wH (wH = JUKUL, union)
		# P(A|H) = sum( P(A|H)P(H) ); P(H) = P(H|Obs) = #H/#Obs
		# P(A|H) = sum( P(A|J)P(J|Obs), P(A|K)P(K|Obs) , etc.) 
		
		# Figure outcome and non-coutcome counts, assume few outcomes
		count_outcomeObs = 0
		for idx_output in outcome_states:
			count_outcomeObs += self.count_perOutputs[idx_output]
		
		# Find probTrue_wH
		probTrue_wH = 0		
		for idx_output in outcome_states:
			probTrue_wH += self.probMatrix_IN_given_OUT[edvidence_state][idx_output] * self.count_perOutputs[idx_output] / count_outcomeObs
		
		
		# Find probTrue_notH
		count_non_outcomeObs = self.countTotalObs - count_outcomeObs
		
		probTrue_notH = 0
		for idx_output in range(self.num_possible_outputs):
			# check if non_outcome_states
			if not(idx_output in outcome_states):
				idx_non_outcome = idx_output
				
				probTrue_notH += self.probMatrix_IN_given_OUT[edvidence_state][idx_non_outcome] * self.count_perOutputs[idx_non_outcome] / count_non_outcomeObs
		
		
		return CALC_posterior(state, prior, probTrue_wH, probTrue_notH)
		
	def reset_count():
		# To calculate P(A|notH) later in calculating prior
		self.countMatrix_IN_given_OUT = [[0 for i in range(self.num_possible_inputs)] for j in range(self.num_possible_outputs)]
		self.count_perOutputs = [0 for j in range(self.num_possible_outputs)]
		self.countTotalObs = 0
	
	def _export(self):
		export_dict = {
			"target_ID"			 :self.target_ID,
			"num_possible_inputs"   :self.num_possible_inputs,
			"num_possible_outputs"  :self.num_possible_outputs,
			"probMatrix_IN_given_OUT"  :self.probMatrix_IN_given_OUT,
			"countMatrix_IN_given_OUT"  :self.countMatrix_IN_given_OUT,
			"count_perOutputs"		  :self.count_perOutputs,
			"countTotalObs"		 :self.countTotalObs,
		}
		return export_dict

	def _import(self, import_dict):
		self.target_ID = import_dict["target_ID"]
		self.num_possible_inputs = import_dict["num_possible_inputs"]
		self.num_possible_outputs = import_dict["num_possible_outputs"]
		self.probMatrix_IN_given_OUT = import_dict["probMatrix_IN_given_OUT"]
		self.countMatrix_IN_given_OUT = import_dict["countMatrix_IN_given_OUT"]
		self.count_perOutputs = import_dict["count_perOutputs"]
		self.countTotalObs = import_dict["countTotalObs"]

class SlaveNode_Tristate(SlaveNode_General):
	def __init__(self, target_ID):
		SlaveNode_General.__init__(self, target_ID, num_possible_inputs=3, num_possible_outputs=3)

class SlaveNode_Bistate(SlaveNode_General):
	def __init__(self, target_ID):
		SlaveNode_General.__init__(self, target_ID)

class TriNode():
	"""
		Idea is that this should contain:
		1) Own state (dependent of data input)
		2) Threshold for True/False/Indeterminate; True = 2, Indeterminate = 1, False = 0
		3) Running Posterior value
		4) a list of slave nodes (lower level nodes this grabs data from)
			a) list contains duples of [prob_wH,prob_notH] ratios
			b) should default to 50/50 if pror node is indeterminate > done in calc_posterior
	"""
	def __init__(self, givenID, threshold):
		# 1,2,3) Own state & thresholds
		self.nodeID = givenID
		self.state = 1 #'INDETERMINATE'
		self.threshold = threshold # 2sigma
		
		# 4) list of slave nodes
		"""
			going with a lookup approach, potential botle neck of looping if taking full vector
		"""
		self.list_slaveNodes = [] # [1,3,4,7] vector of slavenodes [o(ID=1, prob_wH, prob_notH), o(ID=3, prob_wH, prob_notH), o(ID, prob_wH, prob_notH), etc.]
	
	def add_SlaveNode(self, *args, **kwargs):
		"""
			creates a SlaveNode (synapsis) and appends to list of slave nodes
		"""
		new_slaveNode = SlaveNode_Tristate(*args, **kwargs)
		self.list_slaveNodes.append(new_slaveNode)
		return
		
	def add_SlaveEnsemble(self, list_target_nodes):
		"""
			Adds an Ensemble of synapsis to Node
			list_target_nodes = [[1,0][1,3][1,84][0,2]]
		"""
		for targetID in list_target_nodes:
			self.add_SlaveNode(targetID)
			
	def remove_SlaveNode(self, targetID):
		"""
			Finds and Slices out synapsis
		"""
	
	def remove_SlaveEnsemble(self, list_target_nodes):
		"""
			Removes Ensemble of targetID's (synapsis) from node of interest
			*this feature may require some index to quickly locate and remove, otherwise better to just delete Node all together
		"""
		
	def GET_slaveNode_targetstate(self, local_matrix, slave_node):
		state = local_matrix[slave_node.target_ID[0]][slave_node.target_ID[1]]
		
		# default node behavior
		if not(type(state)==type(7)):
			state = default_slave_target_value
		return state
	
	def trainNode_count(self, local_matrix, outcome_state):
		for slave_node in self.list_slaveNodes:
			# Get state from local_matrix corrsponding to slave_node.target_ID
			input_state = self.GET_slaveNode_targetstate(local_matrix, slave_node)
		
			slave_node.updateCount(input_state, outcome_state)

	# Due to total size of Node Net and abstraction ratios, we will only pass in local-Nth# of rows from the total Node-Net
	# the local Matrix is compiled from the 0th row and compiled upward to the Nth# = this Node's row (determined by position in Node_Net)
	def runNode(self, local_matrix):
		# Check to make sure local_matrix is of appropiate max(row)
		# If max_row <= largest slave_node_target_row -> throw exception
		max_row = len(local_matrix)
		for slave_node in self.list_slaveNodes:
			if slave_node.target_ID[0] >= max_row:
				print "Slave Node issue:"
				print slave_node._export()
				print "Local Matrix Max(row#) = %d"% max_row
				raise Exception("Refering slavenodes exceed the Max(row) of local_matrix")

		# Else, continue onto running the node
		# Assume neutral bias
		bayesPropTrue = 0.5
		bayesPropFalse = 0.5
		
		for slave_node in self.list_slaveNodes:
			# Get state from local_matrix corrsponding to slave_node.target_ID
			state = self.GET_slaveNode_targetstate(local_matrix, slave_node)
			
			#set new bayesian probability (True = 2, Indeterminate = 1, False = 0)
			bayesPropTrue = slave_node.CALC_posterior(state, 2, bayesPropTrue)
			bayesPropFalse = slave_node.CALC_posterior(state, 0, bayesPropFalse)
			
		#set State of current node
		if bayesPropTrue > self.threshold:
			self.state = 2 #True
		elif bayesPropFalse > self.threshold:
			self.state = 0 #False
		else:
			self.state = 1 #"INDETERMINATE"
		return self.state
	
	def getState(self):
		return self.state
		
	def _export(self):
		export_slaveNodes = []
		for slave_node in self.list_slaveNodes:
			export_dict = slave_node._export()
			export_slaveNodes.append(export_dict)

		new_dict = {
			"nodeID"	:self.nodeID,
			"state"		:self.state,
			"threshold"	:self.threshold,
			"list_slaveNodes"	:export_slaveNodes,
		}
		return new_dict

	def _import(self, import_dict):
		self.nodeID = import_dict["nodeID"]
		self.state = import_dict["state"]
		self.threshold = import_dict["threshold"]
		self.list_slaveNodes = []
		
		for dict_slaveNode in import_dict["list_slaveNodes"]:
			new_slaveNode = SlaveNode_Tristate([0,0]) # Target irrelevent as over written during import
			new_slaveNode._import(dict_slaveNode)
			self.list_slaveNodes.append(new_slaveNode)

# *****DEBUG***************************
DEBUG = False
def DEBUGT():
	test = TriNode([1,0],num_sigma)
	
	dict_export = test._export()
	
	test._import(dict_export)
	
	test.add_SlaveNode([0,0])
	test.add_SlaveNode([0,1])
	test.add_SlaveNode([0,2])
	dict_export = test._export()
	print dict_export
