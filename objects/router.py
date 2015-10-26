# Router class

class Router:

	def __init__(self, the_router_name, the_links):
		'''
		Initialize an instance of Router by intitializing its attributes.
		'''
		# Name of the Router, each name is a unique string (i.e., "R1")
		self.router_name = the_router_name

		# List of Link that are attached to this Router
		self.links = the_links

		# Python dictionary - contains destination hostnames as keys and Link
		# names as values
		self.routing_table = {}

	def set_routing_table():
		'''
		Sets the routing table for this Router.
		'''

	def send_packet():
		'''
		Sends a packet from this Router to a particular destination using a
		specific link connected to this Router.
		'''

	def receive_packet():
		'''
		Receives a packet from a link and parses it.
		'''

	def print_contents():
		'''
		Prints attribute values for this Router.
		'''








	# def print_contents(self):
	# 	'''
	# 	Prints the contents of the Router to standard output.
	# 	'''
	# 	print("-" * 25)
	# 	print("Router Name: " + self.router_name)
	# 	print("Routing Table: ")
	# 	for dest_host_name, link_name in zip(self.routing_table.keys(), 
	# 										 self.routing_table.values()):
	# 		print("  " + dest_host_name + " --> " + link_name)
	# 	print("Links: ")
	# 	for i, link_name in zip(range(len(self.links)), self.links):
	# 		print("  " + str(i + 1) + ". " + link_name)
	# 	print("Packets in Buffer:\n")
	# 	for i, packet in enumerate(packet_buffer):
	# 		print(i + ":\n")
	# 		packet.print_contents
	# 		print("\n")
	# 	print("-" * 25)


