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
        # names as values.
        self.routing_tables = ({}, {})
        
        # Keep track of the distances so we know how to update the routing tables when necessary.
        self.routing_dists = {}
        
        # The index of the routing table in use.
        self.using_table = 0
        
        
#
# add_link
#
# Description:      Adds a link to the list of links associated with this router.
#
# Arguments:        self (Router)
#                   link_name (string) - The name of the link being added.
#
# Return Values:    None.
#
# Shared Variables: self.links (WRITE) - Updated according to arguments.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created
#
    
    def add_link(self, link_name):
        '''
        Adds a link to the router.
        '''
        self.links.append(link_name)
        
        
#
# switch_routing_table
#
# Description:      This switches which routing table is currently being used
#                   to route packets and prepares the now-unused table to be
#                   refilled.  If there are any entries in the original table
#                   that are not in the new routing table, they are copied over.
#                   This way, if config packets were lost, we at least have a
#                   non-optimal way of routing packets (as opposed to no way at
#                   all).
#
# Arguments:        self (Router)
#
# Return Values:    None.
#
# Shared Variables: self.using_table (READ/WRITE) - Read to determine which
#                       table is unused then written to reflect the table that
#                       is now in use.
#                   self.routing_tables (WRITE) - The table that becomes unused
#                       as a result of this function is cleared.  The table that
#                       becomes used as a result of this function may have
#                       entries written to it.
#                   self.routing_dists (WRITE) - When the routing table is
#                       cleared, so is the list of all of the distances.  This
#                       way, if every time is slower due to congestion, we still
#                       update the routing tables.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created.
#
        
    def switch_routing_table(self):
        '''
        Switches the routing table in use and clears the now-unused one so it
        can be updated.
        '''
        
        # Get the index of the table not in use.
        other_table = (self.using_table + 1) % 2
        
        # Make sure if there was an entry in the routing table before that there
        #   is still an entry in the routing table.
        for key in self.routing_tables[self.using_table]:
            if key not in self.routing_tables[other_table]:
                self.routing_tables[other_table][key] = self.routing_tables[self.using_table][key]
                
        # After populating the new table, clear the current one so we can refill it.
        self.routing_tables[using_table] = {}
        self.routing_dists = {}
                
        # Update the index of which routing table is in use.
        self.using_table = other_table
        
        
#
# create_config_packet
#
# Description:      This creates a configuration packet that will be sent and
#                   propagated throughout the network.  This will contain the
#                   source (itself) and the time it was sent.  Then, each
#                   router can independently decide the route to this router
#                   based on who the time it took to reach them and the last
#                   person to propagate it before reception.
#
# Arguments:        self (Router)
#
# Return Values:    (Packet) - The packet that will be sent.
#
# Shared Variables: None.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#
        
    def create_config_packet(self):
        '''
        Creates a special configuration packet that, when received by other routers,
        is understood as a configuration packet and can be used to set up routing
        tables.
        '''
        
        config_pkt = p.Packet(None, FLOW, self.router_name, None, \
                              PACKET_ROUTING, PACKET_ROUTING_SIZE, None)
        
        config_pkt.set_data(self.router_name, sim.network_now())
        
        return config_pkt
        
        
#
# send_config_packet
#
# Description:      This sends a configuration packet after setting all of the
#                   attributes of it as necessary.
#
# Arguments:        self (Router)
#                   config_pkt (Packet) - The configuration packet that will be
#                       sent to all other routers.
#
# Return Values:    None.
#
# Shared Variables: self.links (READ) - Iterated over so the packet can be sent
#                       to all connected routers.
#
# Global Variables: None.
#
# Limitations:      This currently sends routing packets to hosts, too, which is
#                   fine as long as it doesn't confuse the hosts.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#
# Notes:
        #
        #   In this, we are going to initiate the process here with a specially
        # formatted packet that routers will understand as the "configuration" packet.
        #
        #   We will send a packet with the form [origin_router_name, distance_to] where
        # origin_router is the router sending the first "configuration" packet and 
        # distance_to is the total weight from the origin to this particular router.
        # Clearly, when sending this first packet, we will have [self.router_name, 0].
        # When receiving this packet, receive_packet should call parse_config_packet.  Refer
        # to that function for the rest of the computation involved with configuring the
        # routing tables.
        #
        #   For this to work, we want to keep track of the shortest distance to each
        # router from this one.  Initialize all these values to be infinity.
        #
        
    def send_config_packet(self, config_pkt):
        '''
        Creates a special configuration packet that, when received by other routers,
        is understood as a configuration packet.
        '''
        
        for link in self.links:
            config_pkt.set_time()
            config_pkt.set_ID()
            config_pkt.set_src(self.router_name)
            config_pkt.set_dest(link.link_name)
            send_packet(config_pkt)
        
        
