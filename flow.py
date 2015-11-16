################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# flow.py
#
# This contains the flow class.  The flow is an abstract concept used to 
# simplify the notion of sending packets from a source to a destination.  
# Congestion control algorithms determine when and how many packets are sent 
# at any given time during the simulation.
#
################################################################################


# Notes from meeting with Ritty
# Flow: 
#    window_size = 16
#    packets_in_network = k

# if k < 16:
#       send packet 
#       k++

# Every time a packet is sent, a retransmission timeout event must be spurred
#     timeout after 2 * (round trip time)


# Need a singleton logger class
# logger.log("L1", "Drop", "Time")
# each keyword indicates which log file it's being logged to
# separate csv log file for packets dropped
# separate csv log file for throughput
# separate csv log file for window size


################################################################################
#                                                                              #
#                               Imported Modules                               #
#                                                                              #
################################################################################

# So we can use command line arguments.
import sys

# Import network objects
import packet as p
import link as l
import router as r
import host as h
import event as e

# Import the constants and the conversion functions
import constants as ct
import conversion as cv

# Import utility functions
import utility as u

# Import functions to carry out the simulation
sim  = sys.modules['__main__']

# Import the config parser
import config_parser as cp

# Import the queue Python package for the link buffers which are FIFO
import queue

# Import heapq library so we can use it for our events.
import heapq 

################################################################################
#                                                                              #
#                                   Flow Class                                 #
#                                                                              #
################################################################################

class Flow:

	def __init__(self, the_flow_name, the_src, the_dest, the_size, the_start_time):
		'''
		Initialize an instance of Flow by intitializing its attributes.
		'''
		# Name of the Flow, each ID is a unique string (i.e. "F1")
		self.flow_name = the_flow_name

		# host_name of source Host, a string
		self.src = the_src

		# host_name of destination Host, a string
		self.dest = the_dest

		# Amount of data being sent, an int (in bytes)
		self.size = cv.MB_to_bytes(the_size)

		# Window size as computed.
		self.window_size = 1
		
		# The time the flow is starting.
		self.start_time = the_start_time
		
		# The packets that must be sent.
		self.packets_to_send = []
		
		# The packets that are in flight.
		self.packets_in_flight = []
		
		# Every number less than this has been used as an ID.
		self.next_available_ID = 0
		
		# The next chronological packet that the dest expects from the src.
		self.expecting = 0
		
		# The next chronological packet the source is looking to receive
		#	ack for.
		self.to_complete = 0
		
		
	def create_packet_ID(self):
		'''
		Returns an ID that is not currently in use by any other packet.
		'''
		self.next_available_ID += 1
		return str(self.next_available_ID - 1)
		
		
	def start_flow(self, unused_list):
		'''
		Starts the flow by creating all of the packets to send then starting to
		send them.
		'''
		# Calculate the number of packets we need to send all of the data
		num_packets = int(self.size / ct.PACKET_DATA_SIZE) + 1
		
		# Create all of the packets.
		for i in range(num_packets):
			# First, create a packet.
			new_pkt = p.Packet(self.create_packet_ID(), self.flow_name, 
							   self.src, self.dest,
							   ct.PACKET_DATA, ct.PACKET_DATA_SIZE)
							   
			# Set the data of the packet to be its "chronological" number.
			new_pkt.set_data(i)
							   
			# Put the packet into the heapqueue.
			heapq.heappush(self.packets_to_send, (i, new_pkt))
			
			# Put the packet into the global dictionary of packets.
			sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
			
		# Update the flow so that we have packets in motion.
		self.update_flow()
		
		
	def resend_inflight_packets(self):
		'''
		This remakes and resends all packets that are currently in flight.
		'''
		# Create a new queue of packets in flight
		old_flight = self.packets_in_flight[:]
		self.packets_in_flight = []
		
		# Remove all of the packets in flight, make a new packet out of them
		#	and resend.  We are making a new packet so it has a new ID.  If
		#	we didn't do this, we wouldn't be able to index packets in the
		#	dictionary anymore, which is important because the timestamps will
		#	be different.
		while len(old_flight) > 0:
			# Remove an element and make a new packet from it.
			(old_num, old_pkt) = heapq.heappop(old_flight)
			
			# Create a new packet from it but with a new ID.
			new_pkt = p.Packet(self.create_packet_ID(), self.flow_name,
							   old_pkt.src, old_pkt.dest, old_pkt.type,
							   old_pkt.size)
			new_pkt.set_data(old_pkt.data)
			
			# Add it to the new queue of packets.
			heapq.heappush(self.packets_in_flight, (new_pkt.data, new_pkt))
			
			# Add it to the dictionary of packets.
			sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
			
			# Create an event to send this packet.
			send_event = e.Event(new_pkt.src, 'send_packet', [new_pkt])
			sim.enqueue_event(sim.network_now(), send_event)
			
			
	def update_flow(self):
		'''
		Updates the window size according to congestion and the packets in
		flight according to window size.
		'''
		# If there are no packets to send, the flow is done.
		if len(self.packets_to_send) == 0:
			return
			
		while len(self.packets_in_flight) < self.window_size:
			# Get a packet from the list of packets to send.
			(pkt_num, next_pkt) = heapq.heappop(self.packets_to_send)

			# Put it in flight.
			heapq.heappush(self.packets_in_flight, (pkt_num, next_pkt))
			
			# Tell the host to send the packet by creating an event for it.
			send_time = sim.network_now() + ct.TIME_BIT
			send_event = e.Event(self.src, 'send_packet', [next_pkt])
			sim.enqueue_event(send_time, send_event)
			
		
