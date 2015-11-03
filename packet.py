################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# packet.py
#
# This contains the packet class, which is the data structure that represents
# the actual data being transmitted in the simulated network.
#
################################################################################






################################################################################
#                                                                              #
#                               Imported Modules                               #
#                                                                              #
################################################################################

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

# Import the simulator so we can access events and time.
import simulate as sim


################################################################################
#                                                                              #
#                                  Packet Class                                #
#                                                                              #
################################################################################

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
		
		# Keep track of data contained in this packet (only relevant for routing packets
		#	at the moment)
		self.data = None
		
		
#
# set_dest
#
# Description:		Sets the destination of the packet.
#
# Arguments:		self (Packet)
#					dest_name (string) - The name of the destination of this packet.
#
# Return Values:	None.
#
# Shared Variables:	self.dest (WRITE) - Updated according to arguments.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#
	
	def set_dest(self, dest_name):
		'''
		Sets the destination for this packet.
		'''
		self.dest = dest_name
		
		
#
# set_data
#
# Description:		Sets the data of the packet.
#
# Arguments:		self (Packet)
#					data (Any) - The data carried by this packet.
#
# Return Values:	None.
#
# Shared Variables:	self.data (WRITE) - Updated according to arguments.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#
	
	def set_data(self, data):
		'''
		Sets the data for this packet to send.
		'''
		# Check if data is less than packet size?
		self.data = data
		
		
#
# set_src
#
# Description:		Sets the destination of the packet.
#
# Arguments:		self (Packet)
#					src (string) - The name of the source of this packet.
#
# Return Values:	None.
#
# Shared Variables:	self.src (WRITE) - Updated according to arguments.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#
	
	def set_src(self, src):
		'''
		Sets the source attribute of the packet.
		'''
		self.src = src
		
		
#
# set_time
#
# Description:		Sets the time in ms since the start of the network that the
#					packet was created.  If this is negative, it is sent to the
#					current time in the network.
#
# Arguments:		self (Packet)
#					time (integer) - The time this packet is being sent.  If no
#						argument given, default is -1.
#
# Return Values:	None.
#
# Shared Variables:	self.time (WRITE) - Updated according to arguments.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#
	
	def set_time(self, time = -1):
		'''
		Sets the timestamp of the packet.  If nothing is argued (or the argument is negative),
		then it is set to the current time.
		'''
		if time >= 0:
			self.time = time
		else:
			self.time = sim.network_now()
		
		
#
# set_ID
#
# Description:		Sets the destination of the packet.
#
# Arguments:		self (Packet)
#					the_id (string) - The new ID for this packet.
#
# Return Values:	None.
#
# Shared Variables:	self.ID (WRITE) - Updated according to arguments.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#
	
	def set_ID(self, the_id = -1):
		'''
		Sets the ID of the packet.  If no ID is given or it is negative, then the next available
		ID for the packet's flow is taken.
		'''
		if the_id >= 0:
			self.ID = the_id
		else:
			self.ID = self.flow.create_packet_ID()
		
#
# print_contents
#
# Description:		Prints the attributes and their contained values.  This is
#					used mainly for debugging purposes.
#
# Arguments:		self (Packet)
#
# Return Values:	None.
#
# Shared Variables: None.
#
# Global Variables: None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/??: Created function handle
#
		
	def print_contents(self):
		'''
		Prints statistics about this Packet.
		'''
