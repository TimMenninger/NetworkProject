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


# Notes from meeting with Ritty
# Flow: 
#    window_size = 16
#    packets_in_network = k

# if k < 16:
#       send packet 
#       k++

# Every time a packet is sent, a retransmission timeout event must be spurred
#     timeout after 2 * (round trip time)


# Need a singleton logger class
# logger.log("L1", "Drop", "Time")
# each keyword indicates which log file it's being logged to
# separate csv log file for packets dropped
# separate csv log file for throughput
# separate csv log file for window size


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
import host as h
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
        self.window_size = 16

        # List of packets in the network
        self.packets_in_flight = 0
        
        # Packet asssociated with this flow are stored in a Queue
        self.packets = queue.Queue()

        # Python dictionary storing (flow_name, packet_name) representing 
        # Packet for this Flow that have been acknowledged
        self.awaiting_ack = {}

        # 
        self.next_packet_ID = 0

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
        self.create_data_packets()
        self.check_flow_status()

    def create_data_packets(self):
        '''
        Given the size of the Flow, create all the data Packet.
        '''
        num_packets = self.get_num_data_packets()
        for i in range(num_packets):
            packet_ID = self.create_packet_ID()

            # Create a new Packet
            packet = p.Packet(packet_ID, self, self.src, self.dest, 
                              ct.PACKET_DATA, ct.PACKET_DATA_SIZE)
            
            # Put the Packet into the queue
            self.packets.put(packet)

            sim.packets[(self.flow_name, packet_ID)] = packet

            # Put the Packet identifier (key) and Packet itself into the 
            # awaiting_ack dictionary
            self.awaiting_ack[(self.flow_name, packet_ID)] = packet

    def get_num_data_packets(self):
        '''
        Computes and returns the number of Packet required to send for this 
        Flow.
        '''
        return cv.MB_to_bits(self.size) // ct.PACKET_DATA_SIZE + 1

    def check_flow_status(self):
        '''
        Sends Packet from the Host associated with this Flow as long as the 
        number of Packet in the network is less than the window size.  
        '''
        # Get the Host associated with this Flow
        host_name = sim.endpoints[self.src].host_name

        while self.packets_in_flight < self.window_size:
            # Pop the Packet off the queue and create a send event for it
            packet_ID = self.packets.get().ID

            # Arguments to send_packet() as a list
            send_event_args = [self.flow_name, packet_ID]

            # Enqueue an event to transmit the Packet 
            transmit_event = e.Event(host_name, 'transmit_packet', send_event_args)

            # Slightly stagger (by 1/1000 ms) the send event for each Packet
            print("cur time = " + str(sim.network_now()))
            send_time = sim.network_now() + ct.TIME_BIT 
            heapq.heappush(sim.event_queue, (send_time, transmit_event)) 

            self.packets_in_flight += 1
        
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
        
        # Return the ID.
        self.next_packet_ID += 1
        return str(self.next_packet_ID - 1)