#
# parse_config_packet
#
# Description:      This is called when the router receives a routing packet.
#                   This will parse the packet and decide if routing tables
#                   should be updated and if it should be propagated.  For this,
#                   if the routing table is not updated, the packet is not sent
#                   to other routers.  This is because this router previously
#                   propagated a better route to the given source, so sending it
#                   would not help anyone else, either.
#
# Arguments:        self (Router)
#                   config_pkt (Packet) - The configuration packet that the 
#                       function is to pares.
#
# Return Values:    None.
#
# Shared Variables: self.routing_tables (WRITE) - Updated if the packet shows
#                       that there is a shorter route to its source
#                   self.routing_dists (WRITE) - Updated if the routing table is
#                       updated.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#
# Notes:
        #
        #   This will be called when the router receives a config packet, which is in
        # the format [origin_router, distance_to].  The origin_router was the router which
        # initially sent this packet, and distance_to is the distance from the origin router
        # to this router using whatever path it used.
        #
        # All we need is some way of quantifying distance_to.  Maybe it's time, maybe not, I
        # don't know yet...
        #
        # This will work because every router will do this.  If the routers 
        # are all connected, then by relaying the messages whenever the distance is improved,
        # all routers will get a packet to all other routers at least once.  We only need to
        # continue propagation if it is improved because if not, then the time that the better
        # packet came through, that was propagated.  Therefore, we know this process will
        # terminate.
        #

        
    def parse_config_packet(self, config_pkt):
        '''
        Receives a configuration packet and updates the routing table if any new, useful
        information is learned from it.
        '''
        
        # Get the index of the table that is being populated (not the one being used)
        other_table = (self.using_table + 1) % 2
        
        # If we learn anything new from the information in this packet, update the new table.
        if (config_pkt.data[0] not in self.routing_tables[other_table]) or \
           (routing_dists[config_pkt.data[0]] > config_pkt.data[1]):
            # Update the dictionary at the key corresponding to the router that sent this packet
            #   to reflect that it should be used to send data to the source.
            self.routing_tables[other_table][config_pkt.data[0]] = config_pkt.src
            
            # Update the distances dictionary so we know if a better option comes around.
            self.routing_dists[config_pkt.data[0]] = sim.network_now() - config_pkt.data[1]
            
            # Create events to propagate this "better route" to src that was found and enqueue it.
            config_prop_delay = 0
            config_prop_event = e.Event(self, self.send_config_packet, [config_pkt])
            sim.enqueue_event(config_prop_delay, config_prop_event)
        
        
#
# send_packet
#
# Description:      Enqueues a packet on the appropriate link based on the
#                   routing table for the router.
#
# Arguments:        self (Router)
#                   argument_list ([string, string]) - A list containing the
#                       flow and packet names.
#
# Return Values:    None.
#
# Shared Variables: None.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created function handle and docstring.
#
    
    def send_packet(self, argument_list):
        '''
        Sends a packet from this Router to a particular destination using a
        specific link connected to this Router.
        '''
        
        
#
# receive_packet
#
# Description:      Receives a packet and decides what to do with it based on
#                   its type.  This can be enqueuing an event to propagate the
#                   routing packet or enqueuing an event to route a data/ack
#                   packet.
#
# Arguments:        self (Router)
#                   argument_list ([string, string]) - A list containing the
#                       flow and packet names.
#
# Return Values:    None.
#
# Shared Variables: None.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created function handle and docstring.
#
    
    def receive_packet(self, argument_list):
        '''
        Receives a packet from a link and parses it.
        '''
        
#
# print_contents
#
# Description:      Prints the attributes and their contained values.  This is
#                   used mainly for debugging purposes.
#
# Arguments:        self (Router)
#
# Return Values:    None.
#
# Shared Variables: None.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created function handle and docstring
#
        
    def print_contents(self):
        '''
        Prints attribute values for this Router.
        '''


