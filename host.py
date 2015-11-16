################################################################################
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
################################################################################






################################################################################
#                                                                              #
#                               Imported Modules                               #
#                                                                              #
################################################################################

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


################################################################################
#                                                                              #
#                                   Host Class                                 #
#                                                                              #
################################################################################

class Host:

    def __init__(self, the_host_name):
        ''' 
        Initialize an instance of Host by intitializing its attributes.
        '''
        # Name of the host, each hostname is unique string (i.e., "H1")
        self.host_name = the_host_name
        
        # The link_name representing the Link to this Host
        self.link = []
        
        # Either 0 or 1 indicating for each Link that this Host is connected 
        # to, whether it is the "higher" (0) or "lower" (0) endpoint
        self.endpoint = None
        
#
# add_link
#
# Description:      This sets the link the host is connected to.
#
# Arguments:        self (Host)
#                   link_name (string) - The name of the link that is associated
#                       with this host.
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
        Alters the 'link' attribute of the Host to reflect the link
        connecting the Host to the network.
        '''
        self.link = link_name
    

#
# set_endpoint
#
# Description:      This sets the endpoint for this Host (only useful in 
#                    conjunction with the 'link' attribute.
#
# Arguments:        self (Host)
#                   endpoint (int) - The index of the endpoint (0 or 1) that 
#                   is associated with this Host and the Link
#
# Return Values:    None.
#
# Shared Variables: self.endpoint (WRITE) - This sets the endpoint attribute.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/13: Created
#
        
    def set_endpoint(self, endpoint_name):
        '''
        Alters the 'link' attribute of the Host to reflect the link
        connecting the Host to the network.
        '''
        self.endpoint = endpoint_name
    

#
# send_packet
#
# Description:      This sends a packet from this host onto the link that is
#                   attached to it.
#
# Arguments:        self (Host)
#                   argument_list ([string, string]) - A list of arguments that
#                       is unpacked by the function.  This is a list to
#                       facilitate class definition.  The list should contain
#                       the flow name and the packet name.
#
# Return Values:    None.
#
# Shared Variables: self.link (READ) - This function uses the link name to send
#                       a packet to it.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       This is occasionally called with a packet that is not in
#                       the dictionary.
#
# Revision History: 2015/10/22: Created function handle and docstring.
#                   2015/10/29: Filled in.
#                   2015/11/14: Enqueues event to check for timeout.
#                               Responds according to packet type
#

    def transmit_packet(self, argument_list):
        '''
        Sends a Packet from this Host to a particular destination.  Then, it 
        adds the appropriate subsequent event to the Simulator event queue.
        '''
        
        # Unpack the argument list.
        [flow_name, packet_name] = argument_list
        try:
            packet = sim.packets[(flow_name, packet_name)]
            flow = sim.flows[flow_name]
        except:
            return
        
        # Create an event to enqueue the packet on the link.
        link = sim.links[self.link]
        link.put_packet_on_buffer([self.host_name, flow_name, packet_name])
        
        if packet.type == ct.PACKET_DATA:
            # Wait for timeout (defined as constant) to check that ack has been
            # received for this packet.
            ack_timeout_event = e.Event(self.host_name, 
                                       'check_for_timeout', 
                                       [flow_name, packet_name])
            heapq.heappush(sim.event_queue, 
                          (sim.network_now() + ct.ACK_TIMEOUT_FACTOR * flow.RTT, 
                           ack_timeout_event))
                           
            # Set the data to be the current time so we know the RTT when its
            #   acknowledgement comes.
            sim.packets[(flow_name, packet_name)].data[1] = sim.network_now()
                                              
                                                                                 
#
# check_for_timeout
#
# Description:      This checks whether the host has received acknowledgement
#                   for the argued packet.  If it has, the function does 
#                   nothing.  However, if it hasn't, the function will resend
#                   the packets up to and including itself (nothing after,
#                   because their ack timeouts haven't been reached yet).
#
# Arguments:        self (Host)
#                   argument_list ([string, string]) - The first string is the
#                       name of the flow that the packet is a part of and the
#                       second is the packet ID.
#
# Return Values:    None.
#
# Shared Variables: self.flow (READ) - Reads the attributes of the flow to
#                       decide whether acknowledgement was received and if not,
#                       how to handle it.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/14: Created
#

    def check_for_timeout(self, argument_list):
        '''
        Checks whether acknowledgement has been received for the packet in the
        argued list.
        '''
        
        # Unpack the argument list.
        [flow_name, packet_ID] = argument_list
        
        # For ease, get the packet and flow corresponding to these.
        packet = sim.packets[(flow_name, packet_ID)]
        flow = sim.flows[flow_name]
        
        # If the packet value is less than or equal to the last received, then
        #   ack has been received for this packet.  Otherwise, we must resend
        #   it.
        if int(packet.data[0]) <= flow.last_complete:
            return
            
        # If here, there was a timeout and we must resend the packets in flight
        flow.resend_packets_in_flight()
 
        
#
# receive_packet
#
# Description:      Receives a packet from the link and responds accordingly by
#                   enqueuing an event.  This event may be sending an ack packet
#                   or otherwise.
#
# Arguments:        self (Host)
#                   argument_list ([string, string]) - A list of arguments that
#                       is unpacked by the function.  This implementation is to
#                       facilitate the event class.  The list should contain
#                       the flow name and the packet name.
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
#

    def receive_packet(self, argument_list):
        '''
        Receives a Packet from a Link.  Then, it adds the appropriate event to 
        the Simulator event queue.
        '''
        # Unpack the argument list.
        [flow_name, packet_name] = argument_list
        
        # Create a Packet for the argued description.
        packet = sim.packets[(flow_name, packet_name)]

        # Create a Flow for the argued description.
        flow = sim.flows[flow_name]
        
        if packet.type == ct.PACKET_DATA:

            # Create acknowledgement packet.
            ack_packet = p.Packet(flow.create_packet_ID(), packet.flow,
                                  self.host_name, packet.src, ct.PACKET_ACK, 
                                  ct.PACKET_ACK_SIZE)
                                  
            # Add the time the original packet was sent to this ack packet.
            ack_packet.set_data(packet.data)

            # Add this acknowledgement packet to our packet dictionary.
            sim.packets[(ack_packet.ID, ack_packet.flow)] = ack_packet
            
            # Compute how long the host must wait to send acknowledgement.
            time_delay = 0
            
            # Create an event to send this packet.
            send_ack_event = e.Event(self.host_name, 'transmit_packet',
                                        [ack_packet.flow, ack_packet.ID])

            # Add send ack packet event to the simulation priority queue
            heapq.heappush(sim.event_queue, ((sim.network_now() + time_delay), \
                                              send_ack_event))

        elif packet.type == ct.PACKET_ACK:
            # Check if this has the data of the next packet we expect.
            if int(packet.data[0]) == flow.last_complete + 1:
                # Remove this packet, it has been acknowledged
                flow.packets.pop()
                
                # Reflect that another packet has been complete.
                flow.last_complete += 1
                
                # Calculate the round trip time for this packet.
                pkt_RTT = sim.network_now() - packet.data[0]
                
                # Decrement the number of Packet in flight for the flow because
                # just received an acknowledgement for one
                flow.packets_in_flight -= 1

                # See if a new Packet can be sent
                flow.check_flow_status()
                
                print (len(flow.packets))
                
            # If the packet ID is less than the last complete, then it belongs
            #   to a packet who has already made a round trip.  This happens
            #   as a result of retransmitting packets.  In this case, ignore
            #   the acknowledgement.
            elif int(packet.data[0]) <= flow.last_complete:
                pass

            else:
                # There is an error, we must retransmit the packets.
                flow.resend_packets_in_flight()

        # Decrement the number of Packet going from the other endpoint to 
        # this endpoint
        sim.links[self.link].update_num_on_link(1)
        
           
#
# print_contents
#
# Description:      Prints the attributes and their contained values.  This is
#                   used mainly for debugging purposes.
#
# Arguments:        self (Host)
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
# Revision History: 2015/10/??: Created function handle
#
        
    def print_contents(self):
        '''
        For debugging use. Print out the contents of the Flow.
        '''
