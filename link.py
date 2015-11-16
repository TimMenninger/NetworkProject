################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# link.py
#
# This contains the link class.  It has methods that enqueue packets then
# transmit them at calculated times.
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
import flow as f
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
#                                   Link Class                                 #
#                                                                              #
################################################################################

class Link:

    def __init__(self, the_link_name, the_rate, the_delay, the_buffer_size, the_endpoints):
        '''
        Initialize an instance of Link by intitializing its attributes.
        '''
        # Name of the Link, each name is a unique string (i.e. "L1")
        self.link_name = the_link_name
        
        # This is the index of the endpoint that data is flowing from.  If
        #   negative, there is no flow.
        self.flowing_from = -1

        # How fast the Router can send data (in MB/sec) 
        self.rate = the_rate

        # How much data can be stored in the buffer (in KB)
        self.buffer_size = the_buffer_size

        # Amount of time it takes to send Packet down link (in ms)
        self.delay = the_delay

        # Define the endpoints so we know how to define flow on this 
        # half-duplex link. Could be a Router or Host. 'the_endpoints' is 
        # passed in as a tuple of host_name and/or router_name
        self.end_points = { the_endpoints[0] : 0, the_endpoints[1] : 1 }
        self.ep_names = { 0 : the_endpoints[0], 1 : the_endpoints[1] }
        
        # The packet buffers on either end of the half-duplex link
        self.buffers = [ [], [] ]
        
        # The amount of data in the buffer in bits.
        self.buffer_load = [ 0, 0 ]
        
        # The number of packets on the link from the indexed endpoint.  One of
        #   these must be empty at all times because the link is half-duplex.
        self.packets_on_link = [ [], [] ]
        
        # If a packet is currently being moved from the buffer to the link,
        #   this is true.
        self.in_transmission = False       
        
    #
    # put_packet_on_buffer
    #
    # Description:      This takes a packet and if there is space on the buffer,
    #                   moves it onto the buffer.  If there is nothing on the
    #                   link or either buffer, it also puts it on the link.
    #
    # Arguments:        self (Link)
    #                   sender_name (string) - The name of the endpoing that
    #                       sent the packet.
    #                   packet (Packet) - The packet being sent.
    #
    # Return Values:    None.
    #
    # Shared Variables: self.buffers (WRITE) - This function enqueues a packet onto
    #                       one of the buffers (potentially).
    #                   self.end_points (READ) - This is read to determine which
    #                       buffer should be altered, if any.
    #                   self.buffer_load (WRITE) - This changes the buffer load
    #                       when adding to the buffer.
    #                   self.buffer_size (READ) - This is used to determine if there
    #                       is enough space on the buffer to enqueue a packet.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 2015/10/22: Created function handle and docstring
    #                   2015/10/29: Filled function in.
    #                   2015/11/03: Changed the link buffers to use the python queue
    #                               data structure and only store the flow_name and 
    #                               packet_name
    #
        
    def put_packet_on_buffer(self, sender_name, packet):
        '''
        Determine whether to put the packet on a buffer or on the link, then
        create events accordingly.
        '''
        # Get the index of the endpoint sender_name represents and then the
        #   index of the opposite endpoint.
        ep = self.end_points[sender_name]
        other_ep = (ep + 1) % 2
        
        # Put the packet onto the buffer heapqueue corresponding to the sender.
        #   The time we use for this will be now, because we are using first
        #   come first served priority on the links, but only if there is enough
        #   space.
        if packet.size + self.buffer_load[ep] <= self.buffer_size * (10 ** 3):
            heapq.heappush(self.buffers[ep], (sim.network_now(), packet.flow, packet.ID))
            self.buffer_load[ep] += packet.size
        
        # We now want to check if this should be sent right away.  The reason
        #   this is done here is because it is the best way to "kickstart" the
        #   link.  We want it to send right away if the buffer at the other end
        #   is empty and nothing is being transmitted on the buffer at the end
        #   it is on.  Being transmitted is defined as the time it takes to load
        #   a packet from the buffer onto the link.
        if len(self.buffers[other_ep]) == 0 and not self.in_transmission:
            self.put_packet_on_link([])
            
            
    #
    # reset_in_transmission
    #
    # Description:      Sets the in_transmission flag to 0 so more packets can
    #                   be loaded onto the link.
    #
    # Arguments:        self (Link)
    #                   unused_list (List) - Unused.
    #
    # Return Values:    None.
    #
    # Shared Variables: in_transmission (WRITE) - Written to False.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/16/15: Created
    #
            
    def reset_in_transmission(self, unused_list):
        '''
        Resets the flag that tells whether a packet is in transmission.
        '''
        self.in_transmission = False
            
            
    #
    # put_packet_on_link
    #
    # Description:      This puts a packet on the link.  It then enqueues some
    #                   events.  One will check after transmission time if there
    #                   is another packet that can go in the same direction.
    #                   One will check wait for transmission time then reset
    #                   the in_transmission flag.  One waits for the packet to
    #                   reach the other end to see if there is a packet waiting
    #                   to go the opposite direction, and the last is for the
    #                   other end to receive the packet.
    #
    # Arguments:        self (Link)
    #                   arg_list (List) - Unused.
    #
    # Return Values:    None.
    #
    # Shared Variables: buffers (READ/WRITE) - Read to see if there is anything
    #                       to put on the link, written if something is taken
    #                       off of the buffer to put on the link.
    #                   packets_on_link (READ/WRITE) - Read to see direction of
    #                       travel and written to put packets on the link.
    #                   in_transmission (WRITE) - Written to True when a packet
    #                       is being transmitted.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 2015/10/22: Created function handle and docstring
    #                   2015/10/29: Filled function in.
    #                   2015/11/03: Changed the link buffers to use the python queue
    #                               data structure and only store the flow_name and 
    #                               packet_name
    #                   2015/11/16: Now checks for next packet to put on link and
    #                               creates event for it.
    #
            
    def put_packet_on_link(self, arg_list):
        '''
        Decide which packet should be put on the link next and do it or create
        an event that will do it.
        '''
        # If there is a packet in transmission, we cannot put anything on the
        #   link.
        if self.in_transmission:
            return
            
        # If there are no packets in either buffer, then we have no business
        #   here.
        if len(self.buffers[0]) == 0 and len(self.buffers[1]) == 0:
            return
        
        # Find the direction of travel, which is the source of the data on the
        #   link.  If there is no source, then the data source is -1.
        data_src = 0
        if len(self.packets_on_link[0]) == 0 and len(self.packets_on_link[1]) == 0:
            data_src = -1
        elif len(self.packets_on_link[1]) > 0:
            data_src = 1
        
        # Check which buffer contains the packet that will be put on the link
        #   next.  We will use this to determine whether it goes on the link now
        #   or later (if it must oppose the direction of data).  Unfortunately,
        #   there is no good way of peeking, so we pop then push.
        if len(self.buffers[0]) == 0:
            # If there is nothing on the queue at 0, then the next packet must
            #   come from 1.
            next_pop = 1
        elif len(self.buffers[1]) == 0:
            # If there is nothing on the queue at 1, then the packt must come
            #   from 0.
            next_pop = 0
        else:
            # The next packet will be the first one that arrived.  If the two
            #   are equal, tie goes to the direction of data travel.  We thus
            #   get the time of entry for the next packet from either buffer.
            [time0, temp1, temp2] = heapq.heappop(self.buffers[0])
            heapq.heappush(self.buffers[0], (time0, temp1, temp2))
            
            [time1, temp1, temp2] = heapq.heappop(self.buffers[1])
            heapq.heappush(self.buffers[0], (time1, temp1, temp2))
            
            # If the two times are equal, keep sending data in the direction of
            #   travel.  Otherwise, send the oldest (smallest time) packet.
            next_pop = 0
            if time0 == time1:
                next_pop = data_src
            elif time1 < time0:
                next_pop = 1
                
        # Now that we know the source of the next packet, we know if it goes on
        #   right away.  If the next packet will go in the same direction of 
        #   travel as the other packets, put it on the link.  Otherwise, we must
        #   wait until the link is clear to send it the opposite direction.
        if next_pop == data_src or data_src == -1:
            # We are sending a packet, so set the in_transmission flag.
            self.in_transmission = True
            
            # The next packet will go in the same direction as data on the link.
            [time, flow_name, packet_ID] = heapq.heappop(self.buffers[next_pop])
            
            # Put it on the link, but use the current time so we can heapify
            #   more easily.  Subtract from the buffer load to reflect it.
            heapq.heappush(self.packets_on_link[next_pop],
                           (sim.network_now(), flow_name, packet_ID))
            self.buffer_load[next_pop] -= sim.packets[(flow_name, packet_ID)].size
            
            # Calculate the transmission time as the size of the packet divided
            #   by the link capacity (aka rate).
            transmission_time = cv.bits_to_MB(sim.packets[(flow_name, packet_ID)].size) / self.rate
            
            # Create an event after this packet's transmission to reset the
            #   in_transmission flag.  Subtract a small amount of time to assure
            #   it happens before the next call of this function.
            reset_time = sim.network_now() + transmission_time - ct.TIME_BIT
            reset_event = e.Event(self.link_name, 'reset_in_transmission', [])
            sim.enqueue_event(reset_time, reset_event)
            
            # Create an event to check if we should send another packet after
            #   transmission.
            pkt1_time = sim.network_now() + transmission_time
            pkt1_event = e.Event(self.link_name, 'put_packet_on_link', [])
            sim.enqueue_event(pkt1_time, pkt1_event)
            
            # If we are not sending another packet after transmission, we need
            #   to also have an event that checks after propagation.  Because we
            #   do not know yet, we must make the event no matter what.
            pkt2_time = pkt1_time + self.delay
            pkt2_event = e.Event(self.link_name, 'put_packet_on_link', [])
            sim.enqueue_event(pkt2_time, pkt2_event)
            
            # Enqueue the event for the opposite end to receive the packet.
            #   This occurs at the same time as the transmission plus delay
            #   event.
            rcv_time = pkt2_time
            rcv_event = e.Event(self.link_name, 'handoff_packet', [next_pop])
            sim.enqueue_event(rcv_time, rcv_event)
            
            
    def handoff_packet(self, list_sender):
        '''
        This changes a few variables related to the packet being taken off of
        the link before allowing the host/router to handle the packet.
        '''
        # Unpack the argument list, which has the sender in it.
        [sender_index] = list_sender
        
        # Take the packet off of the link by removing it from the queue.
        [time, flow_name, packet_ID] = \
                heapq.heappop(self.packets_on_link[sender_index])
                
        # Use the sender index to figure out the receiver index.
        rcv_index = (sender_index + 1) % 2
        
        # Now "hand off" the packet to the host.
        ep = sim.endpoints[self.ep_names[rcv_index]]
        ep.receive_packet([flow_name, packet_ID])
        
        
        
        
        
        
        
        
    
