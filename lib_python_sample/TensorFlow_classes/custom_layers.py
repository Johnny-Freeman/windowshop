# =======================================================
# Defining a cutom bayesian Layer, lets see how this influences model
# =======================================================
import tensorflow as tf

class Linear_Normalization(tf.keras.layers.Layer):
	def __init__(self, rectified=True, axis=-1, **kwargs):
		super().__init__()
		
		if rectified:
			self.rectifier = tf.keras.layers.ReLU(**kwargs)
		else:
			self.rectifier = lambda x:x
			
		self.axis = axis
		
	def call(self, inputs):
		inputs = self.rectifier(inputs)
		
		t_reduced_sum = tf.math.reduce_sum(inputs, axis=self.axis, keepdims=True)
		return tf.math.divide(inputs, t_reduced_sum)

# =================================================
# My First Layer
# Adds inductive reasoning to program
# =================================================
class Simple_Bayes_Layer(tf.keras.layers.Layer):
	def __init__(self,
				num_outputs,
				loss_fn=tf.keras.losses.KLDivergence(reduction="sum_over_batch_size"), ## ** https://www.tensorflow.org/api_docs/python/tf/keras/losses/KLDivergence
				**kwargs):
		super().__init__(**kwargs)
		self.num_outputs = num_outputs
		
		# Init loss function
		# https://keras.io/api/losses/
		# ** for Bayes, individual losses are P(orig_bias)Ln(outputs)
		self.loss_fn = loss_fn # averages over batch (eg. sum/32)
	
	# https://www.tensorflow.org/lite/guide/ops_compatibility
	def build(self, input_shape,
					kernel_constraint	= tf.keras.constraints.MinMaxNorm(min_value=0.01, max_value=.99, rate=1.0, axis=0),
					kernel_initializer	= tf.keras.initializers.RandomUniform(minval=0.03, maxval=0.97, seed=None),
					bias_constraint		= tf.keras.constraints.MinMaxNorm(min_value=0.01, max_value=.99, rate=1.0, axis=0),
					bias_initializer	= tf.keras.initializers.Constant(value=0.5),
					):
		# I need to add contraints to each, since they can only be in range (0,1) note boundary exclusion
		# self.M_given_H = self.add_weight("given_H", shape=[int(input_shape[-1])], trainable=True)
		# self.M_given_nH = self.add_weight("given_nH", shape=[int(input_shape[-1])], trainable=True)
		
		# output calculations
		# self.H_bias = self.add_weight("H_bias", shape=[1], trainable=True)
		
		# -----------------------------------------
		# Generalized Tensor versions of the matrixes above (for each node)
		# https://www.tensorflow.org/api_docs/python/tf/repeat
		self.T_given_H = self.add_weight("given_H", shape=[self.num_outputs, int(input_shape[-1])], trainable=True, constraint=kernel_constraint, initializer=kernel_initializer )
		self.T_given_nH = self.add_weight("given_nH", shape=[self.num_outputs, int(input_shape[-1])], trainable=True, constraint=kernel_constraint, initializer=kernel_initializer )
		
		# output calculations
		self.H_bias = self.add_weight("H_bias", shape=[self.num_outputs], trainable=True, constraint=bias_constraint, initializer=bias_initializer )
	
	def call(self, inputs): # input [.1,.2,.3,.4,.5,.6]
		inputs = tf.convert_to_tensor(value=inputs, dtype=self.dtype)
		# We need to generalize math up one dimension to account for MULTIPLE output nodes, we need to use axixes
		# https://www.tensorflow.org/api_docs/python/tf/stack (create compound tensors, will also need to work with axis to make sure they stack properly)
		# https://www.tensorflow.org/api_docs/python/tf/ones (will need to create one's for each node instance)
		# https://www.tensorflow.org/api_docs/python/tf/math/multiply (element by element)
		# https://www.tensorflow.org/api_docs/python/tf/tensordot (this is for collapsing and multipleication across indicies)
		# https://www.tensorflow.org/api_docs/python/tf/math/reduce_prod (PI multiplication)
		
		# -----------------------------------------
		# Calculate probability matrix for set of output nodes
		# -----------------------------------------
		# Here is also where we can pre process prior node inputs, such as dealing with non (0,1) probability values
		#TBD
		
		# expand dimentions and copy so we have outputs dimension to pair up with weights
		tslice_Pw = tf.expand_dims(inputs, [1])
		tslice_Pw = tf.repeat(tslice_Pw, repeats=self.num_outputs, axis=1)
		
		# subparts of partial p(w|H) partials
		tslice_Pw_given_H_1 = tf.math.multiply(tslice_Pw, self.T_given_H)
		tslice_Pw_given_H_2 = tf.math.multiply(1.0-tslice_Pw, 1.0-self.T_given_H)
		t_partial_wH = tslice_Pw_given_H_1 + tslice_Pw_given_H_2
		
		# subparts of partial p(w|nH) partials
		tslice_Pw_given_nH_1 = tf.math.multiply(tslice_Pw, self.T_given_nH)
		tslice_Pw_given_nH_2 = tf.math.multiply(1.0-tslice_Pw, 1.0-self.T_given_nH)
		t_partial_wnH = tslice_Pw_given_nH_1 + tslice_Pw_given_nH_2
		
		# The following Suffers from having pi sum of % divided by pi sum% of %, pi sum of 128, and percentages... is SMALL, it's registered as zeros!
		# Instead we'll divide the tensors over each other.
		"""
		# Product pi-reduce product for each partial set for total P(w|nH) / P(w|nH), and multiply by bias
		t_total_wH = tf.math.reduce_prod(t_partial_wH, axis=-1)
		t_total_wnH = tf.math.reduce_prod(t_partial_wnH, axis=-1)
		
		# Calculate posterior bias
		t_post_bias_negative = tf.math.multiply(t_total_wnH, 1.0-self.H_bias)
		t_post_bias_positive = tf.math.multiply(t_total_wH, self.H_bias)
		
		# Final (1 / (1 + pi-ratios))
		return tf.divide( t_post_bias_positive, tf.add( t_post_bias_positive, t_post_bias_negative ) )
		"""
		
		# Instead we'll divide the tensors over each other, then pi sum.
		t_bias_ratio = tf.math.divide(t_partial_wnH, t_partial_wH)
		t_bias_ratio = tf.math.reduce_prod(t_bias_ratio, axis=-1)
		
		# Calculate posterior bias
		t_bias_ratio = tf.math.divide(t_bias_ratio, self.H_bias)
		t_bias_ratio = tf.math.multiply(t_bias_ratio, 1.0-self.H_bias)
		
		# Final (1 / (1 + pi-ratios))
		outputs = (1.0 / (1.0 + t_bias_ratio))
		
		# Losses - these are recursively called, and custom layers need to define losses
		self.add_loss(self.loss_fn(outputs, self.H_bias)) # though reduction is turned off, batches are feed in, and supplies a PER vector sum of losses, so a batch of 32, will have 32 outputs.
		
		return outputs # If we use normalization we dont need to worry about the other outputs, I may need to write my own if they dont have simple normalization
		# return tf.math.abs(outputs) # there's this small issue of small proabilites coming back with negative values


