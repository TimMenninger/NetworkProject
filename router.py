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
import sys
sim = sys.modules['__main__']


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
        if self.router_name == 'R1':
            self.routing_tables = [ { 'H1' : 'L0', 'H2' : 'L1'}, {} ]
        else:
            self.routing_tables = [ { 'H1' : 'L1', 'H2' : 'L2'}, {} ]
        self.table_using = 0
        
#
# add_link
#
# Description:      This sets the link the router is connected to.
#
# Arguments:        self (Host)
#                   link_name (string) - The name of the link that is associated
#                       with this router.
#
# Return Values:    None.
#
# Shared Variables: self.link (WRITE) - This sets the link attribute.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#
        
    def add_link(self, link_name):
        '''
        Adds a link to the router.
        '''
        self.links.append(link_name)
        

    def set_routing_table():
        '''
        Sets the routing table for this Router.
        '''
        
    def create_config_packet():
        '''
        Creates a special configuration packet that, when received by other routers,
        is understood as a configuration packet.
        '''
        
    def parse_config_packet(self, packet):
        '''
        Receives a configuration packet and updates the routing table if any new, useful
        information is learned from it.
        '''
        # Make sure this wasn't called by mistake.
        assert(packet.type == ct.PACKET_ROUTER)
    

#
# send_packet
#
# Description:      This sends a packet from this router onto the argued link that is
#                   attached to it.
#
# Arguments:        self (Host)
#                   argument_list ([Packet, string]) - A list of arguments that
#                       is unpacked by the function.  This is a list to
#                       facilitate class definition.  The list should contain
#                       the Packet being sent and the name of the link it will be
#                       sent on.
#
# Return Values:    None.
#
# Shared Variables: self.router_name (READ) - This function uses the router name
#                       so the link knows where the Packet came from.
#
# Global Variables: sim.links (READ) - The link name is used to index this and get
#                       the Link.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created function handle and docstring.
#                   2015/10/29: Filled in.
#                   2015/11/14: Now just puts packet on buffer.
#                   2015/11/22: Copied from host and adapted for router.
#

    def send_packet(self, arg_list):
        '''
        Sends a packet from this Router to a particular destination using a
        specific link connected to this Router.
        '''
        # The argument list is just the packet.
        [packet, link_name] = arg_list
        link = sim.links[link_name]
        
        # Give the packet to the link to handle.  Here, it will either be
        #   enqueued on a buffer or transmitted.
        link.put_packet_on_buffer(self.router_name, packet)
 
        
#
# receive_packet
#
# Description:      Receives a packet from the link and responds accordingly by
#                   checking the destination and putting the packet on the link
#                   that leads to that destination.
#
# Arguments:        self (Host)
#                   arg_list ([string, int]) - A list of arguments that
#                       is unpacked by the function.  This implementation is to
#                       facilitate the event class.  The list should contain
#                       the flow name and the packet ID.
#
# Return Values:    None.
#
# Shared Variables: None.
#
# Global Variables: sim.packets (READ) - This gets the packet instance from the
#                       dictionary using the argued key.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created function handle and docstring.
#                   2015/10/29: Filled in function.
#                   2015/11/13: Decremented Link 'num_on_link' attribute.
#                   2015/11/14: Responds according to packet type and ID.
#                   2015/11/22: Copied from host and adapted to router.
#

    def receive_packet(self, arg_list):
        '''
        Receives a packet from a link and parses it.
        '''
        # Unpack the argument list.
        [flow_name, packet_ID] = arg_list
        packet = sim.packets[(flow_name, packet_ID)]
        sim.log.write("[%.5f] %s: received packet %d with data %d.\n" % 
            (sim.network_now(), self.router_name, packet.ID, packet.data))
            
            
        # If this is a routing packet, use it to update the routing table and
        #   then resend it so others can do the same.
        if packet.type == ct.PACKET_ROUTING:
            self.parse_config_packet(packet)
            
        # Use the routing table and the packet destination to decide where to
        #   send this packet.  If it is not in the list, then something went
        #   wrong and this packet will go lost.
        elif packet.dest in self.routing_tables[self.table_using]:
            # Send the packet on that link.
            self.send_packet([packet, self.routing_tables[self.table_using][packet.dest]])


