################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# link.py
#
# This contains the link class.  It has methods that enqueue packets then
# transmit them at calculated times.
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

# Import simulator so we can access global dictionaries.
import simulate as sim

# Import the constants and the conversion functions
import constants as ct
import conversion as cv


################################################################################
#                                                                              #
#                                   Link Class                                 #
#                                                                              #
################################################################################

class Link:

	def __init__(self, the_link_name, the_rate, the_delay, the_buffer_size, 
			     the_endpoints):
		'''
		Initialize an instance of Link by intitializing its attributes.
		'''
		# Name of the Link, each name is a unique string (i.e. "L1")
		self.link_name = the_link_name

		# Flag indicating whether Link is used/free in one direction, 
		# initially free
		self.in_use = ct.LINK_FREE
		
		# This is the index of the endpoint that data is flowing from.  If
		#	negative, there is no flow.
		self.flowing_from = -1

		# How fast the Router can send data (in MB/sec) 
		self.rate = the_rate

		# How much data can be stored in the buffer (in KB)
		self.buffer_size = the_buffer_size

		# Amount of time it takes to send Packet down link (in ms)
		self.delay = the_delay

		# Define the endpoints so we know how to define flow on this 
		# half-duplex link. Could be a Router or Host. 'the_endpoints' is 
		# passed in as a tuple of host_name and/or router_name
		self.end_points = the_endpoints

		# Router buffer which will hold the Packet before the
		# corresponding Packet are transmitted to Link 
		self.buffers = ([],[])
		
		# Packet currently on the link
		self.packets_carrying = []
		
		# Amount of data on link
		self.current_load = 0
		
		
#
# enqueue_packet
#
# Description:		This enqueues a packet onto the buffer at the end that the
#					packet was received from.
#
# Arguments:		self (Link)
#					argument_list ([string, string, string]) - A list of
#						arguments to the function, representing the endpoint
#						name, flow name and packet name, respectively.
#
# Return Values:	(integer) - A status integer that indicates the success or
#						lack thereof of the function.
#
# Shared Variables:	self.buffers (WRITE) - This function enqueues a packet onto
#						one of the buffers (potentially).
#					self.end_points (READ) - This is read to determine which
#						buffer should be altered, if any.
#					self.buffer_current_load (READ) - This is used to determine
#						if there is space on the buffer to enqueue a packet.
#					self.buffer_size (READ) - This is used to determine if there
#						is enough space on the buffer to enqueue a packet.
#
# Global Variables:	sim.packets (READ) - This dictionary is read from to get a
#						packet instance from its flow and packet names.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/22: Created function handle and docstring
#					2015/10/29: Filled function in.
#
		
	def enqueue_packet(self, argument_list):
		'''
		Adds a Packet to the Packet queue where it will wait to be transmitted
		along this link.
		'''
		
		# Unpack the argument list.
		[endpoint_name, flow_name, packet_name] = argument_list
		
		# For ease and code readability, extract the packet
		packet = sim.packets[(flow_name, packet_name)]
		
		# Figure out which endpoint this packet was received from.
		ep = 0
		if self.end_points[1] == endpoint_name:
			ep = 1
		
		# We want to check which endpoint the packet came from then put the
		#	packet in the appropriate buffer, but only if there is enough space
		#	in the buffer.
		if self.buffer_current_load[ep] + packet.size <= self.buffer_size:
			
			# Put the packet into the buffer and update its current load.
			self.buffers[ep].append((sim.network_now(), flow_name, packet_name))
			self.buffer_current_load[ep] += packet.size
			
			return ct.SUCCESS
			
		return ct.LINK_FULL
			
			
#
# dequeue_packet
#
# Description:		This dequeues a packet from the argued endpoint, thereby
#					removing it from the list, and returns it.
#
# Arguments:		self (Link)
#					argument_list ([string]) - A list containing the endpoint
#						index from which a packet should be dequeued.
#
# Return Values:	(string) - The flow name of the dequeued packet.
#					(string) - The name of the packet dequeued.
#
# Shared Variables:	self.buffers (WRITE) - One of the buffers in this loses a
#						packet.
#					self.buffer_current_load (WRITE) - Updated to reflect one
#						one fewer packet.
#
# Global Variables:	sim.packets (READ) - Read to get the packet instance from
#						the flow and packet names.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/22: Created function handle and docstring.
#					2015/10/29: Filled in function
#

	def dequeue_packet(self, argument_list):
		'''
		Dequeues a Packet from the Packet queue to transmit along this link.
		'''
		
		# Unpack the argument list.
		[endpoint] = argument_list
		
		# Dequeue the next packet from the buffer at the argued endpoint. Then,
		# 	update the load on the buffer.
		packet_desc = self.buffers[endpoint].pop()
		packet = sim.packets[(packet_desc[1], packet_desc[ep][2])]
		self.buffer_current_load[ep] -= packet.size
			
		# Return flow name and packet ID
		return packet_desc[1], packet_desc[2]
		
		
