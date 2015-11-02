#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# router.py
#
# This contains the router class, which contains methods for simulating the
# routers in the network.  It also contains methods which periodically run
# a Bellman-Ford algorithm to build its own routing table.
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

class Router:

	def __init__(self, the_router_name):
		'''
		Initialize an instance of Router by intitializing its attributes.
		'''
		# Name of the Router, each name is a unique string (i.e., "R1")
		self.router_name = the_router_name

		# List of Link that are attached to this Router
		self.links = []

		# Python dictionary - contains destination hostnames as keys and Link
		# names as values.
		self.routing_tables = ({}, {})
		
		# Keep track of the distances so we know how to update the routing tables when necessary.
		self.routing_dists = {}
		
		# The index of the routing table in use.
		self.using_table = 0
		
		
	def add_link(link_name):
		'''
		Adds a link to the router.
		'''
		self.links.append(link_name)
		

	def set_routing_table():
		'''
		Sets the routing table for this Router.
		'''
		
	def switch_routing_table():
		# Get the index of the table not in use.
		other_table = (self.using_table + 1) % 2
		
		# Make sure if there was an entry in the routing table before that there
		#	is still an entry in the routing table.
		for key in self.routing_tables[self.using_table]:
			if key not in self.routing_tables[other_table]:
				self.routing_tables[other_table][key] = self.routing_tables[self.using_table][key]
				
		# After populating the new table, clear the current one so we can refill it.
		self.routing_tables[using_table] = {}
		self.routing_dists = {}
				
		# Update the index of which routing table is in use.
		self.using_table = other_table
		
	def create_config_packet():
		'''
		Creates a special configuration packet that, when received by other routers,
		is understood as a configuration packet and can be used to set up routing
		tables.
		'''
		#
		# PSEUDOCODE:
		#
		# config_pkt = p.Packet(None, FLOW, self.router_name, None,
		#		      PACKET_ROUTING, PACKET_ROUTING_SIZE, None)
		#
		# config_pkt.set_data(self.router_name, now())
		#
		# return config_pkt
		#
		
		
	def send_config_packet(config_pkt):
		'''
		Creates a special configuration packet that, when received by other routers,
		is understood as a configuration packet.
		'''
		
		#
		# Proposed pseudocode for this (bellman-ford):
		#	In this, we are going to initiate the process here with a specially
		# formatted packet that routers will understand as the "configuration" packet.
		#
		# 	We will send a packet with the form [origin_router_name, distance_to] where
		# origin_router is the router sending the first "configuration" packet and 
		# distance_to is the total weight from the origin to this particular router.
		# Clearly, when sending this first packet, we will have [self.router_name, 0].
		# When receiving this packet, receive_packet should call parse_config_packet.  Refer
		# to that function for the rest of the computation involved with configuring the
		# routing tables.
		#
		#	For this to work, we want to keep track of the shortest distance to each
		# router from this one.  Initialize all these values to be infinity.
		#
		#
		#
		# PSEUDOCODE:
		#
		# for link in self.links:
		#	config_pkt.set_time()
		#	config_pkt.set_ID()
		#	config_pkt.set_src(self.router_name)
		#	config_pkt.set_dest(link.link_name)
		#	send_packet(config_pkt)
		#
		
	def parse_config_packet(config_pkt):
		'''
		Receives a configuration packet and updates the routing table if any new, useful
		information is learned from it.
		'''
		
		#
		# Proposed pseudocode (continuation of send_config_packet):
		#
		#	This will be called when the router receives a config packet, which is in
		# the format [origin_router, distance_to].  The origin_router was the router which
		# initially sent this packet, and distance_to is the distance from the origin router
		# to this router using whatever path it used.
		#
		# Pseudocode:
		#	receive packet
		#	if distance_to < [previously thought shortest distance to origin router]:
		#		update routing table for origin_router with router that sent packet
		#		send [origin_router, distance_to] to all links besides one it came on
		#
		#
		# All we need is some way of quantifying distance_to.  Maybe it's time, maybe not, I
		# don't know yet...
		#
		# This will work because every router will do this.  If the routers 
		# are all connected, then by relaying the messages whenever the distance is improved,
		# all routers will get a packet to all other routers at least once.  We only need to
		# continue propagation if it is improved because if not, then the time that the better
		# packet came through, that was propagated.  Therefore, we know this process will
		# terminate.
		#
		#
		#
		#
		#
		# PSEUDOCODE:
		#
		# other_table = (self.using_table + 1) % 2
		#
		# if config_pkt.data[0] not in self.routing_tables[other_table] OR
		#    routing_dists[config_pkt.data[0]] > config_pkt.data[1]:
		#	self.routing_tables[other_table][config_pkt.data[0]] = config_pkt.src
		#	self.routing_dists[config_pkt.data[0]] = config_pkt.data[1]
		#	send_config_packet(config_pkt)
		#
		#

	def send_packet(packet):
		'''
		Sends a packet from this Router to a particular destination using a
		specific link connected to this Router.
		'''

	def receive_packet():
		'''
		Receives a packet from a link and parses it.
		'''

	def print_contents():
		'''
		Prints attribute values for this Router.
		'''






	# def print_contents(self):
	# 	'''
	# 	Prints the contents of the Router to standard output.
	# 	'''
	# 	print("-" * 25)
	# 	print("Router Name: " + self.router_name)
	# 	print("Routing Table: ")
	# 	for dest_host_name, link_name in zip(self.routing_table.keys(), 
	# 										 self.routing_table.values()):
	# 		print("  " + dest_host_name + " --> " + link_name)
	# 	print("Links: ")
	# 	for i, link_name in zip(range(len(self.links)), self.links):
	# 		print("  " + str(i + 1) + ". " + link_name)
	# 	print("Packets in Buffer:\n")
	# 	for i, packet in enumerate(packet_buffer):
	# 		print(i + ":\n")
	# 		packet.print_contents
	# 		print("\n")
	# 	print("-" * 25)


