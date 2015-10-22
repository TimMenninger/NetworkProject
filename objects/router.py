# Router class

class Router:

	def __init__(self, the_router_name, the_routing_table, the_links):
		'''
		Initialize an instance of Router by intitializing its attributes.
		'''

		# Name of the Router, each name is a unique string (i.e., "R1")
		self.router_name = the_router_name
		
		# Python dictionary - contains destination hostnames as keys and Link
		# names as values
		self.routing_table = the_routing_table

		# List of string names corresponding to the Link that are attached to 
		# this Router
		self.links = the_links

	def print_contents(self):
		'''
		Prints the contents of the Router to standard output.
		'''
		print("-" * 25)
		print("Router Name: " + self.router_name)
		print("Routing Table: ")
		for dest_host_name, link_name in zip(self.routing_table.keys(), 
											 self.routing_table.values()):
			print("  " + dest_host_name + " --> " + link_name)
		print("Links: ")
		for i, link_name in zip(range(len(self.links)), self.links):
			print("  " + str(i + 1) + ". " + link_name)
		print("-" * 25)