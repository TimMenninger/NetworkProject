################################################################################
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


################################################################################
#                                                                              #
#                                   Functions                                  #
#                                                                              #
################################################################################

#
# network_now
#
# Description:      Returns the current simulation time in milliseconds.
#
# Arguments:        None.
#
# Return Values:    (integer) - The number of milliseconds since the network
#                       simulation began.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
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
# Description:      This takes the flows and creates the initial events for
#                   them.  The initial event will be the same for all flows,
#                   but the time of the event will depend on the flow start
#                   time.
#
# Arguments:        None.
#
# Return Values:    None.
#
# Global Variables: event_queue (WRITE) - The event_queue heapqueue has the
#                       initial flow events enqueued.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created
#

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
        heapq.heappush(event_queue, (flows[flow_name].start_time, flow_event))
        
    
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
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created function handle and docstring.
#
    
def record_network_status(unused_list = None):
    '''
    This records the status of various attributes of the network such as time 
    and congestion.
    '''
    
    # TODO: Record network status
    
    # Create an event for the next recording if there are more events in the 
    # queue.  If there are no more events, we don't need to keep recording.
    # Otherwise, the event queue would never be empty and run_network would
    # always run for the entire allotted time.
    if len(event_queue) > 0:
        next_record_time = network_now() + ct.RECORDING_INTERVAL
        record_event = e.Event(None, record_network_status, [])
        heapq.heappush(event_queue, (next_record_time, record_event))
     
    
#
# run_network
#
# Description:      Starts the loop that will run the network.  This loop will
#                   run either until there are no more events (which means the
#                   network either failed or completed successfully) or until
#                   the maximum simulation time is reached.  This starts by 
#                   creating initial events and then the loop is fueled by
#                   functions adding events.
#
# Arguments:        None.
#
# Return Values:    None.
#
# Global Variables: network_time (WRITE) - Updated to show current time.
#                   event_queue (WRITE) - Updated to have next events.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created as main()
#                   2015/10/29: Changed to run_network and filled in more than
#                                   print functions.
#

def run_network():
    '''
    Run the simulation.
    '''
    
    # Declare that we are using/changing the global variable.
    global network_time

    # For debugging purposes?
    u.print_dict_keys("endpoints", endpoints)
    u.print_dict_keys("links", links)
    u.print_dict_keys("flows", flows)

    # Create the initial events for the flows given their dictated start times.
    create_initial_events()
    
    # Make the first recording of the network status.
    # record_network_status()
    
    # Iterate until there are no more events or the simulation time is over.
    while len(event_queue) > 0 and network_time < ct.MAX_SIMULATION_TIME:
        # Dequeue next event in chronology
        event = heapq.heappop(event_queue)
        
        # Get the time out of the event tuple (time, event)
        event_time = event[0]

        # Forward the network time to the time of the next event
        network_time = event_time

        # Extract the event from the (time, event) tuple
        event = event[1]

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

        print("\nEVENT: " + actor_name + "." + function_name + "(" + str(event_parameters) + ") -- " + str(event_time))
        event_function(actor, event_parameters)


    return ct.SUCCESS


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
    
