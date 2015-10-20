# Flow Class

class Flow:

	def __init__(self, the_ID, the_src, the_dest, the_size, the_start, 
				 the_packets):
		'''
		Initialize an instance of Flow by intitializing its attributes.
		'''

		# ID of the Flow, each ID is a unique string (i.e. "F1")
		self.ID = the_ID

		# Hostname of source host, a string
		self.src = the_src

		# Hostname of destination host, a string
		self.dest = the_dest

		# Amount of data being sent, an int (in MB)
		self.size = the_size

		# Time the flow started (in sec), a float
		self.start = the_start

		# List of string ID corresponding to the Packet being sent in the flow
		self.packets = the_packets