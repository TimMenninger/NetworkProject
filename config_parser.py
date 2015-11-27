################################################################################
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
################################################################################






################################################################################
#                                                                              #
#                               Imported Modules                               #
#                                                                              #
################################################################################

import sys

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

# Import the simulator so we have access to the global variables in it.
sim = sys.modules['__main__']

import utility as u


################################################################################
#                                                                              #
#                                   Functions                                  #
#                                                                              #
################################################################################

#
# load_network_objects
#
#
# Description:      Loads the network topology from a config file that is argued
#                   at the command line.  For each object in the network
#                   topology, this creates an object and indexes it in a
#                   dictionary by its name/ID.
#
# Arguments:        network_file (string) - A string representing the name of
#                       the network topology config file.
#
# Return Values:    sim.endpoints (dictionary) - A dictionary of routers and
#                       hosts indexed by their name.
#                   sim.links (dictionary) - A dictionary of links indexed by
#                       their respective names.
#                   sim.flows (dictionary) - A dictionary of flows indexed by
#                       the flow names.
#                   sim.packets (dictionary) - A dictionary of packets, which is
#                       left untouched (and thus empty) by this function.
#
# Global Variables: sim.endpoints (WRITE) - Adds hosts and routers to this
#                       dictionary when loading the network objects.
#                   sim.links (WRITE) - Adds links to this dictionary when
#                       loading the network objects.
#                   sim.flows (WRITE) - Adds flow objects to this dictionary
#                       when loading network objects.
#
# Limitations:      Only works if the network topology file is in the correct
#                   format.  Behavior is undefined otherwise.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created
#

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
        sim.endpoints[host_name] = h.Host(host_name)
        
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
        sim.endpoints[router_name] = r.Router(router_name)
        
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
        sim.links[link[0]] = l.Link(link[0], float(link[1]), int(link[2]), 
                                             int(link[3]), (link[4], link[5]))

        # Add the name of this Link as an endpoint attribute to each of the 
        # endpoints 
        sim.endpoints[link[4]].add_link(link[0])
        sim.endpoints[link[5]].add_link(link[0])

        # Read the next line.
        link = network.readline()
    
    # Next line is just "flowSpecs (ID Src Dest Data Start)"
    network.readline()

    flow = network.readline()
    
    # Iterate through flow specs, create Flows, and add them to the flows
    # dictionary.
    while flow != '\n' and flow != '':
        # Flow text encoding: (ID Src Dest Data Start_Time)
        # Get list storing: [ID, Src, Dest, Data]
        flow = flow.split()
        
        # Create a flow and add it to the dictionary.
        sim.flows[flow[0]] = f.Flow(flow[0], flow[1], \
                  flow[2], int(flow[3]), 1000 * float(flow[4]))
        
        # Read the next line.
        flow = network.readline()

    # Close the file.
    network.close()
    
    # Add a flow specifically for the routing tables to communicate with each
    #   other.
    sim.flows[ct.ROUTING_FLOW] = f.Flow(ct.ROUTING_FLOW, None, None, None, 0.0)
    
    # Create a dictionary for the packets.  Will be empty at first, but let's 
    # do it here so all of the dictionaries are created at once/in one place.
    sim.packets = {}

    # For debugging/user experience purposes -- to ensure network topology was 
    # loaded correctly
    print("\nNetwork config file: %s\n" % sys.argv[1])
    print("--- NETWORK TOPOLOGY ---\n")
    u.print_dict_keys("Endpoints", sim.endpoints)
    u.print_dict_keys("Links", sim.links)
    u.print_dict_keys("Flows", sim.flows)
    print("\n------------------------")

    # Return all the dictionaries
    return (sim.endpoints, sim.links, sim.flows, sim.packets)


