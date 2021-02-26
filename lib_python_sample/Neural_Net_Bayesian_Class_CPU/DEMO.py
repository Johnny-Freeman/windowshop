# This demonstrates basic functionality and dynamic scope of Neural Net Class
# Demo:
#	- add_Node
#		Adds desired Node to exact location in neural net
#	- append_Node
#		Add desired Node to desired abstraction level
#	- remove Node
#		removes any node form neural net
#	- import/export
#		exports the entire neural net to a text readable format
#		imports the entire neural net from text format into active application
#		Allows post-use analysis of neural net

from node_net import NodeNet

# Create Neural Net
net = NodeNet()

# Add Node, Neural Net requires reference or "slave" nodes to reference for data
# Doubles as replace_Node
# add_Node([x,y location], p-value_reject(bayesian threshold), [list of [reference_node_location] ] )
net.add_Node([1,2], 0.75, [ [0,1],[0,2] ])

# Append Node, similar to Add_Node, but adds to defined abstraction level
# append_Node([abstraction, p-value_reject(bayesian threshold), [list of [reference_node_location] ] )
net.append_Node(1, 0.75, [ [0,1],[0,2] ])

# Exports readable format
net_expt = net._export()
print net_expt
print "\n"

# *****Modfying Net from previous save**************************

# Create a new Net
new_net = NodeNet()

# Import prior saved Net
new_net._import(net_expt)

# Modify Net
new_net.append_Node(1, 0.75, [ [0,1],[0,2] ])

# Export Net
print new_net._export()
new_net.remove_Node([1,2])
print new_net._export()