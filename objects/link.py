# Link Class

class Link:

	def __init__(self, the_ID, the_capacity, the_delay, the_buffer):
		'''
		Initialize an instance of Link by intitializing its attributes.
		'''

		# ID of the Link, each ID is a unique string (i.e. "L1")
		self.ID = the_ID

		# How fast the Router can send data (in MB/sec) 
		self.capacity = the_capacity

		# Amount of time it takes to send Packet down link (in ms)
		self.delay = the_delay

		# Amount of space available on either end of link to store Packet that 
		# cannot travel down the link at a given time (in KB) 
		self.buffer = the_buffer