############################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# host.py
#
# This contains the host class, which is the object used to represent a
# host in the network.
#
############################################################################


############################################################################
#                                                                          #
#                               Imported Modules                           #
#                                                                          #
############################################################################

# So we can use command line arguments.
import sys

# Import network objects
import packet as p
import link as l
import router as r
import flow as f
import event as e

# Import the constants and the conversion functions
import constants as ct
import conversion as cv

# Import utility functions
import utility as u

# Import functions to carry out the simulation
sim  = sys.modules['__main__']

# Import the config parser
import config_parser as cp

# Import the queue Python package for the link buffers which are FIFO
import queue

# Import heapq library so we can use it for our events.
import heapq 


############################################################################
#                                                                          #
#                                   Host Class                             #
#                                                                          #
############################################################################

class Host:

    def __init__(self, in_host_name):
        '''
        Description:        Initialize an instance of Host by intitializing 
                            its attributes.

        Arguments:          in_host_name (string)
                                - A string indicating the name of this 
                                particular Host instance (i.e., "H1").

        Shared Variables:   self.type (WRITE)
                                - Initialized 

                            self.host_name (WRITE) 
                                - Initialized

                            self.link (WRITE)
                                - Initialized

        Global Variables:   None.

        Limitations:        None.

        Known Bugs:         None.

        Revision History:   10/06/15: Created
        '''
        # Store the type so this Host instance can be easily identified as a 
        # Host.
        self.type = ct.TYPE_HOST
        
        # Name of the Host, each host name is unique string (i.e., "H1")
        self.host_name = in_host_name
        
        # The link_name representing the Link to this Host
        self.link = None

        # Number of Packets this Host has sent in a record interval
        self.pkts_sent = 0

        # Number of ack Packets this Host has sent in a record interval
        self.ack_sent = 0

        # Number of Packets this Host has received in a record interval
        self.pkts_received = 0

        # Number of ack Packets this host has received in a record interval
        self.ack_received = 0
        
        
    def add_link(self, link_name):
        '''
        Description:        This sets the Link the Host is connected to.
        
        Arguments:          link_name (string) 
                                - The name of the Link that is associated
                                with this Host.
        
        Return Values:      None.
        
        Shared Variables:   self.link (WRITE) - This sets the link attribute.
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/29: Created
        '''
        self.link = link_name


    def send_packet(self, arg_list):
        '''
        Description:        This sends a packet from this host onto the link 
                            that is attached to it.
        
        Arguments:          argument_list ([string, string]) 
                                - A list of arguments that is unpacked by the 
                                function.  This is a list to facilitate class 
                                definition.  The list should contain the flow 
                                name and the packet name.
        
        Return Values:      None.
        
        Shared Variables:   self.link (READ) 
                                - This function uses the link name to send a 
                                packet to it.
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/22: Created function handle and docstring.
                            2015/10/29: Filled in.
                            2015/11/14: Now just puts packet on buffer.
        '''
        # The argument list is just the packet.
        [packet] = arg_list
        flow = sim.flows[packet.flow]

        # Log the send_packet() event to ct.HOST_LOG_FILE
        self.log_send_packet(packet)

        # First want to put the current time on the packet so we can calculate
        #   RTT later.
        packet.time = sim.network_now()
        
        # Get the link that we are going to send the packet on.
        link = sim.links[self.link]
        
        # Give the packet to the link to handle.  Here, it will either be
        #   enqueued on a buffer or transmitted.
        link.put_packet_on_buffer(self.host_name, packet)

        # Create an event that will search for acknowledgement after some 
        #   amount of time.  If ack was not received, it will resend the 
        #   packets.  This only applies to data packets.
        if packet.type == ct.PACKET_DATA:
            tmout_time = sim.network_now() + \
                         ct.ACK_TIMEOUT_FACTOR * flow.last_RTT
            tmout_event = e.Event(self.host_name, 'check_ack_timeout', 
                                  [packet])
            sim.enqueue_event(tmout_time, tmout_event)

            self.pkts_sent += 1

        elif packet.type == ct.PACKET_ACK:

            self.ack_sent += 1

        
    def check_ack_timeout(self, list_packet):
        '''
        Description:        This is called after some amount of time to check 
                            if we have been waiting "too long" for the argued 
                            Packet to be acknowledged.  If the Packet has 
                            reached its timeout, then all of the Packet in 
                            flight are resent and it is assumed that the 
                            Packet is lost.
        
        Arguments:          list_packet ([Packet]) 
                                - A list containing the packet we are 
                                searching acknowledgement for.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.flows (READ) 
                                - The flow the packet is a part of is read 
                                from this dictionary.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/16: Created
        '''
        # Unpack the argument list.
        [packet] = list_packet
        flow = sim.flows[packet.flow]
        
        # Check if acknowledgement has been received for this packet.  If so,
        #   disregard, we are done here.
        if packet.data < flow.to_complete:
            return
        



        ## Get the actor and function for updating window size as a result of
        ##   this timed-out packet.
        # actor, function = u.get_actor_and_function(self.host_name, \
        #       ct.CONG_UPDATE[ct.CONG_TIMEOUT][flow.congestion_alg])
        #
        ## Call the function on the actor which will update the flow's window
        ##   size according to the congestion control algorithm parameter.
        # actor.function(/* Any parameters required */)




        # If not, we want to first resend all packets in flight,
        #   but only do this if this is one of the packets in flight.
        #   Otherwise, we will end up thinking we lost way more packets
        #   than we actually did.
        if len(flow.packets_in_flight) > 0 and \
           packet.ID >= (flow.packets_in_flight[0][1].ID):
            # Time out will cause congestion control to revert to slow-start 
            #   phase, so we reset the window size to initial size of 1 packet, 
            #   change state to slow-start, and set sst to window/2
            flow.sst = flow.window_size/2
            flow.window_size = 1
            flow.state = 0
            flow.resend_inflight_packets()
        
        # Next, we want to check if the time we waited for timeout is
        #   sufficient.  If we have not received any acknowledgements yet, it
        #   is possible that we simply aren't waiting long enough for ack.
        #   Therefore, if there have been no acks received at all, increase
        #   the waiting time.
        if flow.to_complete == 1:
            flow.last_RTT *= ct.ACK_TIMEOUT_FACTOR
 

    def receive_packet(self, arg_list):
        '''
        Description:        Receives a Packet from the Link and responds 
                            accordingly by enqueuing an event.  This event may 
                            be sending an ack Packet or otherwise.
        
        Arguments:          argument_list ([string, string]) 
                                - A list of arguments that is unpacked by the 
                                function.  This implementation is to facilitate 
                                the Event class.  The list should contain the 
                                flow name and the packet name.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.packets (READ) - This gets the Packet instance 
                            from the dictionary using the argued key.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/22: Created function handle and docstring.
                            2015/10/29: Filled in function.
                            2015/11/13: Decremented Link 'num_on_link' 
                                        attribute.
                            2015/11/14: Responds according to packet type and 
                                        ID.
        '''
        # Unpack the argument list.
        [flow_name, packet_ID] = arg_list
        packet = sim.packets[(flow_name, packet_ID)]
        flow = sim.flows[flow_name]

        # Unpack our duplicate ack tuple
        (last_ack, num_dups) = flow.num_dup_acks

        # Log the receive_packet() event to ct.HOST_LOG_FILE
        self.log_receive_packet(packet)

        # If this is a data packet, create an ack packet and send it back.
        if packet.type == ct.PACKET_DATA:
            # Increment the number of data packets received by this host in 
            # this record interval
            self.pkts_received += 1 

            # Check if it is the one that this dest is expecting.
            if packet.data == flow.expecting:
                flow.expecting += 1
                
            # This is what we want, create an ack packet and send it.
            ack_pkt = p.Packet(-1 * packet.ID, 
                               flow_name, self.host_name, packet.src, 
                               ct.PACKET_ACK)
                               
            # Set the data of the ack to be what we are expecting. The src 
            #   will cross check this with what he sent and resend or not 
            #   accordingly
            ack_pkt.set_data(flow.expecting)
            
            # Add the packet to our dictionary of packets.
            sim.packets[(flow_name, ack_pkt.ID)] = ack_pkt
            
            # Send the packet!
            self.send_packet([ack_pkt])
                
        elif packet.type == ct.PACKET_ACK:
            # Increment the number of ack packets received by this host in 
            # this record interval
            self.ack_received += 1

            # If this is acknowledgement, see if any packets were lost.
            if packet.data > flow.to_complete:
                # The dest has received packets <to_complete> through
                #   <packet.data> - 1, so we want to pop as many packets as
                #   there is separation between these two parameters.

                flow.num_dup_acks = (packet.ID, 0)

                # If the flow is in slow-start phase, increment window size by 1
                if flow.state == 0:
                    # If we have reached the sst threshold, enter congestion avoidance
                    if flow.window_size >= flow.sst:
                        flow.state = 1

                    # Otherwise we are still in slow-start, increment window by 1
                    #   for acknowledged packet
                    flow.window_size += 1

                # If the flow is in congestion avoidance, increase window by 1/W
                if flow.state == 1:
                    flow.window_size += 1/flow.window_size

                for i in range(packet.data - flow.to_complete):
                    flow.to_complete += 1
                    flow.acked_packets += 1
                    heapq.heappop(flow.packets_in_flight)
                assert (packet.data == flow.to_complete)
                
                # Compute the most recent RTT, which can be used for congestion
                #   control
                flow.last_RTT = sim.network_now() - packet.time
                
                # See if the flow can be updated (i.e., more packets put in 
                # flight)
                flow.update_flow()
                
            else:#if packet.data <= flow.to_complete:
                # Packets were lost.  Resend any and all that were in flight,
                #   but only do this if this is one of the packets in flight.
                #   Otherwise, we will end up thinking we lost way more packets
                #   than we actually did.

                # Check to see if this is a duplicate ack being received by 
                #   comparing to the last received ack
                #if packet.ID == last_ack and \
                #   abs(packet.ID) >= flow.packets_in_flight[0][1].ID:
                #    num_dups += 1
                #    flow.num_dup_acks = (packet.ID, num_dups)

                # If at least three duplicate acks have been received, then set 
                #   window size to w/2, set sst to w/2, and retransmit
                if num_dups == 3:
                    flow.sst = flow.window_size/2
                    flow.window_size = flow.window_size/2
                    # num_dups = 0
                    flow.num_dup_acks = (packet.ID, 0)

                # Resend all packets in flight.
                if len(flow.packets_in_flight) > 0 and \
                   abs(packet.ID) > (flow.packets_in_flight[0][1].ID):
                    flow.resend_inflight_packets()
                    # Check to see if this is a duplicate ack being received
                    #   by comparing to the last received ack
                    num_dups += 1
                    flow.num_dup_acks = (packet.ID, num_dups)
            #print (flow.window_size, sim.network_now())
            # else the packet has already been received
        # else the packet is a routing packet and can be ignored.
        
        
    def log_send_packet(self, packet):
        '''
        Description:        Provides log output in ct.HOST_LOG_FILE about a 
                            call to send_packet().  Specifically, it logs 
                            which hcost is sending a Packet, the ID of the 
                            Packet it is sending and the data it is sending
                            within the Packet (be it an index or a full
                            routing table)
        
        Arguments:          packet 
                                - The Packet object that is being sent.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.log_host (WRITE)
        
                            ct.PACKET_DATA (READ)

                            ct.PACKET_ACK (READ)

        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/28: Created
        '''
        if packet.type == ct.PACKET_DATA:
            sim.log_host.write("[%.5f]: Sending data packet from %s to %s.\n" % 
                            (sim.network_now(), self.host_name, packet.dest))
            sim.log_host.write("\tPacket ID: %d\n" % packet.ID)
            # Data of Packet is just its index within the Flow
            sim.log_host.write("\tData: %d\n" % packet.data)

        elif packet.type == ct.PACKET_ACK: # it's an ack Packet
            sim.log_host.write("[%.5f]: Sending ack packet from %s to %s.\n" % 
                              (sim.network_now(), self.host_name, packet.dest))
            sim.log_host.write("\tPacket ID: %d\n" % packet.ID)
            # Data of ack Packet should correspond with data of packet it is 
            # acknowleding, unless a packet is lost.  In any event, it's just
            # an integer
            sim.log_host.write("\tData: %d\n" % packet.data)

        else: # It's a routing packet
            # Not printing the routing tables received by hosts.
            pass

    def log_receive_packet(self, packet):
        '''
        Description:        Provides log output in ct.HOST_LOG_FILE about a 
                            call to receive_packet().  Specifically, it logs 
                            which host is sending a Packet, the ID of the 
                            packet it is sending and the data it is sending
                            within the Packet (be it an index or a full
                            routing table)
        
        Arguments:          packet 
                                - The Packet object that is being received.
        
        Return Values:      None.
        
        Shared Variables:   None.
        
        Global Variables:   sim.log_host (WRITE)
        
                            ct.PACKET_DATA (READ)

                            ct.PACKET_ACK (READ)

        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/28: Created
        '''
        # Retrieve the Flow that this Packet belongs to
        flow = sim.flows[packet.flow]
        if packet.type == ct.PACKET_DATA:
            rec_msg = "[%.5f]: Receiving data packet at %s sent from %s.\n" \
                      % (sim.network_now(), self.host_name, packet.src)
            sim.log_host.write(rec_msg)
            sim.log_host.write("\tPacket ID: %d\n" % packet.ID)
            # Data of Packet is just its index within the Flow
            sim.log_host.write("\tData: %d\n" % packet.data)
            sim.log_host.write("\tExpected Data: %d\n" % flow.expecting)

        elif packet.type == ct.PACKET_ACK: # it's an ack Packet
            rec_msg = "[%.5f]: Receiving ack packet at %s sent from %s.\n" \
                % (sim.network_now(), str(self.host_name), str(packet.src))
            sim.log_host.write(rec_msg)
            sim.log_host.write("\tPacket ID: %d\n" % packet.ID)
            # Data of ack Packet should correspond with data of packet it is 
            # acknowleding, unless a packet is lost.  In any event, it's just
            # an integer
            sim.log_host.write("\tData: %d\n" % packet.data)
            sim.log_host.write("\tTo Complete: %d\n" % flow.to_complete)

        else: 
            # Not printing the routing tables received by hosts.
            pass


