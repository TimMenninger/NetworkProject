# Simulator module

#! This will probably have to be in a module of its own...
event_queue = [] # Contains events for the network such as (e.g. sending packets) in
		 # 	the form of Event instances

def load_network_objects():
	'''
	Loads network topology from the user's config file and instantiates the
	Flow, Host, Link, and/or Router objects, as necessary.
	'''

def compute_routing_tables():
	'''
	Sets the routing tables for the network.
	'''
	
def create_initial_events():
	'''
	This takes the set of flows and their descriptors and fills the event queue
	with events that signify the start of the respective flow.
	'''

def main():
	'''
	Run the simulation.
	'''
	
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