# =================================================
# Helper functions to compile complex tensor column slices into input
# =================================================
def generate_tensor_col_indexes(list_elements):
	i = 0
	while(i < len(list_elements) ):
		element = list_elements[i]
		
		if type(element) == str:
			chunks = element.split(':')
		
			start	= int(chunks[0])
			end		= int(chunks[1])
			
			assert start>= 0 # negative indexing not supported
			assert end	>= 0 # negative indexing not supported
			
			yield start, end
			
			# incrementation is handled independently
			i+=1
	
		elif type(element) == int:
			# possible continual string of elements or single element
			start = element
			end = start
			
			assert start>= 0 # negative indexing not supported
			assert end	>= 0 # negative indexing not supported
			
			# jump to next in list
			i+=1
			while(i < len(list_elements) ):
				element = list_elements[i]
				if type(element) == int and element == end+1:
					end+=1
					i+=1
				else:
					break
			
			# Determine if bounded or single number
			if start == end:
				yield start, None
			else:
				yield start, end+1

def calc_width_of_elements(list_elements):
	# Used in def build() to define layer inputs
	# Mainly affects layers that have to pre build.
	if list_elements == [] or list_elements == None:
		return None
	
	if type(list_elements) == int:
		assert list_elements >=0 # negative indexing not supported
		return 1
	
	count = 0
	for idx_start, idx_end in generate_tensor_col_indexes(list_elements):
		if idx_end == None:
			count+=1
		else:
			count+=(idx_end-idx_start)
	return count
	
