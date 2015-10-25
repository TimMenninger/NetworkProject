# Flow Class

from CS143Project.objects.packet import *
from CS143Project.misc.constants import *
from CS143Project.misc.conversion import *

# A global count of Packet that are sent
PACKET_COUNT = 0

class Flow:

	def __init__(self, the_flow_name, the_src, the_dest, the_size, the_start):
		'''
		Initialize an instance of Flow by intitializing its attributes.
		'''
		# Name of the Flow, each ID is a unique string (i.e. "F1")
		self.flow_name = the_flow_name

		# Hostname of source host, a string
		self.src = the_src

		# Hostname of destination host, a string
		self.dest = the_dest

		# Amount of data being sent, an int (in MB)
		self.size = the_size

		# Time the flow started (in sec), a float
		self.start = the_start

		# Integer representing the number of Packet in the Flow
		self.num_packets = 0

		# List of Packet being sent in the flow
		self.packets = []

		# Congestion control algorithm -- default algorithm is FAST-TCP
		self.algorithm = FLOW_FAST_TCP

	def get_num_packets(self):
		'''
		Computes and returns the number of Packet required to send for this 
		Flow.
		'''
		return MB_to_bits(self.size) // PACKET_DATA_SIZE

	def make_packets(self):
		'''
		Updates the 'num_packets' and 'packets' attributes.
		'''
		global PACKET_COUNT

		# Update the 'num_packets' attribute of this Flow to contain the 
		# number of Packet it is carrying
		self.num_packets = self.get_num_packets()

		# Fill up a list of the Packet being carried in the flow
		packets = []
		for i in range(self.num_packets):
			packet_id = str(PACKET_COUNT)
			p = Packet(packet_id, self, self.src, self.dest, Packet_Types.data, 
					   PACKET_DATA_SIZE, 1.0)
			packets.append(p)
			PACKET_COUNT += 1

		# Update the 'packets' attribute of this Flow to contiain a list of 
		# the Packet it is carrying
		self.packets = packets

	def print_contents(self, VERBOSE=False):
		'''
		Prints the contents of the flow to standard output.
		'''
		print("-" * 25)
		print("Flow Name: " + self.flow_name)
		print("Flow Source: " + self.src)
		print("Flow Destination: " + self.dest)
		print("Flow Size: " + str(self.size))
		print("Number of Packets: " + str(self.num_packets))
		if VERBOSE:
			print("Packets: ")
			for i, packet in zip(range(len(self.packets)), self.packets):
				print("  " + str(i + 1) + ". " + packet.ID)
		print("-" * 25)
