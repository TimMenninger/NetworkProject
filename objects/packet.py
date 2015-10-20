# Packet Class

class Packet:

	def __init__(self, the_ID, the_flow, the_payload):
		'''
		Initialize an instance of Packet by intitializing its attributes.
		'''

		# ID of the Link, each ID is a unique string (i.e. "L1")
		self.ID = the_ID

		# ID of the Flow that the Packet belongs to (gives access to source and 
		# destination)
		self.flow = the_flow

		# Actual data being sent or the acknowledgement
		self.payload = the_payload
