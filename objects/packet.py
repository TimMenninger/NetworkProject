#
# packet.py
#
# This contains the packet class, which is the data structure that represents
# the actual data being transmitted in the simulated network.
#

from CS143Project.objects.link import *
from CS143Project.objects.flow import *
from CS143Project.objects.router import *
from CS143Project.objects.simulator import *
from CS143Project.objects.event import *
from CS143Project.objects.host import *
from CS143Project.misc.constants import *

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


