#
# flow.py
#
# This contains the flow class.  The flow class acts as "God" for the network
# simulation by telling hosts when to and when not to send packets based on
# congestion control algorithms it runs.
#

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import the constants and the conversion functions
import constants as ct
import conversion as cv

# A global count of Packets that are sent
packet_count = 0

class Flow:

	def __init__(self, the_flow_name, the_src, the_dest, the_size):
		'''
		Initialize an instance of Flow by intitializing its attributes.
		'''
		# Name of the Flow, each ID is a unique string (i.e. "F1")
		self.flow_name = the_flow_name

		# host_name of source Host, a string
		self.src = the_src

		# host_name of destination Host, a string
		self.dest = the_dest

		# Amount of data being sent, an int (in MB)
		self.size = the_size

		# Window size as computed 
		self.window_size = 0

		# List of packets in the network
		self.packets_in_flight = []
		
		# The last used packet ID for this flow.  The first packet ID should be 0, so a
		#	value of -1 implies no packets have been created yet.
		self.last_packet_ID = -1

	def set_algorithm(algorithm):
		'''
		Sets the algorithm we are using for congestion control.
		'''
		self.algorithm = algorithm
		
	def create_packet_ID():
		'''
		Returns an unused ID for a packet.
		'''
		# Increment the ID to get the next unused packet ID.
		self.next_packet_ID += 1
		
		# Return the ID.
		return self.next_packet_ID
		
	def print_contents():
		'''
		For debugging use. Print out the contents of the Flow.
		'''
