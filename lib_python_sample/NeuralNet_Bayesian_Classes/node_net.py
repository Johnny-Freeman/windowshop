from nodes import TriNode

emptyNode_placeholder = "NaN"

class Node_Map():
	# Acts similar to lists, but doubles as a static state map
	# Not used yet
	def __init__(self):
		self.li = []
		self.state_map = [] # hidden
	
	def __getitem__(self, item):
		return self.li[item]
	
	def append(self, obs):
		self.li.append(obs)
		self.state_map.append(emptyNode_placeholder)

class NodeNet():
	"""
		1) Holds totality of node structure
		2) Calls each node per node level to return state
		3) Keeps track of previous level's vector of states
		
		**NodeNet is calculated per ONE input vector, unless trainning (inwhich case, make a second version of the nodeNet
		4) Used to call input vector
			nodeNet.setInputVector([input vector from user defined node-lvl's])
			[list_bool] = nodeNet.getOutput //returns a list of final bool vector
	"""
	def __init__(self, depth = 0):
		# 4 level nodeNet : self.node_net = [[lvl-1],[lvl-2],[lvl-3],[lvl-4]]
		self.node_net = [] # [[],[],[],[]]
		self.depth = depth
		self.PRINT_NetDepth()
		
		# Holds static map = [ [1,0,1,0,1]<vector_input, level-0, dynamic row>,	 [1,0,1,0,1] (higher level rows of abstraction), [1,0,1,0,1], [1,0,1,0,1]]
		# Passed into each node when needed
		self.state_map = []
		
		#self.vector_input = []
		#self.vector_output = []
		return
	
	# *****State Functions**********************
	def GET_Node(self, node_id):
		return self.node_net[node_id[0]][node_id[1]]
	
	def GET_Node_State(self, node_id):
		return self.GET_Node().state
		
	def GET_depth(self):
		return len(self.node_net)
		
	def PRINT_NetDepth(self):
		print ("NodeNet depth : %s" % self.depth)
	
	# ******Node Net Management*****************
	def add_Node_level(self, num_levels):
		#list comprehension is just overhead (just does recursion)
		if num_levels <= 0:
			self.depth = self.GET_depth()
			return
		
		# Both node_net, state_map -> make list_like class that mirrors the node_net but houses static values?
		self.node_net.append([])
		self.state_map.append([])
		
		self.add_Node_level(num_levels-1)
		
	def fill_EmptyNodesinLevel(self, node_level, num_nodes):
		#list comprehension is just overhead (just does recursion)
		if num_nodes <= 0:
			return
		
		# Both node_net, state_map
		self.node_net[node_level].append(emptyNode_placeholder)
		self.state_map[node_level].append(emptyNode_placeholder)
		
		self.fill_EmptyNodesinLevel(node_level, num_nodes-1)

	def add_EmptyNodestoFill(self, node_level, num_index):
		if node_level >= self.depth:
			levels_needed = node_level+1 - self.depth
			self.add_Node_level(levels_needed)
		
		#list comprehension is just overhead (just does recursion)
		curr_level_idx = len(self.node_net[node_level])
		if num_index >= curr_level_idx:
			nodes_needed = num_index+1 - curr_level_idx
			self.fill_EmptyNodesinLevel(node_level, nodes_needed)
		
	def append_Node(self, node_level, threshold, slaveNodeEnsemble):
		if node_level >= self.depth:
			levels_needed = node_level+1 - self.depth
			self.add_Node_level(levels_needed)
		
		last_node_level_idx = len(self.node_net[node_level])
		
		node_id = [node_level, last_node_level_idx]
		new_node = TriNode(node_id, threshold)
		new_node.add_SlaveEnsemble(slaveNodeEnsemble)
		
		# Both node_net, state_map
		self.node_net[node_level].append(new_node)
		self.state_map[node_level].append(emptyNode_placeholder)
	
	def add_Node(self, node_id, threshold, slaveNodeEnsemble):
		new_node = TriNode(node_id, threshold)
		new_node.add_SlaveEnsemble(slaveNodeEnsemble)
		
		# if Node out of range > generate matrix to fill
		self.add_EmptyNodestoFill(node_id[0], node_id[1])
		self.node_net[node_id[0]][node_id[1]] = new_node
	
	def kill_Node(self, node_id):
		self.node_net[node_id[0]][node_id[1]] = emptyNode_placeholder
		
	def remove_Node(self, node_id):
		self.node_net[node_id[0]].pop(node_id[1])
		self.state_map[node_id[0]].pop(node_id[1])
	
	# ******Node Net Operations*****************
	def setInputVector(self, vector_input):
		if not (	type(vector_input) == type([])	):
			raise Exception("input vector must be list")
		self.node_net[0] = vector_input # sets Node_lvl-0 as the input vector
		self.state_map[0] = vector_input # sets Node_lvl-0 as the input vector
		
	def runNodeNet(self):
		# Passes lower portion of the Net into each node (this Node net doesn't allow loop-backs down into lower rows)
		for idx_depth in [1, len(self.node_net)]:
			for idx_node in len(self.node_net[idx_depth]):
				# pass in local Matrix (in python this grabs the address of object)
				node = self.node_net[idx_depth][idx_node]
				
				if node == emptyNode_placeholder:
					self.state_map[idx_depth][idx_node] = emptyNode_placeholder
				else:
					node.runNode(self.state_map[:idx_depth])
					# Set the static state_map with the new node value
					self.state_map[idx_depth][idx_node] = node.getState()
		
	def getOutput(self):
		self.runNodeNet()
		return self.node_net[-1]
	
	# *****export/import***********************
	def _export(self):
		# write all nodes into list of dicts.
		dict_node_net = []
		for ins_depth in self.node_net:
			new_node_level = []
			for node in ins_depth:
				if node == emptyNode_placeholder:
					new_node_level.append(node)
				else:
					new_node_level.append(node._export())
			dict_node_net.append(new_node_level)
			
		new_dict = {
			"state_map"	:self.state_map,
			"node_net"	:dict_node_net,
		}
		return new_dict
	
	def _import(self, import_dict):
		self.state_map = import_dict["state_map"]
		
		new_node_net = []
		for ins_depth in import_dict["node_net"]:
			new_node_level = []
			for node_dict in ins_depth:
				if type(node_dict) == type("str"):
					new_node_level.append(node_dict)
				else:
					new_node = TriNode([0,0], 0.5)
					new_node._import(node_dict)
					new_node_level.append(new_node)
			
			new_node_net.append(new_node_level)
		self.node_net = new_node_net


