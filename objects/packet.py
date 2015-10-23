# Packet Class

from enum import Enum

DATA_PACKET_SIZE = 1024 # As per the project specifications
ACK_PACKET_SIZE = 64 # In bits
ROUTING_PACKET_SIZE = 64 # In bits

class Packet_Types(Enum):
	data = 1
	ack = 2
	routing = 3

class Packet:

	def __init__(self, the_ID, the_flow, the_src, the_dest, the_type, the_size, the_time):
		'''
		Initialize an instance of Packet by intitializing its attributes.
		'''

		# ID of the Link, each ID is a unique string (i.e. "L1")
		self.ID = the_ID

		# Flow that the Packet belongs to (gives access to source and 
		# destination)
		self.flow = the_flow

		# Name of the Host sending the Packet
		self.src = the_src

		# Name of the Host to receive the Packet
		self.dest = the_dest

		# Enum representing the type of Packet being sent (data, ack, routing)
		self.type = the_type

		# Integer representing the size of the Packet, dependent on its type
		# Will be either DATA_PACKET_SIZE, ACK_PACKET_SIZE, OR 
		# ROUTING_PACKET_SIZE
		self.size = the_size
		
		# Update the time that the packet was sent
		self.time = the_time

	def print_contents(self):
		'''
		Prints the contents of the Packet to standard output.
		'''
		print("-" * 25)
		print("Packet ID: " + self.ID)
		print("Time: " + self.time)
		print("Flow: " + self.flow.flow_name)
		print("Source: " + self.src)
		print("Destination: " + self.dest)
		print("Type: " + self.type.name)
		print("Size: " + str(self.size))
		print("-" * 25)
