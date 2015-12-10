############################################################################
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
############################################################################


############################################################################
#                                                                          #
#                               Imported Modules                           #
#                                                                          #
############################################################################

import sys
from sys import stdout
import time

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
import status as s

# Import the config parser
import config_parser as cp

# Import heapq library so we can use it for our events.
import heapq


############################################################################
#                                                                          #
#                               Global Variables                           #
#                                                                          #
############################################################################

# Global variables containing objects in the network as well as events.
packets     = {} # Packets in the system
links       = {} # Links in the network
endpoints   = {} # Hosts and routers in the network
flows       = {} # Flows of data in the network

running_flows = [] # Flows that have packets still to send.

event_queue = [] # Heap queue containing (time, event) tuples

# We cannot have duplicate entries for time, so we must keep a "count" of
#   entries so we have a "tie breaker"
ev_time_dict = {}

# A file to log output
log_host = open(ct.HOST_LOG_FILE, 'w')
log_router = open(ct.ROUTER_LOG_FILE, 'w')
log_flow = open(ct.FLOW_LOG_FILE, 'w')
log_main = open(ct.MAIN_LOG_FILE, 'w')

# The time of the network in simulated milliseconds.
network_time = 0

# The number of network recordings being taken by the simulation.
network_recordings = 0    

############################################################################
#                                                                          #
#                           Simulator Functions                            #
#                                                                          #
############################################################################

def run_network():
    '''
    Description:        Starts the loop that will run the network.  This loop 
                        will run either until there are no more events (which 
                        means the network either failed or completed 
                        successfully) or until the maximum simulation time is 
                        reached.  This starts by creating initial events and 
                        then the loop is fueled by functions adding events.

    Arguments:          None.

    Return Values:      None.

    Global Variables:   network_time (WRITE) 
                            - Updated to show current time.
                      
                        event_queue (WRITE) 
                            - Updated to have next events.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/10/22: Created as main()
                        2015/10/29: Changed to run_network and filled in more 
                                    than print functions.
                        2015/11/17: Restyled and neatened it up
                        2015/11/18: Adding halting condition for network 
    '''
    
    # Declare that we are using/changing the global variable.
    global network_time
    
    # Create the initial events, which is the start of each flow.
    create_initial_events()

    # Iterate through the event queue until it is empty.
    while len(event_queue) > 0:
        # Pop the next event.
        [event_time, unused, event] = heapq.heappop(event_queue)
        
        # Advance the network time to the event time.
        network_time = event_time
        
        # If we exceeded the maximum network running time, stop simulating.
        if network_time >= ct.MAX_SIMULATION_TIME:
            print ("\n +----------------------------------+\n",
                      "|              WARNING             |\n",
                      "|                                  |\n",
                      "| Maximum simulation time reached. |\n",
                      "| Aborting...                      |\n",
                      "|                                  |\n",
                      "+----------------------------------+\n")
            return
        
        # Extract the information about the next event so we can execute it.
        (actor_name, function_name, event_parameters) = event.get_elements()
        
        # If there is no actor, then this event is asking to record network
        #   status.
        if actor_name == None:
            s.record_network_status()
        else:
            # Retrieve the actor and the function it will perform on the 
            # network
            actor, event = u.get_actor_and_function(actor_name, function_name)

            # Call the event function with the correct actor and parameters
            event(actor, event_parameters)

        compute_and_print_progress_status()


def compute_and_print_progress_status():
    '''
    '''
    total_pkts = 0
    total_progress = 0
    for flow in flows.values():
        if flow.flow_name != ct.ROUTING_FLOW:
            num_flow_pkts = int(cv.MB_to_bytes(flow.size) /ct.PACKET_DATA_SIZE) 
            total_pkts += num_flow_pkts
            if network_now() > flow.start_time:
                total_progress += num_flow_pkts - len(flow.packets_to_send)
    
    # Dynamically update user of Simulation Progress
    progress_msg = "Simulation Progress: %.1f%%" \
                                    % (100 * (total_progress / total_pkts))
    stdout.write("\r" + progress_msg)
    stdout.flush()


def network_now():
    '''
    Description:        Returns the current simulation time in milliseconds.

    Arguments:          None.

    Return Values:      (integer) 
                            - The number of milliseconds since the network
                            simulation began.

    Global Variables: None.

    Limitations:      None.

    Known Bugs:       None.

    Revision History: 2015/11/02: Created
    '''
    return network_time


def create_initial_events():
    '''
    Description:        This takes the flows and creates the initial events for
                        them.  The initial Event will be the same for all Flow
                        objects, but the time of the event will depend on the 
                        Flow start time.

    Arguments:          None.

    Return Values:      None.

    Global Variables:   event_queue (WRITE) 
                            - The event_queue heapqueue has the initial Flow 
                            events enqueued.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/02: Created
    '''    
    # Create the event that will record the network status.
    enqueue_event(network_now(), e.Event(None, None, None))
    
    # Create an event for each flow.
    for flow_name in flows:
        # Add the flow to our list of running flows.
        running_flows.append(flow_name)
        
        # If this is the routing flow, don't call start flow.  We will handle
        #   the routing flow separately.
        if flow_name == ct.ROUTING_FLOW:
            continue
         
        # Create the event for the flow starting.  There are no arguments, 
        # but the event class expects an argument list.
        flow_event = e.Event(flow_name, 'start_flow', [])
        
        # Enqueue the event in our heap queue.
        enqueue_event(flows[flow_name].start_time, flow_event)
        
    for ep_name in endpoints:
        # Get the link from the dictionary.
        ep = endpoints[ep_name]
        
        # Only want to create events for routers...
        if ep.type != ct.TYPE_ROUTER:
            continue
        
        # Create the first event for each router.
        routing_time = network_now() + ct.TIME_BIT
        routing_event = e.Event(ep.router_name, 'transmit_config_packet', [])
        enqueue_event(routing_time, routing_event)
    
    
def enqueue_event(time, event):
    '''
    Description:        This enqueues an event onto the event queue.  Python 
                        queues do not accept two identical entries, and because 
                        it cannot sort Event instances, two entries of the 
                        same time counts as a duplicate entry.  Thus, this 
                        counts how many entries the time has, and includes 
                        that number so that Python has a way of 
                        differentiating and sorting the heap.

    Arguments:          time (float) 
                            - The time the event is to occur/be enqueued.
                        
                        event (Event) 
                            - The event that is to occur/be enqueued.

    Return Values:      None.

    Shared Variables:   None.

    Global Variables:   ev_time_dict (WRITE) 
                            - Uses this to count how many times a particular 
                            time appears in the event queue.

                        event_queue (WRITE) 
                            - Enqueues the event.

    Limitations:        This orders events that are otherwise supposed to be
                        simultaneous.

    Known Bugs:         None.

    Revision History:   2015/11/16: Created
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

    # Start the timer
    start = time.time()

    # Take the config filename from the commandline.
    network_file = sys.argv[1]
    
    # Load in the network topology
    endpoints, links, flows, packets = cp.load_network_objects(network_file)
    
    # Run the network simulation loop
    status = run_network()

    # End the timer because the simulation is over
    end = time.time()
    print("\n\n[SUCCESS]: NETWORK SIMULATION COMPLETE.") 
    net_time = (network_recordings * ct.RECORD_TIME) / 1000
    print("    [ELAPSED NETWORK TIME]: %.3f seconds" % net_time)
    print("    [ELAPSED REAL TIME]:    %.3f seconds" % (end - start))
    print("    [NETWORK RECORDINGS]:   %d\n" % network_recordings)

    # Construct and desplay the plots
    s.construct_plots()


