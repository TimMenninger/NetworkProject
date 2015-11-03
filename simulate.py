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

# Import the constants and the conversion functions
import constants as ct
import conversion as cv

# Import utility functions
import utility as u

# Import functions to carry out the simulation
import simulate as s

# Import the config parser
import config_parser as cp

# So we can use command line arguments.
import sys

# Import heapq library so we can use it for our events.
import heapq


################################################################################
#                                                                              #
#                               Global Variables                               #
#                                                                              #
################################################################################

# Global variables containing objects in the network as well as events.
packets 	= {} # Packets in the system
links 		= {} # Links in the network
endpoints 	= {} # Hosts and routers in the network
flows 		= {} # Flows of data in the network
event_queue	= [] # Heap queue containing (time, event) tuples

# The time of the network in simulated milliseconds.
network_time = 0


################################################################################
#                                                                              #
#                                   Functions                                  #
#                                                                              #
################################################################################

#
# network_now
#
# Description:		Returns the current simulation time in milliseconds.
#
# Arguments:		None.
#
# Return Values:	(integer) - The number of milliseconds since the network
#						simulation began.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#

def network_now():
	'''
	Returns the time in simulated milliseconds since the network was initiated.
	'''
	return network_time
	

#
# create_initial_events
#
# Description:		This takes the flows and creates the initial events for
#					them.  The initial event will be the same for all flows,
#					but the time of the event will depend on the flow start
#					time.
#
# Arguments:		None.
#
# Return Values:	None.
#
# Global Variables: event_queue (WRITE) - The event_queue heapqueue has the
#						initial flow events enqueued.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created
#
	
def create_initial_events():
	'''
	This takes the set of flows and their descriptors and fills the event queue
	with events that signify the start of the respective flow.
	'''
	
	# Create an event for each flow.
	for flow in flows:
		# Create the event for the flow starting.  There are no arguments, but the
		#	event class expects an argument list.
		flow_event = e.Event(flows[flow], flows[flow].start_flow, [])
		
		# Enqueue the event in our heap queue.
		heapq.heappush(event_queue, (flows[flow].start_time, flow_event))
		
	
#
# record_network_status
#
# Description:		Records the status of the network at the current time.
#
# Arguments:		None.
#
# Return Values:	None.
#
# Global Variables: network_time (READ) - Used as the independent variable when
#						creating graphs.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/11/02: Created function handle and docstring.
#
	
def record_network_status():
	'''
	This records the status of various attributes of the network such as time and congestion.
	'''
	
	
#
# run_network
#
# Description:		Starts the loop that will run the network.  This loop will
#					run either until there are no more events (which means the
#					network either failed or completed successfully) or until
#					the maximum simulation time is reached.  This starts by 
#					creating initial events and then the loop is fueled by
#					functions adding events.
#
# Arguments:		None.
#
# Return Values:	None.
#
# Global Variables: network_time (WRITE) - Updated to show current time.
#					event_queue (WRITE) - Updated to have next events.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/22: Created as main()
#					2015/10/29:	Changed to run_network and filled in more than
#									print functions.
#

def run_network():
	'''
	Run the simulation.
	'''

	# For debugging purposes?
	u.print_dict_keys("endpoints", endpoints)
	u.print_dict_keys("links", links)
	u.print_dict_keys("flows", flows)

	# Create the initial events for the flows given their dictated start times.
	create_initial_events()
	
	# Time in milliseconds the next recording should be made.
	next_data_recording = 0
	
	# Initialize the network time.
	network_time = 0
	
	# Iterate until there are no more events or the simulation time is over.
	while len(event_queue) > 0 and network_time < ct.SIMULATION_TIME:
		# dequeue next event in chronology
		next_event = heapq.heappop(event_queue)
		
		# Forward the time to the time of the next event.  For whatever reason, the time is stored
		#	as a string, so we are converting it to an integer here.
		network_time = round(float(next_event[0]), 0)
		
		# If the time passed the next time we should be making a recording, record network status
		if network_time >= next_data_recording:
			record_network_status()
			next_data_recording = ((network_time / ct.RECORDING_INTERVAL) + 1) * ct.RECORDING_INTERVAL
		
		# Extract the information about the next event so we can execute it.
		(actor, event_function, event_parameters) = next_event[1].get_info()
		
		# Do the event (each event will enqueue another event if necessary)
		event_function(event_parameters)
	
	return ct.SUCCESS


if __name__ == "__main__":
	if len(sys.argv) != 2:
		# Input was incorrect
		print 'usage: python simulate.py [config_file]\n'
		
	# Take the config filename from the commandline.
	network_file = sys.argv[1]
	
	# Load in the network topology
	endpoints, links, flows, packets = cp.load_network_objects(network_file)
	
	# Run the network simulation loop
	status = run_network()
	
	print 'Network ran with no errors.\n'
	
