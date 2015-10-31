#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# simulator_0.py
#
# This module simulates Test Case 0.
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

def main():
	'''
	Run the simulation for test case 0.
	'''
	# Contains (time, event) tuples in a heap queue so that when events are 
	# popped in chronological order
	event_queue = [] 

	# Load in the network topology
	endpoints, links, flows = cp.load_network_objects(ct.TEST_CASE_0_FILENAME)
	packets = {}

	u.print_dict_keys("endpoints", endpoints)
	u.print_dict_keys("links", links)
	u.print_dict_keys("flows", flows)

if __name__ == "__main__":

	# Run test case 0
	main()

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
