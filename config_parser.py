#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# config_parser.py
#
# This contains the simulator module.  This is where the simulation happens:
# the event queue is here, the lists of objects are here and the main loop
# is here.
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

# Dictionaries that will be populated during config parsing and returned in 
# load_network_objects.
dict_endpoints = {}
dict_links = {}
dict_flows = {}

def load_network_objects(network_file):
	'''
	Loads network topology from the user's config file and instantiates the
	Flow, Host, Link, and/or Router objects, as necessary.
	'''
	
	# Open the file so we can parse it.
	network = open(network_file, 'r')

	# First line is just "hostSpects (ID)"
	network.readline()

	# Rirst host_name
	host_name = network.readline()
	
	# Iterate through the host_names, create Hosts, and add them to the 
	# endpoints dictionary
	while host_name != '\n':
		# Remove new line
		host_name = host_name.strip()

		# Create a host and add it to the dictionary.
		dict_endpoints[host_name] = h.Host('host_' + host_name)
		
		# Read the host_name on the next.
		host_name = network.readline()
	
	# Next line is just "routerSpecs (ID)"
	network.readline()

	# First router_name
	router_name = network.readline()

	# Iterate through router_names, create Routers, and add them to the 
	# endpoints dictionary.  If there are no routers in the config files 
	# (i.e. Test Case 0), then nothing is added to the endpoints directory.
	while router_name != '\n':
		# Remove new line
		router_name = router_name.strip()

		# Create a router and add it to the dictionary.
		dict_endpoints[router_name] = r.Router('router_' + router_name)
		
		# Read the next line.
		router_name = network.readline()
	
	# Next line is just "linkSpecs (ID Rate Delay Buffer)"
	network.readline()
	
	# First link_name
	link = network.readline()
	
	# Iterate through link specs, create Links, and add them to the links
	# dictionary.
	while link != '\n':
		# Link text encoding: (ID Rate Delay Buffer Endpoint1 Endpoint2)
		# Get list storing: [ID, Rate, Delay, Buffer, Endpoint1, Endpoint2]
		link = link.split()

		# Create a link and add it to the dictionary
		dict_links[link[0]] = l.Link('link_' + link[0], float(link[1]), int(link[2]), 
								      int(link[3]), (link[4], link[5]))
		
		# Read the next line.
		link = network.readline()
	
	# Next line is just "flowSpecs (ID Src Dest Data Start)"
	network.readline()

	flow = network.readline()
	
	# Iterate through flow specs, create Flows, and add them to the flows
	# dictionary.
	while flow != '\n':
		# Flow text encoding: (ID Src Dest Data)
		# Get list storing: [ID, Src, Dest, Data]
		flow = flow.split()

		# Create a flow and add it to the dictionary.
		dict_flows[flow[0]] = f.Flow('flow_' + flow[0], flow[1], flow[2], int(flow[3]))
		
		# Read the next line.
		flow = network.readline()

	# Close the file.
	network.close()

	# Return all the dictionaries
	return (dict_endpoints, dict_links, dict_flows)