#
# enqueue_carry_event
#
# Description:		This decides which of the two buffers should have a packet
#					popped then sent down the link, then creates an event that
#					will pop from that buffer and send the packet.
#
# Arguments:		self (Link)
#
# Return Values:	ep (integer) - The index of the endpoint that contains the
#						next packet to be sent.
#					packet.flow_name (string) - The name of the flow the packet
#						is a part of.
#					packet.ID (string) - The ID of the packet to be sent.
#					time_delay (integer) - The amount of time it would take in
#						theory for this event to occur in real life.  This will
#						be the amount of time waited before executing the event.
#
# Shared Variables:	self.buffers (READ) - Read from to determine which buffer
#						is more worthy of sending a packet.
#					self.flowing_from (READ) - Read to determine which direction
#						the current flow is going.
#					self.rate (READ) - Used to determine the time delay before
#						the packet gets sent.
#					self.link_current_load (READ) - Used to determine the time
#						until the packet gets sent.
#
# Global Variables:	sim.packets (READ) - Used to get the packet instance from
#						the flow name and packet name.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/29: Created
#
		
	def enqueue_carry_event(self):
		'''
		Peeks at the next packet that is to be sent.  This returns which
		endpoint the packet is at, its flow and packet names and the time
		that must be waited until the link will be able to carry it to the
		other end as well as enqueues the appropriate event.
		'''
		
		# First, check which next packet should be sent next.  Currently, this
		#	is sending the oldest packet on either buffer.
		ep = 1
		if self.buffers[0][0] < self.buffers[1][0]:
			ep = 1
			
		# Put the packet in a container
		packet = sim.packets[(self.buffers[ep][1], self.buffers[ep][2])]
			
		
		# Using the amount of data on the link and the direction of flow,
		#	compute how much time until this packet can be sent.
		if self.flowing_from < 0:
			# There is no flow.  This can be carried immediately.
			time_delay = 0
		elif ep == self.flowing_from:
			# The packet must go in the direction of the current flow.  We just
			#	need to wait until there is enough space on the link.
			if self.rate - self.link_current_load >= packet.size:
				# Enough space to put packet on immediately
				time_delay = 0
			else:
				# Must wait for packet.size to open up on the link.  This time
				#	will be dependent on how much space we would go over if we
				#	were to put the packet on now.
				time_delay = ((packet.size + self.link_current_load) - self.rate) / self.rate
		else:
			# The packet must wait for flow to cease before being put onto the
			#	link.
			time_delay = self.link_current_load / self.rate
			
		# Create the next event.
		carry_event = e.Event(self, carry_packet, [ep])
			
		# Create the event for carrying the packet.
		heapq.heappush(sim.event_queue, (time_delay, carry_event))
		
		return ep, packet.flow_name, packet.ID, time_delay
		

#
# carry_packet
#
# Description:		Simulates the link carrying the packet.  This pops a packet
#					from the appropriate buffer and then changes the link
#					attributes to reflect the packet on the link and enqueues
#					an event for the other end to receive the packet.  Along
#					with this event, this calculates how much time should pass
#					before the reception is made.
#
# Arguments:		self (Link)
#					argument_list ([string]) - A list containing the index of
#						the endpoint that the packet is being sent from.
#
# Return Values:	None.
#
# Shared Variables:	self.packets_carrying (WRITE) - The packet that is being put
#						onto the link is added to this list.
#					self.link_current_load (WRITE) - Updated to reflect the new
#						load on the link.
#					self.delay (READ) - Used to determine the time that should
#						pass before the packet is received.
#
# Global Variables:	sim.packets (READ) - Used to get a packet instance from a
#						flow name and a packet name.
#
# Limitations:		None.
#
# Known Variables:	None.
#
# Revision History: 2015/10/29: Created
#

	def carry_packet(self, argument_list):
		'''
		Updates the Link to reflect that a packet is now in transmission.
		'''
		
		# Unpack the arguments
		[endpoint] = argument_list
		
		# Dequeue from the buffer at the argued endpoint.  This will give us
		#	the packet description we are looking for.
		flow_name, packet_name = self.dequeue_packet(endpoint)
		
		# Create a packet from the info dequeuing gave us.
		packet = sim.packets[(flow_name, packet_name)]
		
		# Put the packet into the link itself and update our size tracker.
		self.packets_carrying.append((flow_name, packet_name))
		self.link_current_load += packet.size
		
		# The next event will be this packet is received by the other endpoint,
		#	and that will be after the propagation delay.
		time_delay = packet.size / self.rate
		receive_event = e.Event(sim.endpoints[self.endpoints[endpoint]], receive_packet, [])
		
		# Enqueue the event.
		heapq.heappush(sim.event_queue, (time_delay, receive_event))
		
		
#
# print_contents
#
# Description:		Prints the attributes and their contained values.  This is
#					used mainly for debugging purposes.
#
# Arguments:		self (Link)
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
		Prints the status of all atributes of this Pink.
		'''
