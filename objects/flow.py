#
# flow.py
#
# This contains the flow class.  The flow class acts as "God" for the network
# simulation by telling hosts when to and when not to send packets based on
# congestion control algorithms it runs.
#

from CS143Project.objects.packet import *
from CS143Project.objects.link import *
from CS143Project.objects.router import *
from CS143Project.objects.simulator import *
from CS143Project.objects.event import *
from CS143Project.objects.host import *
from CS143Project.misc.constants import *
from CS143Project.misc.conversion import *

# A global count of Packets that are sent
packet_count = 0

class Flow:

	def __init__(self, the_flow_name, the_src, the_dest, the_size, the_time):
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

		# Congestion control algorithm
		self.algorithm = None

		# Window size as computed 
		self.window_size = 0

		# List of packets in the network
		self.packets_in_flight = []
		
		# Keep track of what packet IDs have been given out and which ID should
		#	be the next one when requested.
		self.next_packet_ID = 0
		
		# Remember the start time.
		self.start_time = the_time
		
		
	def set_algorithm(algorithm):
		'''
		Sets the algorithm we are using for congestion control.
		'''
		
		self.algorithm = algorithm
		
		
	def create_packet_ID():
		'''
		Returns an unused ID for a packet.
		'''
		
		# Increment the ID for the next call.
		self.next_packet_ID += 1
		
		# Return the old one.
		return self.next_packet_ID - 1
		

	def print_contents():
		'''
		For debugging use. Print out the contents of the Flow.
		'''



