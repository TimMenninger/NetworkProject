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
		
	
	def set_dest(dest_name):
		'''
		Sets the destination for this packet.
		'''
		self.dest = dest_name
		
		
	def set_data(data):
		'''
		Sets the data for this packet to send.
		'''
		# Check if data is less than packet size?
		self.data = data
		
		
	def set_src(src):
		'''
		Sets the source attribute of the packet.
		'''
		self.src = src
		
		
	def set_time(time = -1):
		'''
		Sets the timestamp of the packet.  If nothing is argued (or the argument is negative),
		then it is set to the current time.
		'''
		if time >= 0:
			self.time = time
		else:
			self.time = now()
			
			
	def set_ID(the_id = -1):
		'''
		Sets the ID of the packet.  If no ID is given or it is negative, then the next available
		ID for the packet's flow is taken.
		'''
		if the_id >= 0:
			self.ID = the_id
		else:
			self.ID = self.flow.create_packet_ID()


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
