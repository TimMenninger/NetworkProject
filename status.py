################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# status.py
#
# This contains the code to record the network status at fixed time intervals.
#
################################################################################






################################################################################
#                                                                              #
#                               Imported Modules                               #
#                                                                              #
################################################################################

# So we can use command line arguments.
import sys

# Import network objects
import packet as p
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
sim  = sys.modules['__main__']

# Import the queue Python package for the link buffers which are FIFO
import queue

# Import heapq library so we can use it for our events.
import heapq 

# Matplotlib has everything we need for graphing.
import matplotlib.pyplot as plt

times 					= [ ]
link_rate_readings 		= { }	# Indexed by link name, stores link rates
buffer_occ_recordings	= { }	# Indexed by link name, stores buffer occupancies
packet_loss_recordings 	= { }	# Indexed by link name, stores packet loss
flow_rate_recordings 	= { }	# Indexed by flow name, stores flow rates
packet_delay_recordings = { }	# Indexed by flow name, stores packet delays (RTT)
window_size_recordings	= { }	# Indexed by flow name, stores window sizes





        
    
#
# record_network_status
#
# Description:      Records the status of the network at the current time.  It
#                   then creates a new event for the next network recording.
#                   Before doing this, however, it checks if there are events
#                   in the queue.  If there are no events, then adding another
#                   recording would be pointless because the network simulation
#                   is over.
#
# Arguments:        unused_list (List) - Done in this way so we can enqueue this
#                       as an event in our event queue heapqueue.  Defaults to
#                       None so it can be called without arguments.
#
# Return Values:    None.
#
# Global Variables: network_time (READ) - Used as the independent variable when
#                       creating graphs.
#					times (WRITE) - Time appended
#					link_rate_readings (WRITE) - Link rate appended
#					buffer_occ_recordings (WRITE) - Buffer occupancy appended
#					packet_loss_recordings (WRITE) - Packet loss appended
#					flow_rate_recordings (WRITE) - Flow rate appended
#					packet_delay_recordings (WRITE) - Packet Delay appended
#					window_size_recordings (WRITE) - Window size recorded
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created function handle and docstring.
#					2015/11/16: Filled in global arrays.
#
    
def record_network_status():
	'''
	Records the network status and displays it.
	'''
	# Get the names of all the links and flows in the system.
	all_links = sim.links.keys()
	all_flows = sim.flows.keys()
	
	# Get all of the readings.
	times.append(sim.network_now())
	
	# Get the link rate, buffer occupancies and packet loss for all links
	for link_name in all_links:
		link = sim.links[link_name]
		
		# If this is the first reading, create entries for links.
		if link not in link_rate_readings:
			link_rate_readings[link_name] = []
			buffer_occ_recordings[link_name] = []
			packet_loss_recordings[link_name] = []
		
		# Update our status arrays.	
		link_rate_readings[link_name].append(link.data_on_link)
		buffer_occ_recordings[link_name].append(link.buffer_load[0] + link.buffer_load[1])
		packet_loss_recordings[link_name].append(link.num_packets_lost)
		
	# Get the flow rate, packet delay and window size.
	for flow_name in all_flows:
		flow = sim.flows[flow_name]
		
		# If first reading, create entries for flows
		if flow not in flow_rate_recordings:
			flow_rate_recordings[flow_name] = []
			packet_delay_recordings[flow_name] = []
			window_size_recordings[flow_name] = []
		
		# Update status arrays
		flow_rate_recordings[flow_name] = 0 # TODO: Get flow rate
		packet_delay_recordings[flow_name] = flow.last_RTT
		window_size_recordings[flow_name] = flow.window_size





