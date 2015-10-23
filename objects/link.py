# Link Class

class Link:

	def __init__(self, the_link_name, is_free_in_dir_A, is_free_in_dir_B,  
				 the_capacity, the_delay, the_buffer):
		'''
		Initialize an instance of Link by intitializing its attributes.
		'''

		# Boolean flag indicating whether Link is free in one direction
		self.free_in_dir_A = is_free_in_dir_A

		# Boolean flag indicating whether Link is free in other direction
		self.free_in_dir_B = is_free_in_dir_B

		# Name of the Link, each name is a unique string (i.e. "L1")
		self.link_name = the_link_name

		# How fast the Router can send data (in MB/sec) 
		self.capacity = the_capacity

		# Amount of time it takes to send Packet down link (in ms)
		self.delay = the_delay

	def print_contents(self):
		'''
		Prints the contents of the Link to standard output.
		'''
		print("-" * 25)
		print("Link Name: " + self.link_name)
		print("Link Free (Direction A): " + str(self.free_in_dir_A))
		print("Link Free (Direction B): " + str(self.free_in_dir_B))
		print("Capacity: " + str(self.capacity))
		print("Delay: " + str(self.delay))
		print("Buffer: " + str(self.buffer))
		print("-" * 25)