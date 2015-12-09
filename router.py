############################################################################
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


############################################################################
#                                                                          #
#                                  Router Class                            #
#                                                                          #
############################################################################

class Router:

    def __init__(self, in_router_name):
        '''
        Description:        Initialize an instance of Router by intitializing 
                            its attributes.

        Arguments:          in_router_name (string)

        Shared Variables:   self.in_router_name (WRITE)

        Global Variables:   None.
 
        Limitations:        None.

        Known Bugs:         None.

        Revision History:   10/20/15: Created
        '''
        # Store the type so it can be easily identified as a router.
        self.type = ct.TYPE_ROUTER

        # Name of the Router, each name is a unique string (i.e., "R1")
        self.router_name = in_router_name

        # Dictionary indexed by link names whose values are the identity of
        #   the endpoint on the other side.
        self.links = {}

        # Python dictionary - contains destination hostnames as keys and Link
        #   names as values.
        self.routing_table = {}
        self.updating_table = {}
        
        # Dictionary where keys are hosts and values are pairs of distance to
        #   that host (in average time) and the link one should send a packet 
        #   on to send to that host with that time.  A distance of -1 implies 
        #   that it is unknown what the distance to that host is, but the 
        #   existance of the host is known.
        self.distances = {}
        
        # Dictionary where keys are link names and values are the number of
        #   consecutive routing packets from that link where no new 
        #   information was learned.
        self.no_improves = {}
        
        # This is true if the table is currently configuring/waiting for
        #   configuration packets to fill its table.
        self.configuring = False
        
        
    def get_host_distances(self):
        '''
        Description:        This populates the updating routing table with 
                            distances (in time) to each host connected directly 
                            to this Router.
        
        Arguments:          self (Router)
        
        Return Values:      None.
        
        Shared Variables:   self.links (READ) 
                                - Iterated over to find connected Host objects.
                          
                            self.router_name (READ) 
                                - Used to get information that the Link "knows" 
                                about this Router
                            
                            self.distances (WRITE) 
                                - The distance to each connected Host is 
                                written in this dictionary.
                          
                            self.no_improves (WRITE) 
                                - This is set to the maximum for Link objects
                                connecting Host objects to this Router because
                                Host will never send a routing packet.
                          
                            self.updating_table (WRITE) 
                                - The link used to get to each host is added 
                                to this table.
        
        Global Variables: 
                            sim.endpoints (READ) 
                                - Used to get the endpoint at the other end of 
                                a Link.
                          
                            sim.links (READ) 
                                - Used to get the Link object from its name.
        
        Limitations:      None.
        
        Known Bugs:       None.
        
        Revision History: 11/26/15: Created
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
            
            # Add this link to the routing table, as there will never be an
            #   update for this host as there is only one route.
            self.routing_table[other_ep_name] = link_name
            
            # There will be no routing packets on this link, so make its
            #   no improvements number the maximum.
            self.no_improves[link_name] = ct.MAX_NO_IMPROVES


    def add_link(self, link_name):
        '''
        Description:        This sets the Link the Router is connected to.
        
        Arguments:          link_name (string) 
                                - The name of the Link that is associated
                                with this Router.
        
        Return Values:      None.
        
        Shared Variables:   self.link (WRITE) 
                                - This sets the link attribute.
        
        Global Variables:   sim.links (READ) 
                                - Used to get the name of what is connected to 
                                this Router by this Link.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/29: Created
        '''
        # Add the link and other endpoint to the dictionary of links
        self.links[link_name] = sim.links[link_name].get_other_ep(
                                                            self.router_name)
        
        # There have obviously been no consecutive routing packets on this link
        #   yet.
        self.no_improves[link_name] = 0
        

    def transmit_config_packet(self, empty_list):
        '''
        Description:        This creates a configuration packet and broadcasts 
                            it to the network.  These configuration packets 
                            are to be used by routers to populate their 
                            routing tables.
        
        Arguments:          empty_list ([]) 
                                - Unused.
        
        Return Values:      None.
        
        Shared Variables:   self.router_name (READ) 
                                - Used for identification.

                            self.updating_table (READ) 
                                - If empty, process is suspended.  If not, 
                                table is sent as data.
        
        Global Variables:   sim.flows (READ) 
                                - Used to get the link we are putting Packet 
                                on.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   11/23/15: Created
        '''
        # This marks the start of configuration.
        self.configuring = True
        
        # If there are still flows, the network is not done yet, and we should
        #   schedule the next routing send event.  The one flow that does not
        #   count here (why we use > 1) is the routing flow.
        if len(sim.running_flows) > 1:
            routing_time = sim.network_now() + ct.CONFIG_PKT_TIME
            routing_event = e.Event(self.router_name, 
                                    'transmit_config_packet', [])
            sim.enqueue_event(routing_time, routing_event)
            
        # Calculate the time distances to each host connected to this router 
        #   so we can broadcast the information
        self.get_host_distances()
            
        # If there are no hosts, don't waste anybody's time by sending routing
        #   packets--nobody will have anything to learn from an empty table.
        if len(self.updating_table.keys()) == 0:
            return
        
        # Send this packet onto each link on the router.
        for link_name in self.links:
            
            # Get a unique packet ID for the routing flow.
            pkt_ID = sim.flows[ct.ROUTING_FLOW].create_packet_ID()

            # Create the packet that we are going to send.  It doesn't need to 
            #   have a destination because its destination is everywhere.  
            #   The source is the link name for ease when parsing it.
            routing_pkt = p.Packet(pkt_ID, ct.ROUTING_FLOW, link_name,
                                    None, ct.PACKET_ROUTING)

            # The data that will be parsed is the table of current known
            #   time-distances to each host
            routing_pkt.data = copy.deepcopy(self.distances)

            # Record the time of transmission for this packet so others can 
            #   update their routing table effectively.
            routing_pkt.time = sim.network_now()

            # Put the packet in the global dictionary of packets.
            sim.packets[(ct.ROUTING_FLOW, routing_pkt.ID)] = routing_pkt
            
            # Send this packet on the link.
            self.send_packet([routing_pkt, link_name])
            
        # After a certain amount of time, we will assume all routing packets 
        #   not received have been lost, and we should just switch routing 
        #   tables as is.
        timeout_time = sim.network_now() + ct.ROUTING_TIMEOUT
        timeout_ev = e.Event(self.router_name, 'switch_routing_tables', [])
        sim.enqueue_event(timeout_time, timeout_ev)
        

    def parse_config_packet(self, packet):
        '''
        Description:        Upon reception of a configuration packet, this is
                            called to parse it and update the routing table if
                            necessary.
        
        Arguments:          packet (Packet) 
                                - The packet that is to be parsed to update 
                                the routing table.
        
        Return Values:      None.
        
        Shared Variables:   self.routing_tables (WRITE) 
                                - Updates the routing table not in use to 
                                reflect new information.

                            self.no_improves (WRITE) 
                                - If nothing in the routing table is improved 
                                for a particular Host, the entry for that host 
                                is incremented.

                            self.distances (WRITE) 
                                - Updated to keep track of the closest distance 
                                to a particular host.
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   11/24/15: Created
        '''
        # Before doing anything else, if this contains information about a host
        #   that is not in the routing table, put it in right away.  We don't
        #   want to lose more packets to that host than we already have.
        for host_name in packet.data:
            if host_name not in self.routing_table:
                self.routing_table[host_name] = copy.deepcopy(packet.src)
        
        # Make sure this wasn't called by mistake.
        assert(packet.type == ct.PACKET_ROUTING)
        
        # We want to iterate through the data on the packet to see what can
        #   be updated on our updating routing table.
        for host_name in packet.data:
            # Get the distance from what sent this packet and add it to the
            #   data.
            packet.data[host_name] += self.get_distance(packet.src)
            
            if not self.configuring:
                continue
            
            # If it is not in our table yet, it is clearly an update.  If it
            #   is in our table and is an improvement, there must also be an
            #   update.
            if host_name not in self.updating_table or \
               packet.data[host_name] < self.distances[host_name]:
                # Have the table reflect the link this packet came from
                self.updating_table[host_name] = copy.deepcopy(packet.src)
                
                # Update the distance known to that host.
                self.distances[host_name] = copy.deepcopy(
                                                    packet.data[host_name])
                
                # There have now been zero consecutive non-improvements on
                #   this link.
                self.no_improves[packet.src] = 0
                
            # Otherwise, this did nothing for us.  Update the number of no
            #   improves for this link
            elif packet.src not in self.no_improves:
                # Host is accessible by a different link.
                self.no_improves[packet.src] = 1
            else:
                self.no_improves[packet.src] += 1
         
        # Check if we have received enough packets to determine we are in
        #   equilibrium, in which case we can switch routing tables.
        switch_tables = True
        for link_name in self.no_improves:
            if self.no_improves[link_name] < ct.MAX_NO_IMPROVES:
                switch_tables = False
                       
        # If we received this without improvement, only send it if the num
        #   improves is less than the max.  Otherwise, we can assume the 
        #   system is in equilibrium
        if not switch_tables:#self.no_improves[packet.src] <= ct.MAX_NO_IMPROVES:
            for link_name in self.links:
                # Copy the packet
                updated_pkt = packet.copy_packet()
                
                # Change the source to be the link it will be sent on.
                updated_pkt.src = link_name
                
                # Update the data.
                updated_pkt.data = copy.deepcopy(self.distances)
                
                # Send the packet.
                self.send_packet([updated_pkt, link_name])
        
        # If we never switched the flag to false, we have received enough
        #   packets to switch routing tables.
        if switch_tables:
            self.switch_routing_tables([])
        
        
    def get_distance(self, link_name):
        '''
        Description:        This takes the argued Link and estimates the time 
                            it would take to send a Packet down this Link using 
                            the queue on this side of the Link, the Link 
                            capacity and the Link propagation delay.
        
        Arguments:          link_name (string) 
                                - A string representing the name of the Link 
                                we are interested in.  This is used to index 
                                the global dictionary of Link.
        
        Return Values:      (int) 
                                - The time it would take to send a packet along
                                the argued Link.
        
        Shared Variables:   None.
        
        Global Variables:   sim.links (READ) 
                                - The argued Link name is used to get a Link 
                                object from this dictionary.
        
        Limitations:        This uses the link buffer on this side of the 
                            Link to estimate the link buffer on the other side 
                            of the Link.
        
        Known Bugs:         None.
        
        Revision History:   11/27/15: Created
        '''
        # Get the link so we can retrieve information from it.
        link = sim.links[link_name]
                
        # Otherwise, get the amount of data in the queue for this link
        #   so we can estimate the time it takes to send something here.
        (data, num_pkts) = link.get_buffer_info(self.router_name)
        
        # We will now guess the "distance" to this router in units of time.
        #   This time is the propagation delay plus the queuing delay.  The
        #   prop delay is known but the queuing delay is calculated as such:
        #       - Take the amount of data and number of Packet objects in this
        #           buffer
        #       - Assume the buffer on the other end is identical to this
        #           one.  This many packets must be sent before the next
        #           Packet.
        #       - Packet are loaded onto the link in FIFO order, so assume
        #           that ct.CONSEC_PKTS are sent on one Link before the next
        #           chronological Packet is on the other buffer.  In this
        #           scenario, propagation delay must be waited.
        #       - We now have 2d data to be transmitted, which takes
        #           2d / rate milliseconds.  We also have 2n Packet to be sent,
        #           with a "switch" in direction every cv.CONSEC_PKTS
        #           Packet, for a total of (2n / ct.CONSEC_PKTS) * delay
        #           time.  Then, the next Packet can be sent (this time is
        #           not taken into account because it would be the same next
        #           Packet for every host).
        #       - Add the link delay for this particular packet to be sent
        #           after the way is cleared.
        #
        data *= 2
        data /= ct.CONFIG_PKT_TIME # Puts it as a rate per millisecond.
        num_pkts *= 2
        num_pkts /= ct.CONFIG_PKT_TIME # Puts it as a rate per millisecond.
        queuing_delay = (cv.KB_to_Mb(data) / link.rate) / 1000
        prop_delay = (num_pkts / ct.CONSEC_PKTS + 1) * link.delay
        return queuing_delay + prop_delay
        
        
    def switch_routing_tables(self, empty_list):
        '''
        Description:        This updates the routing table so that the one that 
                            has been configuring becomes the one in use.
        
        Arguments:          empty_list ([]) 
                                - Unused
        
        Return Values:      None.
        
        Shared Variables:   self.configuring (READ) 
                                - If this is called but the Router is not in 
                                configuration, then nothing happens.
                          
                            self.updating_table (WRITE) 
                                - Reset to empty.
                          
                            self.routing_table (WRITE) 
                                - Set to match the new updated routing table 
                                (before it is cleared).
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   11/26/15: Created
        '''
        # If the new routing table is empty, do nothing.
        if not self.configuring:
            return
        
        # Fill any host entry in the routing table that is not in the updating
        #   table.
        for host_name in self.routing_table:
            if host_name not in self.updating_table:
                self.updating_table[host_name] = self.routing_table[host_name]
                
        # Reset the data logger on the link so we can fill the table again.
        for link_name in self.links:
            link = sim.links[link_name]
            link.reset_this_buffer(self.router_name)
                        
        # Switch routing tables then clear the updating one for the next time
        #   around.
        self.routing_table = copy.deepcopy(self.updating_table)
        self.updating_table = {}
        self.no_improves = {}
        self.configuring = False


    def send_packet(self, arg_list):
        '''
        Description:        This sends a Packet from this Router onto the 
                            argued Link that is attached to it.
        
        Arguments:          argument_list ([Packet, string]) 
                                - A list of arguments that is unpacked by the 
                                function.  This is a list to facilitate class 
                                definition.  The list should contain the 
                                Packet being sent and the name of the Link it 
                                will be sent on.
        
        Return Values:      None.
        
        Shared Variables:   self.router_name (READ) 
                                - This function uses the Router name so the 
                                Link knows where the Packet came from.
        
        Global Variables:   sim.links (READ) 
                                - The link name is used to index this and get
                                the Link.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/22: Created function handle and docstring.
                            2015/10/29: Filled in.
                            2015/11/14: Now just puts Packet on buffer.
                            2015/11/22: Copied from Host and adapted for 
                            Router.
        '''
        # The argument list is just the packet.
        [packet, link_name] = arg_list
        link = sim.links[link_name]
        
        # Log the send_packet() event to ct.ROUTER_LOG_FILE
        self.log_send_packet(packet)

        # Give the packet to the link to handle.  Here, it will either be
        #   enqueued on a buffer or transmitted.
        link.put_packet_on_buffer(self.router_name, packet)


    def receive_packet(self, arg_list):
        '''
        Description:        Receives a Packet from the Link and responds 
                            accordingly by checking the destination and 
                            putting the Packet on the Link that leads to that 
                            destination.
        
        Arguments:          arg_list ([string, int]) 
                                - A list of arguments that is unpacked by the 
                                function.  This implementation is to 
                                facilitate the event class.  The list should 
                                contain the flow name and the packet ID.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.packets (READ) 
                                - This gets the packet instance from the 
                                dictionary using the argued key.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/22: Created function handle and docstring.
                            2015/10/29: Filled in function.
                            2015/11/13: Decremented Link 'num_on_link' 
                                        attribute.
                            2015/11/14: Responds according to packet type and 
                                        ID.
                            2015/11/22: Copied from Host and adapted to Router.
        '''
        # Unpack the argument list.
        [flow_name, packet_ID] = arg_list
        packet = sim.packets[(flow_name, packet_ID)] 

        # Log the receive_packet() event to ct.ROUTER_LOG_FILE
        self.log_receive_packet(packet)

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


    def log_send_packet(self, packet):
        '''
        Description:        Provides log output in ct.ROUTER_LOG_FILE about a 
                            call to send_packet() with this Router object.  
                            Specifically, it logs which host is sending a 
                            Packet, the ID of the Packet it is sending and the 
                            data it is sending within the Packet (be it an 
                            index or a full routing table)
        
        Arguments:          packet 
                                - The Packet object that is being sent.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.log_router (WRITE)

                            ct.PACKET_DATA (READ)

                            ct.PACKET_ACK (READ)
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/28: Created
        '''
        if packet.type == ct.PACKET_DATA:
            snd_msg = "[%.5f]: Sending data packet from %s to %s.\n" \
                        % (sim.network_now(), self.router_name, packet.dest)
            sim.log_router.write(snd_msg)
            sim.log_router.write("\tPacket ID: %d\n" % packet.ID)
            sim.log_router.write("\tNext link: %s\n" % \
                            self.routing_table[packet.dest])
            # Data of Packet is just its index within the Flow
            sim.log_router.write("\tData: %d\n" % packet.data)

        elif packet.type == ct.PACKET_ACK: # it's an ack Packet
            snd_msg = "[%.5f]: Sending ack packet from %s to %s.\n" \
                        % (sim.network_now(), self.router_name, packet.dest)
            sim.log_router.write(snd_msg)
            sim.log_router.write("\tPacket ID: %d\n" % packet.ID)
            sim.log_router.write("\tNext link: %s\n" % \
                            self.routing_table[packet.dest])
            # Data of ack Packet should correspond with data of packet it is 
            # acknowleding, unless a packet is lost.  In any event, it's just
            # an integer
            sim.log_router.write("\tData: %d\n" % packet.data)

        else:
            # Destination of routing config packets is 'None'
            snd_msg = "[%.5f]: Sending routing config packet from %s.\n"\
            % (sim.network_now(), self.router_name) 
            sim.log_router.write(snd_msg)
            sim.log_router.write("\tPacket ID: %d\n" % packet.ID)
            # Data of Packet is a routing table
            sim.log_router.write("\tData (Distances):\n")
            for ep in packet.data: 
                sim.log_router.write("\t\t%s : %s\n" % (ep, packet.data[ep]))


    def log_receive_packet(self, packet):
        '''
        Description:        Provides log output in ct.ROUTER_LOG_FILE about a 
                            call to receive_packet() with this Router object.  
                            Specifically, it logs which host is sending a 
                            Packet, the ID of the Packet it is sending and the 
                            data it is sending within the Packet (be it an 
                            index or a full routing table)
        
        Arguments:          packet 
                                - The Packet object that is being sent.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.log_router (WRITE)

                            ct.PACKET_DATA (READ)

                            ct.PACKET_ACK (READ)
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/28: Created
        '''
        if packet.type == ct.PACKET_DATA:
            rec_msg = "[%.5f]: Receiving data packet at %s sent from %s.\n" \
                      % (sim.network_now(), self.router_name, packet.src)
            sim.log_router.write(rec_msg)
            sim.log_router.write("\tPacket ID: %d\n" % packet.ID)
            sim.log_router.write("\tNext link: %s\n" % \
                            self.routing_table[packet.dest])
            # Data of Packet is just its index within the Flow
            sim.log_router.write("\tData: %d\n" % packet.data)

        elif packet.type == ct.PACKET_ACK: # it's an ack Packet
            rec_msg = "[%.5f]: Receiving ack packet at %s sent from %s.\n" \
                % (sim.network_now(), self.router_name, packet.src)
            sim.log_router.write(rec_msg)
            sim.log_router.write("\tPacket ID: %d\n" % packet.ID)
            if packet.dest in self.routing_table:
                sim.log_router.write("\tNext link: %s\n" % \
                                        self.routing_table[packet.dest])
            # Data of ack Packet should correspond with data of packet it is 
            # acknowleding, unless a packet is lost.  In any event, it's just
            # an integer
            sim.log_router.write("\tData: %d\n" % packet.data)

        else: # it's a Routing Packet
            rec_msg = "[%.5f]: Receiving routing config packet at %s sent " \
                  "from %s.\n" % (sim.network_now(), self.router_name, 
                                  packet.src)
            sim.log_router.write(rec_msg)
            sim.log_router.write("\tPacket ID: %d\n" % packet.ID)
            # Data of Packet is a routing table
            sim.log_router.write("\tData (Distances):\n")
            for ep in packet.data: 
                sim.log_router.write("\t\t%s : %.5f\n" % (ep, packet.data[ep]))


