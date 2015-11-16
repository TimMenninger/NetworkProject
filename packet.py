#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# packet.py
#
# This contains the packet class, which is the data structure that represents
# the actual data being transmitted in the simulated network.
#

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

class Packet:

    def __init__(self, the_ID, the_flow, the_src, the_dest, the_type, the_size):
        '''
        Initialize an instance of Packet by intitializing its attributes.
        '''
        # ID of the Link, each ID is a unique string (i.e. "P1")
        self.ID = the_ID

        # Flow that the Packet belongs to 
        # Gives access to source and destination, uniquely identifies Packet
        self.flow = the_flow

        # Host/Router sending the Packet
        self.src = the_src

        # Host/Router to receive the Packet
        self.dest = the_dest

        # Constant representing the type of Packet being sent 
        # PACKET_DATA, PACKET_ACK, PACKET_ROUTING
        self.type = the_type

        # Integer representing the size of the Packet, dependent on its type
        # PACKET_DATA_SIZE, PACKET_ACK_SIZE, or PACKET_ROUTING_SIZE
        self.size = the_size
        
        # The time of transmission from src.  -1 means not transmitted
        self.time = -1
        
        # The data is usually a marker so we have some sense of chronology of
        #   packets
        self.data = None
        
        
    #
    # set_data
    #
    # Description:      Sets the data of the packet.
    #
    # Arguments:        self (Packet)
    #                   data (Any) - The data carried by this packet.
    #
    # Return Values:    None.
    #
    # Shared Variables: self.data (WRITE) - Updated according to arguments.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 2015/11/02: Created
    #
        
    def set_data(self, pkt_data):
        '''
        Sets the data for the packet.
        '''
        self.data = pkt_data
        
        
        
        
        
        
        