def extract_tensor_cols(tensor, list_elements):
	if list_elements == [] or list_elements==None:
		return tensor
	
	list_tensor_slices = []
	
	for idx_start, idx_end in generate_tensor_col_indexes(list_elements):
		if idx_end:
			list_tensor_slices.append(tensor[:, idx_start:idx_end ])
		else:
			# only single slice
			assert idx_start < tensor.shape[1] # Must be contained within tensor
			list_tensor_slices.append(tensor[:, idx_start:idx_start+1 ])
	
	return tf.concat(list_tensor_slices,1)


# =================================================
# Hybrid Layer
# Similar to pass through, but enacts all layers on the same set of data
# True multivariance approach to layers
# =================================================
class Hybrid_Composite_Layer(tf.keras.layers.Layer):
	def __init__(self, *args_various_layers, partition=[], **kwargs):
		super().__init__(**kwargs)
		
		# Check to make sure partitioning matches number of nest layers
		if not ( len(partition) == 0 or len(partition) == len(args_various_layers)):
			raise ValueError("Length of partition must be empty_[] or equal to the number of input layers in composite.")
		
		self.len_arg_layers = len(args_various_layers)
		self.args_various_layers = args_various_layers
		self.partition = partition
		
	def add_loss(self, arg_layer):
		# optional to change BASED ON APPLICATION
		# https://github.com/tensorflow/tensorflow/blob/v2.4.1/tensorflow/python/keras/engine/base_layer.py#L1482-L1604	# def add_loss()
		# https://github.com/tensorflow/tensorflow/blob/v2.4.1/tensorflow/python/keras/engine/base_layer.py#L378		# self.losses
		
		# a tad unfortunte but will need to pass in reference to arg_layer here since I want to reduce the number of for-scans in the main call function
		# I think I'm starting to understand why all the abstraction of TF's source code
		sub_loss = arg_layer._losses
		super().add_loss(sub_loss)
		
		
	def build(self, input_shape):
		# nothing to really build individually
		# input shape is in form (None, #1th idx_number is only one that matters, #, #, #)
		
		# Pass All
		if self.partition == []:
			for arg_layer in self.args_various_layers:
				arg_layer.build(input_shape)
		
		# Handle individually
		else:
			for i in range(self.len_arg_layers):
				count = calc_width_of_elements(self.partition[i])
				if count == None:
					self.args_various_layers[i].build(input_shape)
				elif count == 0:
					self.args_various_layers[i].build((None,))
				else:
					self.args_various_layers[i].build((None,) + (count,) + input_shape[2:])

	def call(self, input):
		# Combine the outputs from each tensor
		# Upto programmer to ensure outputs are accepted between layers
		list_batch_output_tensor_slices = []
		
		if self.partition == []:
			for i in range(self.len_arg_layers):
				output_tensor_slice = self.args_various_layers[i].call(input)
				list_batch_output_tensor_slices.append(output_tensor_slice)
				
				# Update losses
				self.add_loss(self.args_various_layers[i])
		
		else:
			for i in range(self.len_arg_layers):
				sliced_input = extract_tensor_cols(input, self.partition[i])
				output_tensor_slice = self.args_various_layers[i].call(sliced_input)
				list_batch_output_tensor_slices.append(output_tensor_slice)
				
				# Update losses
				self.add_loss(self.args_various_layers[i])
		
		return tf.concat(list_batch_output_tensor_slices,1)

# =================================================
# Pass through, exactly how it sounds
# =================================================
class Acrylic_Layer(tf.keras.layers.Layer):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
	def build(self, *args, **kwargs):
		pass

	def call(self, input):
		return input

if __name__ == "__main__":
	import numpy as np
	nparray = np.array([.1, .2, .3, .4, .5, .6])
	test_tensor = tf.expand_dims(nparray,0)
	bayes_layer = Simple_Bayes_Layer(num_outputs=10)
	# builds layer as if used in model
	print(bayes_layer(test_tensor))
	print(bayes_layer._losses)
	print()
	# Call as if used in model evaulate
	# print(bayes_layer(test_tensor[0]))
	
	pass_layer = Acrylic_Layer()
	
	# Hybrid Layer, two layers in one
	hybrid_layer = Hybrid_Composite_Layer(bayes_layer, bayes_layer, pass_layer, partition=[[], [5,5,5,4,5,1], [1,2,3]])
	print(hybrid_layer(test_tensor))
	print(hybrid_layer._losses)
	print()
	