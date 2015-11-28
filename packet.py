############################################################################
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
############################################################################

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

# Import the simulate module.
import sys
sim = sys.modules['__main__']


############################################################################
#                                                                          #
#                                  Packet Class                            #
#                                                                          #
############################################################################


class Packet:

    def __init__(self, in_ID, in_flow, in_src, in_dest, in_type):
        '''
        Description:        Initialize an instance of Packet by intitializing 
                            its attributes.

        Arguments:          in_ID (integer)
                                - An integer that is the ID of the Packet; it 
                                is combined with the flow name to uniquely
                                idenitfy this Packet object.

                            in_flow (string)
                                - A string indicating the name of the Flow 
                                that this Packet instance belongs to.  It, 
                                along with the packet_ID uniquely identifies a 
                                Packet.

                            in_src (string)
                                - A string indicating the host name of the 
                                source of the Packet (i.e., "H1").

                            in_dest (string)
                                - A string indicating the host name of the 
                                destination Host of the Packet (i.e., "H2").

                            in_type (integer)
                                - An integer constant defined in constants.py
                                that defines the type of Packet for this 
                                Packet.

        Shared Variables:   self.ID (WRITE) 

                            self.flow (WRITE)

                            self.src (WRITE)

                            self.dest (WRITE)

                            self.type (WRITE)

                            self.size (WRITE)             (not init argument)

                            self.time (WRITE)             (not init argument)
        
                            self.data (WRITE)             (not init argument)

        Global Variables:   None.

        Limitations:        The 'src' and 'dest' parameters can be fetched from 
                            the 'flow' attribute and do not need to be their 
                            own separate command-line argument.  Fixing this 
                            limitation is not a high-priority fix at the 
                            moment.

        Known Bugs:         None.

        Revision History:   10/03/15: Created
        '''
        # Store the type so we can easily identify the object.
        self.type = ct.TYPE_PACKET
        
        # ID of the Link, each ID is a unique string (i.e. "P1")
        self.ID = in_ID

        # Flow that the Packet belongs to 
        # Gives access to source and destination, uniquely identifies Packet
        self.flow = in_flow

        # Host/Router sending the Packet
        self.src = in_src

        # Host/Router to receive the Packet
        self.dest = in_dest

        # Constant representing the type of Packet being sent 
        # PACKET_DATA, PACKET_ACK, PACKET_ROUTING
        self.type = in_type

        # Integer representing the size of the Packet, dependent on its type
        # PACKET_DATA_SIZE, PACKET_ACK_SIZE, or PACKET_ROUTING_SIZE
        self.size = ct.PACKET_DATA_SIZE
        if self.type == ct.PACKET_ACK:
            self.size = ct.PACKET_ACK_SIZE
        elif self.type == ct.PACKET_ROUTING:
            self.size = ct.PACKET_ROUTING_SIZE
        
        # The time of transmission from src.  -1 means not transmitted
        self.time = -1
        
        # The data is usually a marker so we have some sense of chronology of
        #   packets
        self.data = None
        
        
    def copy_packet(self):
        '''
        Description:        Returns a copy of the argued packet.
        
        Arguments:          None.
        
        Return Values:      Packet
                                - An exact copy of this Packet object.
        
        Shared Variables:   self.flow (READ) 
                                - Used to initialize another duplicate Packet.

                            self.src (READ) 
                                - Used to initialize another duplicate Packet.

                            self.dest (READ) 
                                - Used to initialize another duplicate Packet.

                            self.type (READ)
                                - Used to initialize another duplicate Packet.

        Global Variables: None.
        
        Revision History: 11/26/15: Created
        '''
        copy_pkt = Packet(sim.flows[self.flow].create_packet_ID(), self.flow,
                            self.src, self.dest, self.type)
                            
        # Copy the other data over.
        copy_pkt.time = self.time
        copy_pkt.set_data(self.data)
        
        # Add it to the global dictionary of packets.
        sim.packets[(copy_pkt.flow, copy_pkt.ID)] = copy_pkt
        
        return copy_pkt
        
        
    def set_data(self, pkt_data):
        '''
        Description:        Sets the data of the packet.
        
        Arguments:          pkt_data (Any) 
                                - The data carried by this packet.
        
        Return Values:      None.
        
        Shared Variables:   self.data (WRITE) - Updated according to arguments.
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/02: Created
        '''
        self.data = pkt_data
        
        
 