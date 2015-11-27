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

    def __init__(self, the_link_name, the_rate, the_delay, the_buffer_size, 
                 the_endpoints):
        '''
        Initialize an instance of Link by intitializing its attributes.
        '''
        # Store the type so it can be easily identified as a router.
        self.type = ct.TYPE_LINK
        
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
        
        # The packet buffers on either end of the half-duplex link (heapq's)
        self.buffers = [ [], [] ]
        
        # The amount of data in the buffer in bytes.
        self.buffer_load = [ 0, 0 ]
        
        # The number of packets on the link from the indexed endpoint.  One of
        #   these must be empty at all times because the link is half-duplex.
        self.packets_on_link = [ [], [] ]
        
        # The amount of data on the link in MB
        self.data_on_link = 0
        
        # If a packet is currently being moved from the buffer to the link,
        #   this is true.
        self.in_transmission = False   
        
        # Keep track of the number of packets lost
        self.num_packets_lost = 0  
        
        
    #
    # get_buffer_info
    #
    # Description:      This returns the amount of data and number of packets
    #                   on the buffer at the argued endpoint.  This can then
    #                   be used to guesstimate RTTs.
    #
    # Arguments:        self (Link)
    #                   ep_name (string) - The name of the endpoint that is
    #                       requesting its buffer information.
    #
    # Return Values:    (int) - The amount of data in bytes on the buffer.
    #                   (int) - The number of packets in the buffer.
    #
    # Shared Variables: self.end_points (READ) - Used to get the index that
    #                       corresponds to the argued endpoint name.
    #                   self.buffer_load (READ) - Value at endpoint index
    #                       is returned.
    #                   self.buffers (READ) - Length (i.e. num packets) is
    #                       returned for endpoint index.
    #
    # Global Variables: None.
    #
    # Revision History: 11/26/15: Created
    #
        
    def get_buffer_info(self, ep_name):
        '''
        Returns the amount of data and number of packets in the buffer on the 
        side of the link corresponding to the argued endpoint name.
        '''
        ep_index = self.end_points[ep_name]
        
        # Return the amount of data in the buffer and the number of packets
        #   (which is necessary because not all packets are the same size)
        return self.buffer_load[ep_index], len(self.buffers[ep_index])
        
    
    #
    # get_other_ep
    #
    # Description:      This is called by a particular endpoint (whose name is
    #                   argued) and returns the name of the other endpoint on
    #                   the link.
    #
    # Arguments:        self (Link)
    #                   ep_name (string) - The name of the endpoint calling the
    #                       function.
    #
    # Return Values:    (string) - A string representing the name of the other
    #                       endpoint
    #
    # Shared Variables: self.ep_names (READ) - Read to get the name of the other
    #                       other endpoint.
    #
    # Global Variables: None.
    #
    # Limitations:      This always returns an endpoint name.  If the argued
    #                   name is unknown, it will always return what is at index
    #                   1 in the endpoint dictionary.
    #
    # Revision History: 11/26/15: Created
    #
        
    def get_other_ep(self, ep_name):
        '''
        Returns the name/identity of the endpoint to this link that did not
        call the function.
        '''
        if self.ep_names[0] == ep_name:
            return self.ep_names[1]
        return self.ep_names[0]
          
        
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
        ep, other_ep = u.assign_endpoints(self.end_points, sender_name)
        
        # Put the packet onto the buffer heapqueue corresponding to the sender.
        #   The time we use for this will be now, because we are using first
        #   come first served priority on the links, but only if there is enough
        #   space.
        if packet.size + self.buffer_load[ep] <= cv.KB_to_bytes(self.buffer_size):
            # Add the packet identifier to the link buffer heap queue along 
            # with the time
            heapq.heappush(self.buffers[ep], 
                (sim.network_now(), packet.flow, packet.ID))

            # Update the buffer load for this link buffer because it is now
            # storing an additional packet.size
            self.buffer_load[ep] += packet.size
        
        # We now want to kickstart the putting packets on the link.  If there
        #   is already a packet in transmission, then nothing will happen.
        #   Otherwise, we are telling it the buffer is now nonempty.  However,
        #   create an event some dt in the future so all the "current" events
        #   can finish first.
        link_time = sim.network_now() + ct.TIME_BIT
        link_ev = e.Event(self.link_name, 'put_packet_on_link', [])
        sim.enqueue_event(link_time, link_ev)
            
            
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
    # get_next_buffer_pop
    #
    # Description:      This function Returns a tuple reflecting 1) the 
    #                   current direction of data travel on this link by 
    #                   stating the source of the data flow and 2) the index of 
    #                   the endpoint on this link that should place a packet 
    #                   onto the link next (either 0 or 1). 
    #
    # Arguments:        self (Link)
    #                   (no use to include an arg list because this funciton
    #                    is internal)
    #
    # Return Values:    (data_src, next_pop)
    #                   See docstring for description of these return values
    #
    # Shared Variables: buffers (READ/WRITE) - Read to see if there is anything
    #                       to put on the link, written if something is taken
    #                       off of the buffer to put on the link.
    #                   packets_on_link (READ/WRITE) - Read to see direction of
    #                       travel and written to put packets on the link.
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 2015/11/18: Moved this code out of put_packet_on_link()
    #                               and into this function for readability 
    #                               and easing debugging.
    #

    def get_next_buffer_pop(self):
        '''
        Returns a tuple reflecting 1) the current direction of data travel on 
        this link by stating the source of the data flow and 2) the index of 
        the endpoint on this link that should place a packet onto the link 
        next (either 0 or 1).
        '''
        # Find the direction of travel, which is the source of the data on the
        #   link.  If there is no source, then the data source is -1.
        data_src = -1
        if len(self.packets_on_link[0]) > 0:
            data_src = 0
        elif len(self.packets_on_link[1]) > 0:
            data_src = 1
        
        # Check which buffer contains the packet that will be put on the link
        #   next.  We will use this to determine whether it goes on the link now
        #   or later (if it must oppose the direction of data).  
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
            #   get the time of entry for the next packet from either buffer
            #   by "peeking" the element that would be popped off each of 
            #   the heapq's.
            [time0, temp1, temp2] = self.buffers[0][0]
            [time1, temp1, temp2] = self.buffers[1][0]
            
            # If the two times are equal, keep sending data in the direction of
            #   travel.  Otherwise, send the oldest (smallest time) packet.
            next_pop = 0
            if time0 == time1:
                next_pop = data_src
            elif time1 < time0:
                next_pop = 1
        
        return data_src, next_pop


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
    #                   arg_list ([]) - Unused.
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
    #                   data_on_link (WRITE) - The amount of data on the link is
    #                       updated
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
        
        # Get which buffer to pop a packet from next (0 or 1)
        data_src, next_pop = self.get_next_buffer_pop()
        
        # Now that we know the source of the next packet, we know if it goes on
        #   right away.  If the next packet will go in the same direction of 
        #   travel as the other packets, put it on the link.  Otherwise, we must
        #   wait until the link is clear to send it the opposite direction.
        if next_pop == data_src or data_src == -1:
            # We are sending a packet, so set the in_transmission flag.
            self.in_transmission = True
            
            # The next packet will go in the same direction as data on the link.
            # Pop the packet from the link buffer
            [time, flow_name, packet_ID] = heapq.heappop(self.buffers[next_pop])
            
            # Put it on the link and use the current time so we can heapify
            #   more easily.  Subtract from the buffer load to reflect that the
            #   packet is no longer on the buffer
            heapq.heappush(self.packets_on_link[next_pop],
                           (sim.network_now(), flow_name, packet_ID))
            packet_size = sim.packets[(flow_name, packet_ID)].size # in bytes
            self.buffer_load[next_pop] -= packet_size
            self.data_on_link += cv.bytes_to_MB(packet_size)
            
            # Calculate the transmission time as the size of the packet divided
            #   by the link capacity (aka rate).
            packet_size = sim.packets[(flow_name, packet_ID)].size
            transmission_time =  cv.bytes_to_MB(packet_size) / self.rate
            
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
            
            # Enqueue the event for the opposite end to receive the packet.
            #   This occurs at the same time as the transmission plus delay
            #   event.
            rcv_time = pkt1_time + self.delay
            rcv_event = e.Event(self.link_name, 'handoff_packet', [next_pop])
            sim.enqueue_event(rcv_time, rcv_event)
            
            # If we are not sending another packet after transmission, we need
            #   to also have an event that checks after propagation.  Because we
            #   do not know yet, we must make the event no matter what.
            pkt2_time = rcv_time
            pkt2_event = e.Event(self.link_name, 'put_packet_on_link', [])
            sim.enqueue_event(pkt2_time, pkt2_event)
            
            
    #
    # handoff_packet
    #
    # Description:      This changes all the appropriate variables so the link
    #                   reflects that it no longer has the packet on it.  It
    #                   then allows the endpoint to receive the packet.
    #
    # Arguments:        self (Link)
    #                   list_sender ([sender_index]) - A list containing the
    #                       index of the sender in the shared arrays.
    #
    # Shared Variables: data_on_link (WRITE) - Decremented to show data has
    #                       been taken off link.
    #                   packets_on_link (WRITE) - Packet popped off of link.
    #                   ep_names (READ) - Used to get the name of the endpoint.
    #
    # Global Variables: sim.packets (READ) - Used to get the size of data being
    #                       taken off of the link.
    #                   sim.endpoints (READ) - Used to obtain endpoint object.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 2015/11/16: Created
    #
            
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
        packet_size = sim.packets[(flow_name, packet_ID)].size # in bytes
        self.data_on_link -= cv.bytes_to_MB(packet_size)
        
        # Use the sender index to figure out the receiver index.
        rcv_index = (sender_index + 1) % 2
        
        # Now "hand off" the packet to the host/router.
        ep = sim.endpoints[self.ep_names[rcv_index]]
        ep.receive_packet([flow_name, packet_ID])
        
        
        
        
        
        
        
        
    
