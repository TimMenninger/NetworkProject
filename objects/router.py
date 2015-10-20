# Router class

class Router:

	def __init__(self, the_ID, the_routing_table):
		'''
		Initialize an instance of Router by intitializing its attributes.
		'''

		# ID of the Router, each ID is a unique string (i.e., "R1")
		self.ID = the_ID
		
		# python dictionary - contains destination hostnames as keys and Link
		# as values
		self.routing_table = the_routing_table