################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# flow.py
#
# This contains the flow class.  The flow is an abstract concept used to 
# simplify the notion of sending packets from a source to a destination.  
# Congestion control algorithms determine when and how many packets are sent 
# at any given time during the simulation.
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


################################################################################
#                                                                              #
#                                   Flow Class                                 #
#                                                                              #
################################################################################

class Flow:

    def __init__(self, the_flow_name, the_src, the_dest, the_size, the_start_time):
        '''
        Initialize an instance of Flow by intitializing its attributes.
        '''
        # Name of the Flow, each ID is a unique string (i.e. "F1")
        self.flow_name = the_flow_name
        
        # The time the flow is to start.
        self.start_time = the_start_time

        # host_name of source Host, a string
        self.src = the_src

        # host_name of destination Host, a string
        self.dest = the_dest

        # Amount of data being sent, an int (in MB)
        self.size = the_size

        # Window size as computed 
        self.window_size = 0

        # List of packets in the network
        self.packets_in_flight = []
        
        # The last used packet ID for this flow.  The first packet ID should 
        # be 0, so a value of -1 implies no packets have been created yet.
        self.last_packet_ID = -1
        
    
#
# start_flow
#
# Description:      This is what is called when the flow is to be begun.  It
#                   will enqueue the necessary events to start the flow and
#                   begin including it on congestion control.
#
# Arguments:        self (Flow)
#                   unused_list (List) - Here because of event class structure.
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
        
    def start_flow(self, unused_list):
        '''
        Begins the flow.  The argument is unused.
        '''

        
#
# set_algorithm
#
# Description:      This sets the attribute that indicates which algorithm to
#                   use for congestion control.
#
# Arguments:        self (Flow)
#                   algorithm (integer) - Probably a defined constant.  This
#                       will indicate which algorithm to use.
#
# Return Values:    None.
#
# Shared Variables: self.algorithm (WRITE) - This value is updated according
#                       to the argued value.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#

    def set_algorithm(self, algorithm):
        '''
        Sets the algorithm we are using for congestion control.
        '''
        self.algorithm = algorithm
        
        
#
# create_packet_ID
#
# Description:      This creates a unique ID for a packet in this flow.
#
# Arguments:        self (Flow)
#
# Return Values:    (integer) - The unique ID that can be used for a new packet.
#
# Shared Variables: self.next_packet_ID (WRITE) - This is incremented so we know
#                       what the next unused packet ID is next time an ID is
#                       requested.
#
# Global Variables: None.
#
# Limitations:      Once a packet is destroyed, this has no way of knowing that
#                       the associated ID has freed up.  Therefore, this always
#                       returns the lowest never-used ID, not necessarily the
#                       lowest unused ID.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#
        
    def create_packet_ID(self):
        '''
        Returns an unused ID for a packet.
        '''
        # Increment the ID to get the next unused packet ID.
        self.next_packet_ID += 1
        
        # Return the ID.
        return str(self.next_packet_ID)
        
        
#
# print_contents
#
# Description:      Prints the attributes and their contained values.  This is
#                   used mainly for debugging purposes.
#
# Arguments:        self (Flow)
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
