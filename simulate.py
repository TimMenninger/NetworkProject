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

# Import utility functions
import utility as u

# Import functions to carry out the simulation
import simulate as s

# Import the config parser
import config_parser as cp

# Import heapq library so we can use it for our events.
import heapq



################################################################################
#                                                                              #
#                               Global Variables                               #
#                                                                              #
################################################################################

# Global variables containing objects in the network as well as events.
packets     = {} # Packets in the system
links       = {} # Links in the network
endpoints   = {} # Hosts and routers in the network
flows       = {} # Flows of data in the network
event_queue = [] # Heap queue containing (time, event) tuples

# The time of the network in simulated milliseconds.
network_time = 0

# We cannot have duplicate entries for time, so we must keep a "count" of
#   entries so we have a "tie breaker"
ev_time_dict = {}





def run_network():
    '''
    Runs the network.
    '''
    
    # Declare that we are using/changing the global variable.
    global network_time

    # For debugging purposes?
    u.print_dict_keys("endpoints", endpoints)
    u.print_dict_keys("links", links)
    u.print_dict_keys("flows", flows)
    
    # Create the initial events, which is the start of each flow.
    create_initial_events()
    
    # Iterate through the event queue until it is empty.
    while len(event_queue) > 0:
        # Pop the next event.
        [event_time, unused, event] = heapq.heappop(event_queue)
        
        # Advance the network time to the event time.
        network_time = event_time
        
        # Extract the information about the next event so we can execute it.
        (actor_name, function_name, event_parameters) = event.get_elements()

        # Do the event (each event will enqueue another event if necessary)
        if actor_name.startswith("F"):
            actor = flows[actor_name]
            event_function = getattr(f.Flow, function_name)
        elif actor_name.startswith("H") or actor_name.startswith("R"):
            actor = endpoints[actor_name]
            if actor_name.startswith("H"):
                event_function = getattr(h.Host, function_name)
            else:
                event_function = getattr(r.Router, function_name)
        #elif actor_name.startswith("packet"):
        #    actor = packets[]
        else: 
            actor = links[actor_name]
            event_function = getattr(l.Link, function_name)

        #print("\nEVENT: " + actor_name + "." + function_name + "(" + str(event_parameters) + ") -- " + str(event_time))
        event_function(actor, event_parameters)
        
        
def network_now():
    '''
    Returns the time of the network simulation.
    '''
    return network_time
    
    
def create_initial_events():
    '''
    This takes the set of flows and their descriptors and fills the event queue
    with events that signify the start of the respective flow.
    '''

    # Create an event for each flow.
    for flow_name in flows:
        # Create the event for the flow starting.  There are no arguments, 
        # but the event class expects an argument list.
        flow_event = e.Event(flow_name, 'start_flow', [])
        
        # Enqueue the event in our heap queue.
        enqueue_event(flows[flow_name].start_time, flow_event)
    
    
    
def enqueue_event(time, event):
    '''
    Enqueues an event on the event queue.
    '''
    # Figure out the "count" for this particular time so that we don't have two
    #   entries in the heapqueue that have the exact same key.
    if time not in ev_time_dict:
        ev_time_dict[time] = 0
    else:
        ev_time_dict[time] += 1
        
    heapq.heappush(event_queue, (time, ev_time_dict[time], event))
    
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        # Input was incorrect
        print("usage: python simulate.py [config_file]\n")
        exit()
        
    # Take the config filename from the commandline.
    network_file = sys.argv[1]
    
    # Load in the network topology
    endpoints, links, flows, packets = cp.load_network_objects(network_file)
    
    # Run the network simulation loop
    status = run_network()
    
    print("\n[SUCCESS]: Network simulation complete.\n")
    
