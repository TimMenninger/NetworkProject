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

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import simulator so we can access events, objects and time.
import simulate as sim

import constants as ct

def network_type(actor_name):
    '''
    Returns the type of the network object (as a constant) given its name
    '''
    if actor_name.startswith("F"):
        return ct.FLOW
    elif actor_name.startswith("L"):
        return ct.LINK
    elif actor_name.startswith("R"):
        return ct.ROUTER
    elif actor_name.startswith("H"):
        return ct.HOST
    else:
        return ct.PACKET

def get_actor_and_function(actor_name, function_name):
    '''
    Returns the actor and function object given an actor_type (one of the 
    network object constants from constants.py) and the function_name (a string)
    '''
    # Get whether its a Flow, Link, Host, Router, or Packet so that 
    # you can call the correct function
    actor_type = network_type(actor_name)
    
    # FLOW
    if actor_type == ct.FLOW:
        actor = sim.flows[actor_name]
        event_function = getattr(f.Flow, function_name)
    # LINK
    elif actor_type == ct.LINK:
        actor = sim.links[actor_name]
        event_function = getattr(l.Link, function_name)
    # PACKET
    elif actor_type == ct.PACKET:
        actor = sim.packets[actor_name]
        event_function = getattr(p.Packet, function_name)
        # ROUTER || HOST
    else: # actor_type == ct.ROUTER or actor_type == ct.HOST
        actor = sim.endpoints[actor_name]
        if actor_type == ct.ROUTER:
            event_function = getattr(r.Router, function_name)
        else: # actor_type == ct.HOST
            event_function = getattr(h.Host, function_name)

    return actor, event_function

def assign_endpoints(endpoints, sender_name):
    '''
    Returns a tuple, either (1,0) or (0,1), given an input of the sender name
    which indicates what the keys for the ep_names dictionary is in link.py 
    '''
    ep = endpoints[sender_name]
    other_ep = (ep + 1) % 2
    return ep, other_ep

def print_dict_keys(dict_name, dict):
    '''
    Prints the keys of a dictionary.
    '''
    print("- " + dict_name + " -")
    for key in dict.keys():
        print("\t" + key)
