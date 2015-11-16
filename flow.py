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
        self.packets = []

        # Python dictionary storing (flow_name, packet_name) representing 
        # Packet for this Flow that have been acknowledged
        #self.awaiting_ack = {}

        # Next unused packet ID
        self.next_packet_ID = 0

        # The last used packet ID for this flow.  The first packet ID should 
        # be 0, so a value of -1 implies no packets have been created yet.
        #self.last_packet_ID = -1
        
        # The numerical ID of the last packet that was sent and ack was received
        #   by the src
        self.last_complete = -1
        
        # The numerical ID of the packet that dest is waiting to receive next.
        self.waiting_for = 0
        
        # The round trip time for this flow.  This should be dynamic and
        #   dependent upon congestion.  It is here so we know when to check for
        #   acknowledgement timeouts.
        self.RTT = ct.INITIAL_ASSUMED_RTT

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

    
    #
    # create_data_packets
    #
    # Description:      This creates a queue of data packets based on the size of
    #                   the flow and the size of each packet.  The queue will 
    #                   contain every packet that is to be sent.
    #
    # Arguments:        self (Flow)
    #
    # Return Values:    None.
    #
    # Shared Variables: packets (WRITE) - This fills the queue with packets.
    # 
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/13/15: Created
    #

    def create_data_packets(self):
        '''
        Given the size of the Flow, create all the data Packet.
        '''
        num_packets = self.get_num_data_packets()
        for i in range(num_packets):
            packet_ID = self.create_packet_ID()

            # Create a new Packet
            packet = p.Packet(packet_ID, self.flow_name, self.src, self.dest, 
                              ct.PACKET_DATA, ct.PACKET_DATA_SIZE)
                              
            # Set the packet data.  The data in this case has the packet's
            #   original ID.  Hosts will check this data to see if it is the
            #   chronologically correct packet whereas the packet ID is used
            #   purely for identification.  The other piece is originally None
            #   but will eventually be the time of transmission from the source.
            packet.set_data([int(packet_ID), None])
            
            # Put the Packet into the queue/dictionary
            self.packets.append(packet)

            sim.packets[(self.flow_name, packet_ID)] = packet

            # Put the Packet identifier (key) and Packet itself into the 
            # awaiting_ack dictionary
            #self.awaiting_ack[(self.flow_name, packet_ID)] = packet

    
    #
    # get_num_data_packets
    #
    # Description:      This returns the number of data packets that need to be sent
    #                   in order to send all of the data that this flow needs to
    #                   send.
    #
    # Arguments:        self (Flow)
    #
    # Return Values:    (int) - The number of packets that need to be created/sent.
    #
    # Shared Variables: size (READ) - Used to determine how many packets need to be
    #                       created/sent.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/13/15: Created
    #

    def get_num_data_packets(self):
        '''
        Computes and returns the number of Packet required to send for this 
        Flow.
        '''
        return cv.MB_to_bits(self.size) // ct.PACKET_DATA_SIZE + 1
        
    
    #
    # check_flow_status
    #
    # Description:      This checks the status of the flow by comparing the number
    #                   of packets in flight to the window size.  If there are
    #                   fewer packets in flight than the window size, then this
    #                   enqueues events to put more packets in flight.  If there
    #                   are more packets in flight than the window size, this 
    #                   throws an assertion error.
    #
    # Arguments:        self (Flow)
    #
    # Return Values:    None.
    #
    # Shared Variables: packets_in_flight (READ/WRITE) - Read to check if any new
    #                       packets should be sent, written if new packets are sent.
    #                   window_size (READ) - Read to determine if packets should be
    #                       sent.
    #                   endpoints (READ) - Read to determine the host name of the
    #                       flow source.
    #                   flow_name (READ) - Used for identification purposes
    #
    # Global Variables: sim.event_queue (WRITE) - An event is added to this queue
    #                       whenever a packet needs to be put in flight.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/13/15: Created
    #                   11/16/15: Changed so that putting packets in flight no
    #                             longer pops from the packet queue.  Rather,
    #                             it reads and sends them and lets the ack
    #                             handler pop them.  This also now returns if
    #                             the queue is empty.
    #

    def check_flow_status(self):
        '''
        Sends Packet from the Host associated with this Flow as long as the 
        number of Packet in the network is less than the window size.  
        '''
        # If there are no packets in the queue, do nothing.  The flow is over.
        if len(self.packets) == 0:
            return
            
        # Make sure we don't have too many packets in flight.
        assert(self.packets_in_flight <= self.window_size)
        
        # Get the Host associated with this Flow
        host_name = sim.endpoints[self.src].host_name

        # We want the first <window_size> packets to be in flight.  If some are
        #   already in flight, we only want to send the ones in the first
        #   <window_size> that are not already in flight.
        for i in range(self.packets_in_flight, self.window_size - self.packets_in_flight):
            # Create a send event for the i-th packet in the queue.  It will be
            #   popped from the packets list once ack is received.
            packet_ID = self.packets[i].ID

            # Arguments to send_packet() as a list
            send_event_args = [self.flow_name, packet_ID]

            # Enqueue an event to transmit the Packet 
            transmit_event = e.Event(host_name, 'transmit_packet', send_event_args)

            # Slightly stagger (by 1/1000 ms) the send event for each Packet
            #print("cur time = " + str(sim.network_now()))
            send_time = sim.network_now() + ct.TIME_BIT 
            heapq.heappush(sim.event_queue, (send_time, transmit_event)) 

            self.packets_in_flight += 1
            
    
    #
    # resend_packets_in_flight
    #
    # Description:      This is called when something goes wrong and all packets
    #                   must be resent.  It looks for the packets in flight and
    #                   creates new packets for each one that is identical to the
    #                   one in flight, but with a different ID.  It then uses this
    #                   new packet to overwrite the old one, thereby "forgetting"
    #                   the one that has now been lost.  It then resets the 
    #                   counter for packets in flight and calls a function to bring
    #                   that number back up to the window size.
    #
    # Arguments:        self (Flow)
    #
    # Return Values:    None.
    #
    # Shared Variables: packets_in_flight (WRITE) - Resets this to zero.
    #                   packets (WRITE) - Overwrites the lost packets with new
    #                       packets to send.
    #
    # Global Variables: sim.packets (WRITE) - Adds the new packet(s) to the
    #                       global dictionary of packets.
    #
    # Limitations:      This assumes that the if there are x packets in flight,
    #                   they are the first x elements in the list of packets on
    #                   this flow.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/16/15: Created
    #
            
    def resend_packets_in_flight(self):
        '''
        This creates new packets for each packet in flight and sends those,
        effectively forgetting about the ones that were previously in flight.
        '''
        # Create new packets for all of the packets that were in flight.  The
        #   packets that are in flight are the first packets in the list of
        #   packets.
        for i in range(self.packets_in_flight):
            # Get the old packet so we can copy everything over.
            old_pkt = self.packets[i]
            
            # Create a new packet which is exactly the old one but with a unique
            #   ID
            new_pkt = p.Packet(self.create_packet_ID(), self.flow_name,
                               old_pkt.src, old_pkt.dest,
                               old_pkt.type, old_pkt.size)
            
            # Set the data of the new packet with the packet number of the old
            #   packet but no time (yet...)
            new_pkt.set_data([old_pkt.data[0], None])
            
            # Add this new packet to our dictionary of packets.
            sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
            
            # Overwrite the old packet in the list of packets to send.
            self.packets[i] = new_pkt
            
        # Now reset packets_in_flight to be none.
        self.packets_in_flight = 0
        
        # Check the flow status so we have as many packets in flight as our
        #   window size allows.
        self.check_flow_status()
        
        
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
