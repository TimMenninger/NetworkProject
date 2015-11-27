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

# Allows us to copy elements
import copy


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
        # Store the type so it can be easily identified as a router.
        self.type = ct.TYPE_ROUTER

        # Name of the Router, each name is a unique string (i.e., "R1")
        self.router_name = the_router_name

        # Dictionary indexed by link names whose values are the identity of
        #   the endpoint on the other side.
        self.links = {}

        # Python dictionary - contains destination hostnames as keys and Link
        #   names as values.
        self.routing_table = {}
        self.updating_table = {}
        
        # Dictionary where keys are hosts and values are pairs of distance to
        #   that host (in average time) and the link one should send a packet on
        #   to send to that host with that time.  A distance of -1 implies that
        #   it is unknown what the distance to that host is, but the existance
        #   of the host is known.
        self.distances = {}
        
        # Dictionary where keys are link names and values are the number of
        #   consecutive routing packets from that link where no new information
        #   was learned.
        self.no_improves = {}
        
        # This is true if the table is currently configuring/waiting for
        #   configuration packets to fill its table.
        self.configuring = False
        
        
    #
    # get_host_distances
    #
    # Description:      This populates the updating routing table with distances
    #                   (in time) to each host connected directly to this
    #                   router.
    #
    # Arguments:        self (Router)
    #
    # Return Values:    None.
    #
    # Shared Variables: self.links (READ) - Iterated over to find connected
    #                       hosts.
    #                   self.router_name (READ) - Used to get information
    #                       that the link "knows" about this router
    #                   self.distances (WRITE) - The distance to each connected
    #                       host is written in this dictionary.
    #                   self.no_improves (WRITE) - This is set to the maximum
    #                       for links connecting hosts to this router because
    #                       hosts will never send a routing packet.
    #                   self.updating_table (WRITE) - The link used to get to
    #                       each host is added to this table.
    #
    # Global Variables: sim.endpoints (READ) - Used to get the endpoint at the
    #                       other end of a link.
    #                   sim.links (READ) - Used to get the link object from its
    #                       name.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/26/15: Created
    #
        
    def get_host_distances(self):
        '''
        Populates the update routing table with distances (in calculated time)
        to each host connected directly to this router.
        '''
        # Iterate over all of the links' other endpoints to get distances.
        for link_name in self.links:
            link = sim.links[link_name]
            
            # Get the name of the other endpoint to see if it is a host.
            other_ep_name = link.get_other_ep(self.router_name)
            
            # Get the other endpoint to check its type.
            other_ep = sim.endpoints[other_ep_name]
            
            # If it is not a host, we don't learn anything from it.
            if other_ep.type != ct.TYPE_HOST:
                continue
                
            # Get the delay associated with sending packets along this link.
            total_delay = self.get_distance(link_name)
            
            # Add this "distance" to the distance dictionary
            self.distances[other_ep_name] = total_delay
            
            # Add this host and link pair to our routing table.
            self.updating_table[other_ep_name] = link_name
            
            # There will be no routing packets on this link, so make its
            #   no improvements number the maximum.
            self.no_improves[link_name] = ct.MAX_NO_IMPROVES


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
    # Global Variables: sim.links (READ) - Used to get the name of what is connected
    #                       to this router by this link.
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
        # Add the link and other endpoint to the dictionary of links
        self.links[link_name] = sim.links[link_name].get_other_ep(self.router_name)
        
        # There have obviously been no consecutive routing packets on this link
        #   yet.
        self.no_improves[link_name] = 0
        
    #
    # transmit_config_packet
    #
    # Description:      This creates a configuration packet and broadcasts it
    #                   to the network.  These configuration packets are to be
    #                   used by routers to populate their routing tables.
    #
    # Arguments:        self (Router)
    #                   empty_list ([]) - Unused.
    #
    # Return Values:    None.
    #
    # Shared Variables: self.router_name (READ) - Used for identification.
    #                   self.updating_table (READ) - If empty, process is
    #                       suspended.  If not, table is sent as data.
    #
    # Global Variables: sim.flows (READ) - Used to get the link we are putting
    #                       packets on.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/23/15: Created
    #

    def transmit_config_packet(self, empty_list):
        '''
        Creates and sends a special configuration packet that, when received by
        other routers, is understood as a configuration packet.
        '''
        # This marks the start of configuration.
        self.configuring = True
        
        # If there are still flows, the network is not done yet, and we should
        #   schedule the next routing send event.  The one flow that does not
        #   count here (why we use > 1) is the routing flow.
        if len(sim.running_flows) > 1:
            routing_time = sim.network_now() + ct.CONFIG_PKT_TIME
            routing_event = e.Event(self.router_name, 'transmit_config_packet', [])
            sim.enqueue_event(routing_time, routing_event)
            
        # Calculate the time distances to each host connected to this router so
        #   we can broadcast the information
        self.get_host_distances()
            
        # If there are no hosts, don't waste anybody's time by sending routing
        #   packets--nobody will have anything to learn from an empty table.
        if len(self.updating_table.keys()) == 0:
            return
        
        # Send this packet onto each link on the router.
        for link_name in self.links:
            
            # Get a unique packet ID for the routing flow.
            pkt_ID = sim.flows[ct.ROUTING_FLOW].create_packet_ID()

            # Create the packet that we are going to send.  It doesn't need to have
            #   a destination because its destination is everywhere.  The source
            #   is the link name for ease when parsing it.
            routing_pkt = p.Packet(pkt_ID, ct.ROUTING_FLOW, link_name,
                                    None, ct.PACKET_ROUTING)

            # The data that will be parsed is the table of current known
            #   time-distances to each host
            routing_pkt.data = self.distances

            # Record the time of transmission for this packet so others can update
            #   their routing table effectively.
            routing_pkt.time = sim.network_now()

            # Put the packet in the global dictionary of packets.
            sim.packets[(ct.ROUTING_FLOW, routing_pkt.ID)] = routing_pkt
            
            # Send this packet on the link.
            self.send_packet([routing_pkt, link_name])
            
        # After a certain amount of time, we will assume all routing packets not
        #   received have been lost, and we should just switch routing tables
        #   as is.
        timeout_time = sim.network_now() + ct.ROUTING_TIMEOUT
        timeout_ev = e.Event(self.router_name, 'switch_routing_tables', [])
        sim.enqueue_event(timeout_time, timeout_ev)
    
    #
    # parse_config_packet
    #
    # Description:      Upon reception of a configuration packet, this is
    #                   called to parse it and update the routing table if
    #                   necessary.
    #
    # Arguments:        self (Router)
    #                   packet (Packet) - The packet that is to be parsed
    #                       to update the routing table.
    #
    # Return Values:    None.
    #
    # Shared Variables: self.routing_tables (WRITE) - Updates the routing table
    #                       not in use to reflect new information.
    #                   self.no_improves (WRITE) - If nothing in the routing
    #                       table is improved for a particular host, the entry
    #                       for that host is incremented.
    #                   self.distances (WRITE) - Updated to keep track of the
    #                       closest distance to a particular host.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/24/15: Created
    #

    def parse_config_packet(self, packet):
        '''
        Receives a configuration packet and updates the routing table if any new,
        useful information is learned from it.
        '''
        print (sim.network_now())
        print (self.routing_table)
        print (self.updating_table)
        print (packet.data)
        # Before doing anything else, if this contains information about a host
        #   that is not in the routing table, put it in right away.  We don't
        #   want to lose more packets to that host than we already have...
        for host_name in packet.data:
            if host_name not in self.routing_table:
                self.routing_table[host_name] = packet.src
                
        # Ignore the packet if we are not currently configuring.
        if not self.configuring:
            return
            
        # Make sure this wasn't called by mistake.
        assert(packet.type == ct.PACKET_ROUTING)
        
        # We want to iterate through the data on the packet to see what can
        #   be updated on our updating routing table.
        for host_name in packet.data:
            # Get the distance from what sent this packet and add it to the
            #   data.
            packet.data[host_name] += self.get_distance(packet.src)
            
            # If it is not in our table yet, it is clearly an update.  If it
            #   is in our table and is an improvement, there must also be an
            #   update.
            if host_name not in self.updating_table or \
               packet.data[host_name] < self.distances[host_name]:
                # Have the table reflect the link this packet came from
                self.updating_table[host_name] = packet.src
                
                # Update the distance known to that host.
                self.distances[host_name] = packet.data[host_name]
                
                # There have now been zero consecutive non-improvements on
                #   this link.
                self.no_improves[packet.src] = 0
                
            # Otherwise, this did nothing for us.  Update the number of no
            #   improves for this link
            elif packet.src not in self.no_improves:
                self.no_improves[packet.src] = 1
            else:
                self.no_improves[packet.src] += 1
                
        # If we received this without improvement, only send it if the num
        #   improves is less than the max.  Otherwise, we can assume the system
        #   is in equilibrium
        if self.no_improves[packet.src] < ct.MAX_NO_IMPROVES:
            for link_name in self.links:
                # Copy the packet
                updated_pkt = packet.copy_packet()
                
                # Change the source to be the link it will be sent on.
                updated_pkt.src = link_name
                
                # Update the data.
                updated_pkt.data = self.distances
                
                # Send the packet.
                self.send_packet([updated_pkt, link_name])
         
        # Check if we have received enough packets to determine we are in
        #   equilibrium, in which case we can switch routing tables.
        switch_tables = True
        for host_name in self.no_improves:
            if self.no_improves[host_name] < ct.MAX_NO_IMPROVES:
                switch_tables = False
        
        # If we never switched the flag to false, we have received enough
        #   packets to switch routing tables.
        if switch_tables:
            self.switch_routing_tables([])
        
        print(self.updating_table)
        print('\n')
        
        
    def get_distance(self, link_name):
        '''
        Gets the "distance" (time) to send a packet from this router to
        the other end of the argued link.
        '''
        # Get the link so we can retrieve information from it.
        link = sim.links[link_name]
                
        # Otherwise, get the amount of data in the queue for this link
        #   so we can estimate the time it takes to send something here.
        (data, num_pkts) = link.get_buffer_info(self.router_name)
        
        # We will now guess the "distance" to this router in units of time.
        #   This time is the propagation delay plus the queuing delay.  The
        #   prop delay is known but the queuing delay is calculated as such:
        #       - Take the amount of data and number of packets in this
        #           buffer
        #       - Assume the buffer on the other end is identical to this
        #           one.  This many packets must be sent before the next
        #           packet.
        #       - Packets are loaded onto the link in FIFO order, so assume
        #           that cv.CONSEC_PKTS are sent on one link before the next
        #           chronological packet is on the other buffer.  In this
        #           scenario, propagation delay must be waited.
        #       - We now have 2d data to be transmitted, which takes
        #           2d / rate time.  We also have 2n packets to be sent,
        #           with a "switch" in direction every cv.CONSEC_PKTS
        #           packets, for a total of (2n / ct.CONSEC_PKTS) * delay
        #           time.  Then, the next packet can be sent (this time is
        #           not taken into account because it would be the same next
        #           packet for every host).
        data *= 2
        num_pkts *= 2
        queuing_delay = data / link.rate
        prop_delay = (num_pkts / ct.CONSEC_PKTS) * link.delay
        total_delay = queuing_delay + prop_delay
        
        return total_delay
        
        
    #
    # switch_routing_tables
    #
    # Description:      This updates the routing table so that the one that has
    #                   been configuring becomes the one in use.
    #
    # Arguments:        self (Router)
    #                   empty_list ([]) - Unused
    #
    # Return Values:    None.
    #
    # Shared Variables: self.configuring (READ) - If this is called but the
    #                       router is not in configuration, then nothing
    #                       happens.
    #                   self.updating_table (WRITE) - Reset to empty.
    #                   self.routing_table (WRITE) - Set to match the new
    #                       updated routing table (before it is cleared)
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/26/15: Created
    #
        
    def switch_routing_tables(self, empty_list):
        '''
        Switches routing tables to the one that has been updating.
        '''
        # If the new routing table is empty, do nothing.
        if not self.configuring:
            return
            
        # Fill any host entry in the routing table that is not in the updating
        #   table.
        for host_name in self.routing_table:
            if host_name not in self.updating_table:
                self.updating_table[host_name] = self.routing_table[host_name]
                
        # Switch routing tables then clear the updating one for the next time
        #   around.
        self.routing_table = copy.deepcopy(self.updating_table)
        self.updating_table = {}
        self.configuring = False


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
        
        if 0:#packet.type != ct.PACKET_ROUTING:
            print("[%.5f] %s: sent packet %d with data %d to %s.\n" % 
                (sim.network_now(), self.router_name, packet.ID, packet.data, packet.dest))
            print(self.routing_table)


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

        # If this is a routing packet, use it to update the routing table and
        #   then resend it so others can do the same.
        if packet.type == ct.PACKET_ROUTING:
            self.parse_config_packet(packet)

        # Use the routing table and the packet destination to decide where to
        #   send this packet.  If it is not in the list, then something went
        #   wrong and this packet will go lost.
        elif packet.dest in self.routing_table:
            # Send the packet on that link.
            send_time = sim.network_now() + ct.TIME_BIT
            send_ev = e.Event(self.router_name, 'send_packet',
                                [packet, self.routing_table[packet.dest]])
            sim.enqueue_event(send_time, send_ev)
            
            #print("[%.5f] %s: received packet %d containing %d going to %s.  Sending on link %s\n" % 
            #    (sim.network_now(), self.router_name, packet.ID, packet.data, packet.dest, self.routing_table[packet.dest]))
            #print(self.routing_table)