# ****Trainning methods / Debugging*************************************
#net = NodeNet()
#net.add_Node([1,2], 0.75, [ [0,1],[0,2] ])
#net_expt = net._export()
#print net_expt
#print "\n"
#
#new_net = NodeNet()
#new_net._import(net_expt)
#new_net.append_Node(1, 0.75, [ [0,1],[0,2] ])
#new_net.append_Node(1, 0.75, [ [0,1],[0,2] ])
#print new_net._export()
#new_net.remove_Node([1,2])
#print new_net._export()

class NodeNetTrainning(NodeNet):
	#built on top of NodeNet, using slavenode's counters recalculating H, not H
	def __init__(self):
		return
	def exportNodeNet(self):
		return
	
	def resetNodeNet(self):
		self.node_net = []
	
	"""
		1) must work on each node level one at a time
			a) Add node level of [ node[o(slave_nodes)] , o(nodes),o,o,o,]
			b) run nodenet per data instance
				- feed an input_vector
				- feed feedback_vector, single or a vector = length of node vector, can train as many and as few nodes at a time.
			c) count per instance (saved into node[o(slave_nodes)]
				- Each time Feedback = True occurs
				- Each time Feedback = False occurs
				- Each time NodeState=True, given True feedback occurs
				- Each time NodeState=True, given False feedback occurs
			d) calculate
	"""