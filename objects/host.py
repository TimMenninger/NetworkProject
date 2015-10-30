#
# host.py
#
# This contains the host class, which is the object used to represent a
# host in the network.
#

from CS143Project.objects.packet import *
from CS143Project.objects.link import *
from CS143Project.objects.flow import *
from CS143Project.objects.router import *
from CS143Project.objects.simulator import *
from CS143Project.objects.event import *


class Host:

	def __init__(self, the_host_name):
		''' 
		Initialize an instance of Host by intitializing its attributes.
		'''
		# Name of the host, each hostname is unique string (i.e., "H1")
		self.host_name = the_host_name
		
		# The link_name representing the Link to this Host
		self.link = []
		
		
	def add_link(link_name):
		'''
		Alters the 'links' attribute of the Host to reflect the link
		connecting the Host to the network.
		'''
		self.link = link_name
		

	def send_packet(argument_list):
		'''
		Sends a Packet from this Host to a particular destination.  Then, it 
		adds the appropriate subsequent event to the Simulator event queue.
		'''
		
		# Unpack the argument list.
		[flow_name, packet_name] = argument_list
		
		# Enqueue the packet on the link.
		self.link.enqueue_packet(self.host_name, flow_name, packet_name)
		

	def receive_packet(argument_list):
		'''
		Receives a Packet from a Link.  Then, it adds the appropriate event to 
		the Simulator event queue.
		'''
		# Unpack the argument list.
		[flow_name, packet_name] = argument_list
		
		# Create a packet for the argued description.
		packet = dict_packets[(flow_name, packet_name)]
		
		if packet.type == PACKET_DATA:
			# Create acknowledgement packet.
			ack_packet = Packet(flow.create_ID(), packet.flow,
								self.host_name, packet.src, PACKET_ACK,
								PACKET_ACK_SIZE, now())
			# Compute how long the host must wait to send acknowledgement.
			time_delay = 0
			# Create an event to send this packet.
			send_ack_event = Event(self, send_packet, [ack_packet.flow, ack_packet.ID])
		

	def print_contents():
		'''
		Prints what is contained in all of the attributes of this Host.
		'''

