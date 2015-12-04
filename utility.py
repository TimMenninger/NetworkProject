############################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# utilities.py
#
# This contains the utilities module.  This is where a number of random 
# utility functions are defined.
#
############################################################################


############################################################################
#                                                                          #
#                               Imported Modules                           #
#                                                                          #
############################################################################


# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import simulator so we can access events, objects and time.
import sys
sim = sys.modules['__main__']

import constants as ct


############################################################################
#                                                                          #
#                            Utility Functions                             #
#                                                                          #
############################################################################


def network_type(actor_name):
    '''
    Description:        Returns the type of the network object (as a constant) 
                        given its name.
    '''
    if actor_name in sim.flows:
        # It's a Flow!
        return ct.TYPE_FLOW

    elif actor_name in sim.links:
        # It's a Link!
        return ct.TYPE_LINK

    elif actor_name in sim.endpoints:
        # It's an endpoint (Host or Router)!
        return sim.endpoints[actor_name].type

    else:
        # It's a Packet!
        return ct.TYPE_PACKET


def get_actor_and_function(actor_name, function_name):
    '''
    Description:        Returns the actor and function object given an 
                        actor_type (one of the network object constants from 
                        constants.py) and the function_name (a string).
    '''
    # Get whether its a Flow, Link, Host, Router, or Packet so that 
    # you can call the correct function
    actor_type = network_type(actor_name)
    
    # FLOW
    if actor_type == ct.TYPE_FLOW:
        actor = sim.flows[actor_name]
        event_function = getattr(f.Flow, function_name)
    # LINK
    elif actor_type == ct.TYPE_LINK:
        actor = sim.links[actor_name]
        event_function = getattr(l.Link, function_name)
    # PACKET
    elif actor_type == ct.TYPE_PACKET:
        actor = sim.packets[actor_name]
        event_function = getattr(p.Packet, function_name)
    
    # ROUTER or HOST
    else: # actor_type == ct.TYPE_ROUTER or actor_type == ct.TYPE_HOST
        actor = sim.endpoints[actor_name]
        if actor_type == ct.TYPE_ROUTER:
            event_function = getattr(r.Router, function_name)
        else: # actor_type == ct.TYPE_HOST
            event_function = getattr(h.Host, function_name)

    return actor, event_function


def assign_endpoints(endpoints, sender_name):
    '''
    Description:        Returns a tuple, either (1,0) or (0,1), given an input 
                        of the sender name which indicates what the keys for 
                        the ep_names dictionary is in link.py. 
    '''
    ep = endpoints[sender_name]
    other_ep = (ep + 1) % 2
    return ep, other_ep


def print_dict_keys(dict_name, dict):
    '''
    Description:        Prints the keys of a dictionary.
    '''
    print("- " + dict_name + " -")
    for key in dict.keys():
        print("\t" + key)


