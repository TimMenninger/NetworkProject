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

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import simulator so we can access global dictionaries.
import simulator as sim

# Import the constants and the conversion functions
import constants as ct
import conversion as cv

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
		
	def enqueue_packet(argument_list):
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
			self.buffers[ep].append((now(), flow_name, packet_name))
			self.buffer_current_load[ep] += packet.size
			

	def dequeue_packet(argument_list):
		'''
		Dequeues a Packet from the Packet queue to transmit along this link.
		'''
		
		# Unpack the argument list.
		[endpoint] = argument_list
		
		# Dequeue the next packet from the buffer at the argued endpoint. Then,
		# 	update the load on the buffer.
		packet_desc = self.buffers.pop()
		packet = sim.packets[(packet_desc[1], packet_desc[ep][2])]
		self.buffer_current_load[ep] -= packet.size
			
		return packet_desc[1], packet_desc[2]
		
		
	def enqueue_carry_event():
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
			if self.rate - self.buffer_current_load >= packet.size:
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
		carry_event = Event(self, carry_packet, [ep])
			
		# Create the event for carrying the packet.
		event_queue.append(time_delay, carry_event)
		
		return ep, packet.flow_name, packet.ID, time_delay
		

	def carry_packet(argument_list):
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
		receive_event = Event(sim.endpoints[self.endpoints[endpoint]], receive_packet, [])
		
		# Enqueue the event.
		event_queue.append((time_delay, receive_event))
		
		# Compute how much time "God" must wait to tell the link to load another
		#	packet onto the link.
		next_packet_delay = packet.size * self.delay
		
		return next_packet_delay
		

	def print_contents():
		'''
		Prints the status of all atributes of this Pink.
		'''
