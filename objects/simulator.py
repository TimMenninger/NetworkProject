#
# simulator.py
#
# This contains the simulator module.  This is where the simulation happens:
# the event queue is here, the lists of objects are here and the main loop
# is here.
#

# Import network objects
import packet, link, flow, router, event, host

# Contains (time, event) tuples in a heap queue so that when events are popped
# in chronological order
event_queue = [] 

dict_flows    	= {}
dict_endpoints	= {}
dict_links   	= {}
dict_packets 	= {}

def load_network_objects(network_filename):
	'''
	Loads network topology from the user's config file and instantiates the
	Flow, Host, Link, and/or Router objects, as necessary.
	'''
	
	# Open the file so we can parse it.
	network = network_filename.open()
	
	# First line is just hosts
	line = network.readline()
	line = network.readline()
	
	# Iterate through hosts and create them.
	while line != '\n':
		# Create a host and add it to the dictionary.
		host_name = list(line)
		dict_endpoints[host_name[0]] = Host(host_name[0])
		
		# Read the next line.
		line = network.readline()
		
	# The next line is the router title.
	line = network.readline()
	line = network.readline()
	
	# Iterate through routers and create them.
	while line != '\n':
		# Create a router and add it to the dictionary.
		router_name = list(line)
		dict_endpoints[router_name[0]] = Router(router_name[0])
		
		# Read the next line.
		line = network.readline()
	
	# The next line is just the linkSpecs title.
	line = network.readline()
	line = network.readline()
	
	# Iterate through links and specs and create links for them.
	while line != '\n':
		# Syntax: (ID Rate Delay Buffer)
		link = list(line)
		
		# Create a link and add it to the dictionary.
		dict_links[link[0]] = Link(link[0], int(link[1]), int(link[2]), link[3])
		
		# Read the next line.
		line = network.readline()
		
	# The next line will be flowSpecs
	line = network.readline()
	line = network.readline()
	
	# Iterate through flows and create flows for them.
	while line != '\n':
		# Syntax: (ID Src Dest Data Start_Time)
		flow = list(line)
		
		# Create a flow and add it to the dictionary.
		dict_flows[flow[0]] = Flow(flow[0], flow[1], flow[2], int(flow[3]), float(flow[4]))
		
		# Read the next line.
		line = network.readline()
		
	# The next line will be Links.
	line = network.readline()
	line = network.readline()
	
	# Iterate through links and set up network.
	while line != '\n':
		# Syntax: (firstID linkID secondID)
		link = list(line)
		
		# Add the link to the first and second nodes.
		dict_endpoints[link[0]].add_link(link[1])
		dict_endpoints[link[2]].add_link(link[1])
		
		# Read the next line.
		line = network.readline()
		
	# Close the file.
	network.close()

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
