#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# simulate.py
#
# This module contains functions that are required to carry out a network 
# simulation.
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

# Import utility functions
import utility as u

# Import functions to carry out the simulation
import simulate as s

# Import the config parser
import config_parser as cp


# Global variables containing objects in the network as well as events.
packets 	= {} # Packets in the system
links 		= {} # Links in the network
endpoints 	= {} # Hosts and routers in the network
flows 		= {} # Flows of data in the network
event_queue	= [] # Heap queue containing (time, event) tuples

	
def create_initial_events():
	'''
	This takes the set of flows and their descriptors and fills the event queue
	with events that signify the start of the respective flow.
	'''

def run_network():
	'''
	Run the simulation.
	'''

	# For debugging purposes?
	u.print_dict_keys("endpoints", endpoints)
	u.print_dict_keys("links", links)
	u.print_dict_keys("flows", flows)

	# Proposed pseudocode:
	#
	# // load and configure network
	# load_network_objects()
	# create_initial_events()
	# compute_routing_tables()
	#
	# // simulate network
	# time = 0 ms
	# next_data_recording = 0 ms
	# While event_queue not empty:
	# 	dequeue next event in chronology
	#	time = event_time
	#	if time >= next_data_recording:
	#		record network status // for realtime updates
	#		next_data_recording += network_recording_increments
	#	do event // each event will enqueue another event if necessary
	#
	
	return u.SUCCESS

if __name__ == "__main__":
	'''
	Takes one command-line argument (in addition to Python file): the name of the config
	file for the network.
	'''

	# Take the config filename from the commandline.
	network_file = argv[1]
	
	# Load in the network topology
	endpoints, links, flows, packets = cp.load_network_objects(network_file)
	
	# Run the network simulation loop
	status = run_network()
	
	return status
	
