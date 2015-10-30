#
# packet.py
#
# This contains the packet class, which is the data structure that represents
# the actual data being transmitted in the simulated network.
#

# Import network objects
import simulator, link, flow, router, event, host

class Packet:

	def __init__(self, the_ID, the_flow, the_src, the_dest, the_type, the_size, 
		         the_time):
		'''
		Initialize an instance of Packet by intitializing its attributes.
		'''
		# ID of the Link, each ID is a unique string (i.e. "P1")
		self.ID = the_ID

		# Flow that the Packet belongs to 
		# Gives access to source and destination, uniquely identifies Packet
		self.flow = the_flow

		# Host/Router sending the Packet
		self.src = the_src

		# Host/Router to receive the Packet
		self.dest = the_dest

		# Constant representing the type of Packet being sent 
		# PACKET_DATA, PACKET_ACK, PACKET_ROUTING
		self.type = the_type

		# Integer representing the size of the Packet, dependent on its type
		# PACKET_DATA_SIZE, PACKET_ACK_SIZE, or PACKET_ROUTING_SIZE
		self.size = the_size


	def print_contents():
		'''
		Prints statistics about this Packet.
		'''

	# def print_contents(self):
	# 	'''
	# 	Prints the contents of the Packet to standard output.
	# 	'''
	# 	print("-" * 25)
	# 	print("Packet ID: " + self.ID)
	# 	print("Time: " + self.time)
	# 	print("Flow: " + self.flow.flow_name)
	# 	print("Source: " + self.src)
	# 	print("Destination: " + self.dest)
	# 	print("Type: " + self.type.name)
	# 	print("Size: " + str(self.size))
	# 	print("-" * 25)
