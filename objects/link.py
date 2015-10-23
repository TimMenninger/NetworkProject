# Link Class

from CS143Project.misc.constants import *

class Link:

	def __init__(self, the_link_name, the_capacity, the_delay, the_buffer):
		'''
		Initialize an instance of Link by intitializing its attributes.
		'''

		# Name of the Link, each name is a unique string (i.e. "L1")
		self.link_name = the_link_name

		# Flag indicating whether Link is used/free in one direction
		#     LINK_USED_HIGH -> Used in direction of higher Host/Router name
		#     LINK_USED_LOW -> Used in direction of lower Host/Router name
		#     LINK_FREE -> Free in both directions
		self.in_use = LINK_FREE

		# How fast the Router can send data (in MB/sec) 
		self.capacity = the_capacity

		# Amount of time it takes to send Packet down link (in ms)
		self.delay = the_delay

	def print_contents(self):
		'''
		Prints the contents of the Link to standard output.
		'''
		print("-" * 25)
		print("Link Name: " + self.link_name)
		print("Link: " + str(self.in_use))
		print("Capacity: " + str(self.capacity))
		print("Delay: " + str(self.delay))
		print("-" * 25)
