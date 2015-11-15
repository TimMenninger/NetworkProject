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

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import simulator so we can access global dictionaries.
import simulate as sim

# Import the constants and the conversion functions
import constants as ct
import conversion as cv


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
        self.link = None
        
        
#
# set_link
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
        
    def set_link(self, link_name):
        '''
        Alters the 'link' attribute of the Host to reflect the link
        connecting the Host to the network.
        '''
        self.link = link_name
    

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
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created function handle and docstring.
#                   2015/10/29: Filled in.
#                   2015/11/14: Enqueues event to check for timeout.
#                               Responds according to packet type
#

    def send_packet(self, argument_list):
        '''
        Sends a Packet from this Host to a particular destination.  Then, it 
        adds the appropriate subsequent event to the Simulator event queue.
        '''
        
        # Unpack the argument list.
        [flow_name, packet_name] = argument_list
        packet = sim.packets[(flow_name, packet_name)]
        flow = sim.flows[flow_name]
        
        # Create an event to enqueue the packet on the link.
        self.link.enqueue_packet(self.host_name, \
                                 [self.host_name, flow_name, packet_name])
        
        if packet.type == PACKET_DATA:
            # Wait for timeout (defined as constant) to check that ack has been
            #   received for this packet.
            ack_timeout_time = e.Event(self, check_for_timeout, [flow_name, packet_name])
            heapq.heappush(sim.event_queue, (sim.network_now() + ACK_TIMEOUT, \
                                             ack_timeout_event))
                                             
            # If this packet is not in our packets_in_flight array, add it to it.
            #   It's not given that it is not in the array because this may be
            #   a packet resend.
            if argument_list not in flow.packets_in_flight:
                flow.packets_in_flight.append(argument_list)
                                         
                                         
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
        [flow_name, packet_name] = argument_list
        
        # For ease, get the packet and flow corresponding to these.
        packet = sim.packets[(flow_name, packet_name)]
        flow = sim.flows(flow_name)
        
        # If the packet ID is less than or equal to the last received, then
        #   ack has been received for this packet.  Otherwise, we must resend
        #   it.
        if int(packet.ID) <= flow.last_complete:
            return
            
        # If here, there was a timeout and we must resend the packets in flight
        for packet in flow.packets_in_flight:
            # Resend the packets in the list up to and including this lost one.
            self.send_packet(packet)
 
        
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
#                   2015/11/14: Responds according to packet type and ID.
#
        

    def receive_packet(self, argument_list):
        '''
        Receives a Packet from a Link.  Then, it adds the appropriate event to 
        the Simulator event queue.
        '''
        # Unpack the argument list.
        [flow_name, packet_name] = argument_list
        
        # Create a packet for the argued description.
        packet = sim.packets[(flow_name, packet_name)]
        flow = sim.flows[flow_name]
        print flow_name
        if packet.type == PACKET_DATA:
            # Check that it is the packet that this dest is "waiting for"
            if int(packet.ID) == flow.waiting_for:
                self.waiting_for += 1
            
            # Create acknowledgement packet.
            ack_packet = Packet(flow.waiting_for, packet.flow, \
                                self.host_name, packet.src, PACKET_ACK, \
                                PACKET_ACK_SIZE, sim.network_now())
            
            # Compute how long the host must wait to send acknowledgement.
            time_delay = 0
            
            # Create an event to send this packet.
            send_ack_event = Event(self, send_packet, [ack_packet.flow, ack_packet.ID])

            # Add send ack packet event to the simulation priority queue
            heapq.heappush(sim.event_queue, ((sim.network_now() + time_delay), \
                                              send_ack_event))
                                              
        elif packet.type == PACKET_ACK:
            # Check if it is the next packet we are waiting for.
            if flow.last_complete + 1 == packet.ID:
                # If it is, remove it from packets in flight
                flow.packets_in_flight.remove(argument_list)
                
                # Then, update the flow to reflect last packet received.
                flow.last_complete += 1
                
                # Send the next packet.
                if len(flow.packets_in_flight) < flow.window_size and \
                   flow.last_complete < cv.MB_to_bits(flow.size):
                    # Create the next packet.
                    next_pkt = p.Packet(flow.create_packet_ID, flow, flow.src, \
                                        flow.dest, PACKET_DATA, PACKET_DATA_SIZE)
                                        
                    # Send the next packet.
                    self.send_packet(packet)
                
            elif flow.last_complete >= packet.ID:
                # In this case, it is a packet that has already been received
                #   and accounted for.
                pass
                
            else:
                # Otherwise, we assume that the previous packets were lost, so
                #   resend them.
                for packet in flow.packets_in_flight:
                    self.send_packet(packet)
                
        
        
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
