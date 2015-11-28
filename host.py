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
        print("[%.5f] %s: sent packet %d with data %d.\n" % 
            (sim.network_now(), self.host_name, packet.ID, packet.data))
        print(flow.to_complete, flow.expecting)
        
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
        
        # If not, we want to first resend all packets in flight,
        #   but only do this if this is one of the packets in flight.
        #   Otherwise, we will end up thinking we lost way more packets
        #   than we actually did.
        if len(flow.packets_in_flight) > 0 and \
           abs(packet.ID) > (flow.packets_in_flight[0][1].ID):
            flow.resend_inflight_packets()
        
        # Next, because we want to check if the time we waited for timeout is
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
        if 0:#packet.type != ct.PACKET_ROUTING:
            print("[%.5f] %s: received packet %d with data %d.\n" % 
                (sim.network_now(), self.host_name, packet.ID, packet.data))
            print(flow.to_complete, flow.expecting)

        # If this is a data packet, create an ack packet and send it back.
        if packet.type == ct.PACKET_DATA:
            # Check if it is the one that this dest is expecting.
            if packet.data == flow.expecting:
                # Increment what we are now expecting.
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
            # If this is acknowledgement, see if any packets were lost.
            if packet.data > flow.to_complete:
                # The dest has received packets <to_complete> through
                #   <packet.data> - 1, so we want to pop as many packets as
                #   there is separation between these two parameters.
                for i in range(packet.data - flow.to_complete):
                    flow.to_complete += 1
                    heapq.heappop(flow.packets_in_flight)
                assert (packet.data == flow.to_complete)
                
                # Compute the most recent RTT, which can be used for congestion
                #   control
                flow.last_RTT = sim.network_now() - packet.time
                
                # See if the flow can be updated (i.e., more packets put in 
                # flight)
                flow.update_flow()
                
            else:# packet.data <= flow.to_complete:
                # Packets were lost.  Resend any and all that were in flight,
                #   but only do this if this is one of the packets in flight.
                #   Otherwise, we will end up thinking we lost way more packets
                #   than we actually did.
                if len(flow.packets_in_flight) > 0 and \
                   abs(packet.ID) > (flow.packets_in_flight[0][1].ID):
                    flow.resend_inflight_packets()
            
            # else the packet has already been received
        # else the packet is a routing packet and can be ignored.
        
        
