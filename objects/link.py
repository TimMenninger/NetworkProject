# Link Class

class Link:

	def __init__(self, the_link_name, the_capacity, the_delay, the_buffer):
		'''
		Initialize an instance of Link by intitializing its attributes.
		'''

		# Name of the Link, each name is a unique string (i.e. "L1")
		self.link_name = the_link_name

		# How fast the Router can send data (in MB/sec) 
		self.capacity = the_capacity

		# Amount of time it takes to send Packet down link (in ms)
		self.delay = the_delay

		# Amount of space available on either end of link to store Packet that 
		# cannot travel down the link at a given time (in KB) 
		self.buffer = the_buffer

	def print_contents(self):
		'''
		Prints the contents of the Link to standard output.
		'''
		print("-" * 25)
		print("Link Name: " + self.link_name)
		print("Capacity: " + str(self.capacity))
		print("Delay: " + str(self.delay))
		print("Buffer: " + str(self.buffer))
		print("-" * 25)