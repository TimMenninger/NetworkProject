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
#

    def send_packet(self, argument_list):
        '''
        Sends a Packet from this Host to a particular destination.  Then, it 
        adds the appropriate subsequent event to the Simulator event queue.
        '''
        
        # Unpack the argument list.
        [flow_name, packet_name] = argument_list
        
        # Create an event to enqueue the packet on the link.
        self.link.enqueue_packet(self.host_name, flow_name, packet_name)
        
        
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
        
        if packet.type == PACKET_DATA:
            # Create acknowledgement packet.
            ack_packet = Packet(flow.create_ID(), packet.flow,
                                self.host_name, packet.src, PACKET_ACK,
                                PACKET_ACK_SIZE, sim.network_now())
            
            # Compute how long the host must wait to send acknowledgement.
            time_delay = 0
            
            # Create an event to send this packet.
            send_ack_event = Event(self, send_packet, [ack_packet.flow, ack_packet.ID])

            # Add send ack packet event to the simulation priority queue
            heapq.heappush(sim.event_queue, ((sim.network_now() + time_delay), 
                                              send_ack_event))
        
        
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
