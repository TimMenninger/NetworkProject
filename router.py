################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# router.py
#
# This contains the router class, which contains methods for simulating the
# routers in the network.  It also contains methods which periodically run
# a Bellman-Ford algorithm to build its own routing table.
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

# Import simulator so we can access events, objects and time.
import simulate as sim


################################################################################
#                                                                              #
#                                  Router Class                                #
#                                                                              #
################################################################################

class Router:

    def __init__(self, the_router_name):
        '''
        Initialize an instance of Router by intitializing its attributes.
        '''
        # Name of the Router, each name is a unique string (i.e., "R1")
        self.router_name = the_router_name

        # List of Link that are attached to this Router
        self.links = []

        # Python dictionary - contains destination hostnames as keys and Link
        #   names as values.  The table_using variable stores the index of the
        #   routing table in use.
        self.routing_tables = [ { 'H1' : 'L0', 'H2' : 'L1' }, {} ]
        self.table_using = 0
        
        
    def add_link(self, link_name):
        '''
        Adds a link to the router.
        '''
        self.links.append(link_name)
        

    def set_routing_table():
        '''
        Sets the routing table for this Router.
        '''
        
    def send_config_packet():
        '''
        Creates a special configuration packet that, when received by other routers,
        is understood as a configuration packet.
        '''
        
    def parse_config_packet():
        '''
        Receives a configuration packet and updates the routing table if any new, useful
        information is learned from it.
        '''

    def send_packet(self, arg_list):
        '''
        Sends a packet from this Router to a particular destination using a
        specific link connected to this Router.
        '''
        # The argument list is just the packet.
        [packet, link_name] = arg_list
        link = sim.links[link_name]
        
        # First want to put the current time on the packet so we can calculate
        #   RTT later.
        packet.time = sim.network_now()
        
        # Give the packet to the link to handle.  Here, it will either be
        #   enqueued on a buffer or transmitted.
        link.put_packet_on_buffer(self.router_name, packet)
        

    def receive_packet(self, arg_list):
        '''
        Receives a packet from a link and parses it.
        '''
        # Unpack the argument list.
        [flow_name, packet_ID] = arg_list
        packet = sim.packets[(flow_name, packet_ID)]
        sim.log.write("[%.5f] %s: received packet %d with data %d.\n" % 
            (sim.network_now(), self.router_name, packet.ID, packet.data))
            
        # Use the routing table and the packet destination to decide where to
        #   send this packet.  If it is not in the list, then something went
        #   wrong and this packet will go lost.
        if packet.dest in self.routing_tables[self.table_using]:
            # Send the packet on that link.
            self.send_packet([packet, self.routing_tables[self.table_using][packet.dest]])


