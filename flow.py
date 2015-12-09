############################################################################
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
############################################################################


############################################################################
#                                                                          #
#                               Imported Modules                           #
#                                                                          #
############################################################################

# So we can use command line arguments.
import sys

# So we can copy heapqueues.
import copy

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


############################################################################
#                                                                          #
#                                   Flow Class                             #
#                                                                          #
############################################################################


class Flow:

    def __init__(self, in_flow_name, in_src, in_dest, in_size, in_start_time):
        '''
        Description:        Initialize an instance of Flow by intitializing 
                            its attributes.

        Arguments:          in_flow_name (string)
                                - A string indicating the name of this Flow 
                                instance (i.e., "F1").

                            in_src (string)
                                - A string indicating the host name of the Host
                                that is sending the data for this particular 
                                Flow instance (i.e., "H3")

                            in_dest (string)
                                - A string indicating the host name of the Host
                                that is receiving the data for this particular 
                                Flow instance (i.e., "H2")

                            in_size (int)
                                - An int indicating how much data is being 
                                sent for this particular Flow object (in MB, 
                                i.e., 20).

                            in_start_time (float)
                                - A float indicating the start time of this 
                                Flow instance (i.e., 4.567)

        Shared Variables:   self.type (WRITE)              (not init argument)
                                - Initialized
                            
                            self.flow_name (WRITE) 
                                - Initialized
                            
                            self.src (WRITE) 
                                - Initialized

                            self.dest (WRITE) 
                                - Initialized

                            self.size (WRITE)
                                - Initialized

                            self.window_size (WRITE)       (not init argument)
                                - Initialized

                            self.start_time (WRITE)
                                - Initialized

                            self.packets_to_send (WRITE)   (not init argument)    
                                - Initialized

                            self.packets_in_flight (WRITE) (not init argument) 
                                - Initialized 

                            self.next_available_ID (WRITE) (not init argument)
                                - Initialized 

                            self.expecting (WRITE)         (not init argument)
                                - Initialized

                            self.to_complete (WRITE)       (not init argument)
                                - Initialized

                            self.acked_packets (WRITE)     (not init argument)
                                - Initialized

                            self.last_RTT (WRITE)          (not init argument)
                                - Initialized

        Global Variables:   None.

        Limitations:        None.

        Known Bugs:         None.

        Revision History:   10/06/15: Created
        '''
        # Store the type so it can be easily identified as a router.
        self.type = ct.TYPE_FLOW
        
        # Name of the Flow, each ID is a unique string (i.e. "F1")
        self.flow_name = in_flow_name

        # host_name of source Host, a string
        self.src = in_src

        # host_name of destination Host, a string
        self.dest = in_dest

        # Amount of data being sent, an int (in bytes)
        self.size = in_size

        # Window size as computed.
        self.window_size = ct.INITIAL_WINDOW_SIZE
        
        # The time the flow is starting.
        self.start_time = in_start_time
        
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

        # The number of packets that have been acknowledged in this record
        #   interval.  Used to compute flow rate.
        self.acked_packets = 0
        
        # This is the assumed RTT, which is only relevant when we have not
        #   yet received any packets and are still guessing the RTT.
        self.assumed_RTT = ct.INITIAL_ASSUMED_RTT
        
        # Keep track of the round trip time a packet has taken so we can
        #   guage an appropriate timeout-check delay.  Before any acks are
        #   received, this is more of a blind guess.
        self.last_RTT = 0

        # Keep track of the minimum RTT up until this point for Fast TCP
        self.min_RTT = 0

        # Keep track of average RTT over update period for FAST TCP. The 
        #   tuple is (cum_RTT, num_RTT's observed)
        self.avg_RTT = (0, 0)

        # The state that the flow is currently in. 0 = slow-start and  
        #   1 = congestion avoidance. Default set for slow-start phase
        self.state = 0

        # The slow-start threshold for the flow. Initially set to be infinity
        self.sst = float("inf")

        # Tuple to represent the last received ack # and # of duplicate acks
        self.num_dup_acks = (0, 0)

        # The congestion control algorithm used to update window size on this
        #   flow.
        self.congestion_alg = ct.DEFAULT_ALG

        # Keep track of time of last dropped packet update so we have a buffer 
        #   period that avoids too many successive window updates.
        self.last_update = 0.0

    
    def periodic_window_update(self, unused_list):
        '''
        Description:        This will update window size according to FAST TCP
        
        Arguments:          self (Flow)
        
        Return Values:      None.
        
        Shared Variables:   self.last_RTT (READ) 
                                - This is the previous RTT time computed 
                                for the flow.

                            self.min_RTT (READ) 
                                - This is the minimum RTT time that has 
                                been computed up to this point.

                            self.window_size (WRITE) 
                                - This is the window size of the flow, that 
                                will be updated according to FAST TCP
        
                            self.avg_RTT (READ/WRITE) 
                                - This has cum_RTT over last update period 
                                from which we can compute the average_RTT 
                                for the FAST TCP window update. It will be 
                                reset to (0,0) at the end of update

        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/12/07: Created
        '''
        # Enqueue event for updating flow, this will cause window to be updated 
        #   periodically. There must be more than one flow running for this 
        #   event to be enqueued.
        if len(sim.running_flows) > 1:
            FAST_TCP_update = e.Event(self.flow_name, 'periodic_window_update', [])
            update_time = sim.network_now() + ct.FAST_TCP_PERIOD
            sim.enqueue_event(update_time, FAST_TCP_update)
        
        # Unpack avg_RTT so we can compute the average_RTT
        (cum_RTT, num_RTTs) = self.avg_RTT
        # If there are no RTTs, we have no information to update the flow with.
        if num_RTTs != 0:
            average_RTT = cum_RTT / num_RTTs

            if average_RTT != 0:
                self.window_size = self.window_size * (self.min_RTT / average_RTT) \
                                   + ct.ALPHA_VALUE
                                   
        # Reset the metrics used to update the flow for FAST TCP
        self.avg_RTT = (0, 0)        
        
    def create_packet_ID(self):
        '''
        Description:        This creates a unique ID for a packet in this flow.
        
        Arguments:          self (Flow)
        
        Return Values:      (integer) 
                                - The unique ID that can be used for a new 
                                packet.
        
        Shared Variables:   self.next_packet_ID (WRITE) 
                                - This is incremented so we know what the next 
                                unused packet ID is next time an ID is 
                                requested.
        
        Global Variables:   None.
        
        Limitations:        Once a packet is destroyed, this has no way of 
                            knowing that the associated ID has freed up.  
                            Therefore, this always returns the lowest 
                            never-used ID, not necessarily the lowest unused 
                            ID.  Fixing this limitation is not a high-priority
                            at the moment.
        
        Known Bugs:         None.
        
        Revision History:   2015/10/29: Created
        '''

        self.next_available_ID += 1
        return self.next_available_ID - 1
        
 
    def start_flow(self, unused_list):
        '''
        Description:        This starts the flow by creating all of the packets 
                            in the flow and then starting to send them.
        
        Arguments:          unused_list (List) 
                                - Unused.
        
        Return Values:      None.
        
        Shared Variables:   self.size (READ) 
                                - Used to determine how many packets to create.
        
        Global Variables:   sim.packets (WRITE) 
                                - New packets are written to the global 
                                dictionary.
        
        Limitations:        None.
        
        Known Variables:    None.
        
        Revision History:   11/16/15: Created
        '''

        # Call periodic_window_update initially so that periodic window update can 
        #   be enqueued, to start the periodic updates
        if self.congestion_alg == ct.FLOW_FAST_TCP:
            self.periodic_window_update([])

        # Calculate the number of packets we need to send all of the data
        num_packets = int(cv.MB_to_bytes(self.size) / ct.PACKET_DATA_SIZE) + 1
        
        # Create all of the packets.
        for i in range(1, num_packets):
            # First, create a packet.
            new_pkt = p.Packet(self.create_packet_ID(), self.flow_name, 
                               self.src, self.dest, ct.PACKET_DATA)
                               
            # Set the data of the packet to be its "chronological" number.
            new_pkt.set_data(i)
                               
            # Put the packet into the heapqueue.
            heapq.heappush(self.packets_to_send, (i, new_pkt))
            
            # Put the packet into the global dictionary of packets.
            sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
            
        # Update the flow so that we have packets in motion.
        self.update_flow()
        
        
    def resend_inflight_packets(self):
        '''
        Description:        Creates copies of all of the in flight packets and
                            resends them all.  The reason we create new packets
                            is so we don't get confused when old packets that
                            we thought were lost arrive.
        
        Arguments:          None.
        
        Return Values:      None.
        
        Shared Variables:   packets_in_flight (WRITE) 
                                - This is overwritten to contain all of the 
                                new packets.
                          
                            flow_name (READ) 
                                - Used to index packets in the global 
                                dictionary.
        
        Global Variables:   sim.packets (WRITE) 
                                - The new packets are written to this 
                                dictionary.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   11/16/15: Created
        '''
        
        # Create a new queue of packets in flight
        old_flight = copy.deepcopy(self.packets_in_flight)
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
                               old_pkt.src, old_pkt.dest, old_pkt.type)

            # Make sure the new packet contains the same data (index)
            new_pkt.set_data(old_pkt.data)
            
            # Set the time of this new packet to be the current time so we can
            #   determine the round trip time later.
            new_pkt.time = sim.network_now()
            
            # Add it to the new queue of packets.
            heapq.heappush(self.packets_in_flight, (new_pkt.data, new_pkt))
            
            # Add it to the dictionary of packets.
            sim.packets[(self.flow_name, new_pkt.ID)] = new_pkt
            
            # Create an event to send this packet.
            send_event = e.Event(new_pkt.src, 'send_packet', [new_pkt])
            sim.enqueue_event(sim.network_now(), send_event)

            
    def update_flow(self):
        '''
        Description:            This checks the status of the flow by comparing 
                                the number of packets in flight to the window 
                                size. If there are fewer packets in flight 
                                than the window size, then this enqueues 
                                events to put more packets in flight.  
                                If there are more packets in flight than the 
                                window size, this throws an assertion error.
        
        Arguments:              None.
        
        Return Values:          None.
        
        Shared Variables:       packets_in_flight (READ/WRITE) 
                                    - Read to check if any new packets should 
                                    be sent, written if new packets are sent.

                                window_size (READ) 
                                    - Read to determine if packets should be 
                                    sent.

                                packets_to_send (WRITE) 
                                    - Packets that are to be sent are popped 
                                    from this queue.

                                flow_name (READ) 
                                    - Used for identification purposes.
        
        Global Variables:       sim.event_queue (WRITE) 
                                    - An event is added to this queue whenever 
                                    a packet needs to be put in flight, and to 
                                    account for window updates in the case of 
                                    FAST TCP being used.
        
        Limitations:            None.
        
        Known Bugs:             None.
        
        Revision History:       11/13/15: Created
        '''

        sim.log_flow.write("[%.5f]: Updating %s\n" % 
                          (sim.network_now(), self.flow_name))
        sim.log_flow.write("\tin-flight / window size: %d/%d (Before)\n" %
                          (len(self.packets_in_flight), self.window_size))

        while len(self.packets_in_flight) < self.window_size:
            # If there are no packets to send, the flow is done.
            if len(self.packets_to_send) == 0:
                # Remove it from our list ofrunning packets.  If it does not 
                #   work, we already deleted it, so continue normally.
                try:
                    sim.running_flows.remove(self.flow_name)
                    self.window_size = 0
                except ValueError:
                    pass
                return
                
            # Get a packet from the list of packets to send.
            (pkt_num, pkt) = heapq.heappop(self.packets_to_send)
            
            # Set the time of the packet so we can calculate the round trip
            #   time upon reception of this packet's ack.
            pkt.time = sim.network_now()

            # Put it in flight.
            heapq.heappush(self.packets_in_flight, (pkt_num, pkt))
            
            # Tell the host to send the packet by creating an event for it.
            send_time = sim.network_now() + ct.TIME_BIT
            send_event = e.Event(self.src, 'send_packet', [pkt])
            sim.enqueue_event(send_time, send_event)
        
        sim.log_flow.write("\tin-flight / window size: %d/%d (After)\n" %
                          (len(self.packets_in_flight), self.window_size))
        

        
