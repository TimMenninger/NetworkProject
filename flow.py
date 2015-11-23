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

        # host_name of source Host, a string
        self.src = the_src

        # host_name of destination Host, a string
        self.dest = the_dest

        # Amount of data being sent, an int (in bytes)
        self.size = the_size

        # Window size as computed.
        self.window_size = ct.INITIAL_WINDOW_SIZE
        
        # The time the flow is starting.
        self.start_time = the_start_time
        
        # The packets that must be sent.
        self.packets_to_send = []
        
        # The packets that are in flight.
        self.packets_in_flight = []
        
        # Every number less than this has been used as an ID.
        self.next_available_ID = 1
        
        # The next chronological packet that the dest expects from the src.
        self.expecting = 1
        
        # The next chronological packet the source is looking to receive
        #   ack for (i.e. every packet whose data is strictly less than
        #   this has been acknowledged)
        self.to_complete = 1
        
        # Keep track of the round trip time a packet has taken so we can
        #   guage an appropriate timeout-check delay.  Before any acks are
        #   received, this is more of a blind guess.
        self.last_RTT = ct.INITIAL_ASSUMED_RTT
        
        
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
        Returns an ID that is not currently in use by any other packet.
        '''
        self.next_available_ID += 1
        return self.next_available_ID - 1
        
        
    #
    # start_flow
    #
    # Description:      This starts the flow by creating all of the packets in 
    #                   the flow and then starting to send them.
    #
    # Arguments:        self (Flow)
    #                   unused_list (List) - Unused
    #
    # Return Values:    None.
    #
    # Shared Variables: self.size (READ) - Used to determine how many packets to
    #                       create.
    #
    # Global Variables: sim.packets (WRITE) - New packets are written to the
    #                       global dictionary.
    #
    # Limitations:      None.
    #
    # Known Variables:  None.
    #
    # Revision History: 11/16/15: Created
    #
        
    def start_flow(self, unused_list):
        '''
        Starts the flow by creating all of the packets to send then starting to
        send them.
        '''
        # Calculate the number of packets we need to send all of the data
        num_packets = int(cv.MB_to_bytes(self.size) / ct.PACKET_DATA_SIZE) + 1
        
        # Create all of the packets.
        for i in range(1, num_packets + 1):
            # First, create a packet.
            new_pkt = p.Packet(self.create_packet_ID(), self.flow_name, 
                               self.src, self.dest,
                               ct.PACKET_DATA, ct.PACKET_DATA_SIZE)
                               
            # Set the data of the packet to be its "chronological" number.
            new_pkt.set_data(i)
                               
            # Put the packet into the heapqueue.
            heapq.heappush(self.packets_to_send, (i, new_pkt))
            
            # Put the packet into the global dictionary of packets.
            sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
            
        # Update the flow so that we have packets in motion.
        self.update_flow()
        
        
    #
    # resend_inflight_packets
    #
    # Description:      Creates copies of all of the in flight packets and
    #                   resends them all.  The reason we create new packets
    #                   is so we don't get confused when old packets that
    #                   we thought were lost arrive.
    #
    # Arguments:        self (Flow)
    #
    # Return Values:    None.
    #
    # Shared Variables: packets_in_flight (WRITE) - This is overwritten
    #                       to contain all of the new packets.
    #                   flow_name (READ) - Used to index packets in the
    #                       global dictionary.
    #
    # Global Variables: sim.packets (WRITE) - The new packets are written
    #                       to this dictionary.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/16/15: Created
    #
        
    def resend_inflight_packets(self):
        '''
        This remakes and resends all packets that are currently in flight.
        '''
        # Create a new queue of packets in flight
        old_flight = self.packets_in_flight[:]
        self.packets_in_flight = []
        
        # Remove all of the packets in flight, make a new packet out of them
        #   and resend.  We are making a new packet so it has a new ID.  If
        #   we didn't do this, we wouldn't be able to index packets in the
        #   dictionary anymore, which is important because the timestamps will
        #   be different.
        while len(old_flight) > 0:
            # Remove an element and make a new packet from it.
            (old_num, old_pkt) = heapq.heappop(old_flight)
            
            # Create a new packet from it but with a new ID.
            new_pkt = p.Packet(self.create_packet_ID(), self.flow_name,
                               old_pkt.src, old_pkt.dest, old_pkt.type,
                               old_pkt.size)

            # Make sure the new packet contains the same data (index)
            new_pkt.set_data(old_pkt.data)
            
            # Add it to the new queue of packets.
            heapq.heappush(self.packets_in_flight, (new_pkt.data, new_pkt))
            
            # Add it to the dictionary of packets.
            sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
            
            # Create an event to send this packet.
            send_event = e.Event(new_pkt.src, 'send_packet', [new_pkt])
            sim.enqueue_event(sim.network_now(), send_event)
        
        
    #
    # update_flow
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
    #                   packets_to_send (WRITE) - Packets that are to be sent are
    #                       popped from this queue.
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
    #   
            
    def update_flow(self):
        '''
        Updates the window size according to congestion and the packets in
        flight according to window size.
        '''
        # If there are no packets to send, the flow is done.
        if len(self.packets_to_send) == 0:
            return
        
        sim.log.write("[%.5f] %s: in-flight / window size %d/%d\n" %
            (sim.network_now(), self.flow_name, len(self.packets_in_flight), 
                self.window_size))

        while len(self.packets_in_flight) < self.window_size:
            # Get a packet from the list of packets to send.
            (pkt_num, pkt) = heapq.heappop(self.packets_to_send)

            # Put it in flight.
            heapq.heappush(self.packets_in_flight, (pkt_num, pkt))
            
            # Tell the host to send the packet by creating an event for it.
            send_time = sim.network_now() + ct.TIME_BIT
            send_event = e.Event(self.src, 'send_packet', [pkt])
            sim.enqueue_event(send_time, send_event)
        
        sim.log.write("[%.5f] %s: in-flight / window size %d/%d\n" %
            (sim.network_now(), self.flow_name, len(self.packets_in_flight), 
                self.window_size))
        
