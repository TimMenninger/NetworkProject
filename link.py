############################################################################
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
############################################################################


############################################################################
#                                                                          #
#                               Imported Modules                           #
#                                                                          #
############################################################################

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


############################################################################
#                                                                          #
#                                   Link Class                             #
#                                                                          #
############################################################################


class Link:

    def __init__(self, in_link_name, in_rate, in_delay, in_buffer_size, 
                 in_endpoints):
        '''
        Description:        Initialize an instance of Link by intitializing 
                            its attributes.

        Arguments:          in_link_name (string)
                                - A string indicating the name of this 
                                particular Link instance (i.e., "L1").

                            in_rate (float)
                                - A float indicating the link rate for this 
                                particular Link instance in Mbps (i.e., 10.5).

                            in_delay (integer)
                                - An integer indicating the link delay for this 
                                particular Link instance in ms (i.e., 10).

                            in_buffer_size (integer)
                                - An integer indicating the buffer size for the
                                link buffers on this particular Link instance 
                                in KB (i.e., 64). 

                            in_endpoints ((string, string))
                                - A (string, string) tuple that contain the 
                                names (either host names and/or link names) of 
                                the endpoints of this Link object.

        Shared Variables:   self.type (WRITE)
                                - Initialized
        
                            self.link_name (WRITE)
                                - Initialized
        
                            self.flowing_from (WRITE)     (not init argument)
                                - Initialized

                            self.rate (WRITE)
                                - Initialized

                            self.buffer_size (WRITE)
                                - Initialized

                            self.delay (WRITE)
                                - Initialized

                            self.end_points (WRITE)       (not init argument)
                                - Initialized
        
                            self.ep_names (WRITE)         (not init argument)
                                - Initialized
        
                            self.buffers (WRITE)          (not init argument)
                                - Initialized
        
                            self.buffer_load (WRITE)      (not init argument)
                                - Initialized
        
                            self.packets_on_link (WRITE)  (not init argument)
                                - Initialized
                
                            self.data_on_link (WRITE)     (not init argument)
                                - Initialized
        
                            self.in_transmission (WRITE)  (not init argument)
                                - Initialized 
        
                            self.num_packets_lost (WRITE) (not init argument)
                                - Initialized 

        Global Variables:   None.

        Limitations:        None.

        Known Bugs:         None.

        Revision History:   10/20/15: Created
        '''
        # Store the type so it can be easily identified as a router.
        self.type = ct.TYPE_LINK
        
        # Name of the Link, each name is a unique string (i.e. "L1")
        self.link_name = in_link_name
        
        # This is the index of the endpoint that data is flowing from.  If
        #   negative, there is no flow.
        self.flowing_from = -1

        # How fast the Router can send data (in Mb/sec) 
        self.rate = in_rate

        # How much data can be stored in the buffer (in KB)
        self.buffer_size = in_buffer_size

        # Amount of time it takes to send Packet down link (in ms)
        self.delay = in_delay

        # Define the endpoints so we know how to define flow on this 
        # half-duplex link. Could be a Router or Host. 'in_endpoints' is 
        # passed in as a tuple of host_name and/or router_name
        self.end_points = { in_endpoints[0] : 0, in_endpoints[1] : 1 }
        self.ep_names = { 0 : in_endpoints[0], 1 : in_endpoints[1] }
        
        # The packet buffers on either end of the half-duplex link (heapq's)
        self.buffers = [ [], [] ]
        
        # The amount of data in the buffer in bytes.
        self.buffer_load = [ 0, 0 ]
        
        # The number of packets on the link from the indexed endpoint.  One of
        #   these must be empty at all times because the link is half-duplex.
        self.packets_on_link = [ [], [] ]
        
        # The amount of data on the link in Mb
        self.data_on_link = 0
        
        # If a packet is currently being moved from the buffer to the link,
        #   this is true.
        self.in_transmission = False   
        
        # Keep track of the number of packets lost
        self.num_packets_lost = 0  
        
        
    def get_buffer_info(self, ep_name):
        '''
        Description:        This returns the amount of data and number of 
                            Packet on the buffer at the argued endpoint.  This 
                            can then be used to estimate RTTs.
        
        Arguments:          ep_name (string) 
                                - The name of the endpoint that is requesting 
                                its buffer information.
        
        Return Values:      (int, int) 
                                - The amount of data in bytes on the buffer.
                                - The number of packets in the buffer.
        
        Shared Variables: self.end_points (READ) 
                                - Used to get the index that corresponds to the 
                                argued endpoint name.
                          self.buffer_load (READ) 
                                - Value at endpoint index is returned.
                          self.buffers (READ) 
                                - Length (i.e. num packets) is returned for 
                                endpoint index.
        
        Global Variables: None.
        
        Revision History: 11/26/15: Created
        '''
        ep_index = self.end_points[ep_name]
        
        # Return the amount of data in the buffer and the number of packets
        #   (which is necessary because not all packets are the same size)
        return self.buffer_load[ep_index], len(self.buffers[ep_index])
    
        
    def get_other_ep(self, ep_name):
        '''
        Description:        This is called by a particular endpoint (whose 
                            name is argued) and returns the name of the other 
                            endpoint on the Link.
        
        Arguments:          ep_name (string) 
                                - The name of the endpoint calling the 
                                function.
        
        Return Values:      (string) 
                                - A string representing the name of the other
                                endpoint.
        
        Shared Variables:   self.ep_names (READ) 
                                - Read to get the name of the other other 
                                endpoint.
        
        Global Variables:   None.
        
        Limitations:        This always returns an endpoint name.  If the 
                            argued name is unknown, it will always return what 
                            is at index 1 in the endpoint dictionary.
        
        Revision History:   11/26/15: Created
        '''
        if self.ep_names[0] == ep_name:
            return self.ep_names[1]
        return self.ep_names[0]
          
        
    def put_packet_on_buffer(self, sender_name, packet):
        '''
        Description:        This takes a packet and if there is space on the 
                            buffer, moves it onto the buffer.  If there is 
                            nothing on the Link or either buffer, it also puts 
                            it on the Link.
        
        Arguments:          sender_name (string) 
                                - The name of the endpoint that sent the 
                                Packet.

                            packet (Packet) 
                                - The Packet being sent.
        
        Return Values:      None.
        
        Shared Variables:   self.buffers (WRITE) 
                                - This function enqueues a packet onto one of 
                                the buffers (potentially).
                            
                            self.end_points (READ) 
                                - This is read to determine which buffer should 
                                be altered, if any.

                            self.buffer_load (WRITE) 
                                - This changes the buffer load when adding to 
                                the buffer.
                            
                            self.buffer_size (READ) 
                                - This is used to determine if there is enough 
                                space on the buffer to enqueue a Packet.
        
        Global Variables: None.
        
        Limitations:      None.
        
        Known Bugs:       None.
        
        Revision History: 2015/10/22: Created function handle and docstring
                          2015/10/29: Filled function in.
                          2015/11/03: Changed the link buffers to use the 
                                      python queue data structure and only 
                                      store the flow_name and packet_name
        '''
        # Get the index of the endpoint sender_name represents and then the
        #   index of the opposite endpoint.
        ep, other_ep = u.assign_endpoints(self.end_points, sender_name)
        
        # Put the packet onto the buffer heapqueue corresponding to the sender.
        #   The time we use for this will be now, because we are using first
        #   come first served priority on the links, but only if there is 
        #   enough space.
        if packet.size + cv.KB_to_bytes(self.buffer_load[ep]) <= \
           cv.KB_to_bytes(self.buffer_size):
            # Add the packet identifier to the link buffer heap queue along 
            # with the time
            heapq.heappush(self.buffers[ep], 
                (sim.network_now(), packet.flow, packet.ID))

            # Update the buffer load for this link buffer because it is now
            # storing an additional packet.size
            self.buffer_load[ep] += cv.bytes_to_KB(packet.size)
        
        else: 
            self.num_packets_lost += 1

        # We now want to kickstart the putting packets on the link.  If there
        #   is already a packet in transmission, then nothing will happen.
        #   Otherwise, we are telling it the buffer is now nonempty.  However,
        #   create an event some dt in the future so all the "current" events
        #   can finish first.
        link_time = sim.network_now() + ct.TIME_BIT
        link_ev = e.Event(self.link_name, 'put_packet_on_link', [])
        sim.enqueue_event(link_time, link_ev)
            
            
    def reset_in_transmission(self, unused_list):
        '''
        reset_in_transmission
        
        Description:        Sets the in_transmission flag to 0 so more packets 
                            can be loaded onto the link.
        
        Arguments:          unused_list (List) 
                                - Unused.
        
        Return Values:      None.
        
        Shared Variables:   in_transmission (WRITE) 
                                - Written to False.
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   11/16/15: Created
        '''
        self.in_transmission = False
            

    def get_next_buffer_pop(self):
        '''
        Description:        This function gives information about the current
                            direction of travel on the Link as well as which 
                            buffer on the Link should be "popped" from next.
        
        Arguments:          None.
        
        Return Values:      (data_src, next_pop)
                                - The source of the data currently travelling
                                on the Link -- essentially gives direction of 
                                data flow on Link.
                                - An integer index of the endpoint on this Link
                                that should next place a Packet onto the Link
                                (either 0 or 1) .
        
        Shared Variables:   buffers (READ/WRITE) 
                                - Read to see if there is anything to put on 
                                the Link, written if something is taken off of 
                                the buffer to put on the Link.
                          
                            packets_on_link (READ/WRITE) 
                                - Read to see direction of travel and written 
                                to put Packet on the Link.
        
        Global Variables:   None.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/18: Moved this code out of 
                                        put_packet_on_link()
                                        and into this function for readability 
                                        and easing debugging.
        '''
        # Find the direction of travel, which is the source of the data on the
        #   link.  If there is no source, then the data source is -1.
        data_src = -1
        if len(self.packets_on_link[0]) > 0:
            data_src = 0
        elif len(self.packets_on_link[1]) > 0:
            data_src = 1
        
        # Check which buffer contains the packet that will be put on the link
        #   next.  We will use this to determine whether it goes on the link 
        #   now or later (if it must oppose the direction of data).  
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

            
    def put_packet_on_link(self, arg_list):
        '''
        Description:        This puts a Packet on the Link.  It then enqueues 
                            some Event.  One will check after transmission time 
                            if there is another Packet that can go in the same 
                            direction. One will check wait for transmission 
                            time then reset the in_transmission flag.  One 
                            waits for the Packet to reach the other end to see 
                            if there is a Packet waiting to go the opposite 
                            direction, and the last is for the other end to 
                            receive the Packet.
        
        Arguments:          arg_list ([]) 
                                - Unused.
        
        Return Values:      None.
        
        Shared Variables:   buffers (READ/WRITE) 
                                - Read to see if there is anything to put on 
                                the Link, written if something is taken
                                off of the buffer to put on the link.
                          
                            packets_on_link (READ/WRITE) 
                                - Read to see direction of travel and written 
                                to put Packet on the Link.
                          
                            in_transmission (WRITE) 
                                - Written to True when a packet is being 
                                transmitted.
                          
                            data_on_link (WRITE) 
                                - The amount of data on the Link is updated.
        
        Global Variables: None.
        
        Limitations:      None.
        
        Known Bugs:       None.
        
        Revision History: 2015/10/22: Created function handle and docstring
                          2015/10/29: Filled function in.
                          2015/11/03: Changed the link buffers to use the 
                                      python queue data structure and only 
                                      store the flow_name and packet_name
                          2015/11/16: Now checks for next packet to put on 
                                      Link and creates Event for it.
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
        #   travel as the other packets, put it on the link.  Otherwise, we 
        #   must wait until the link is clear to send it the opposite 
        #   direction.
        if next_pop == data_src or data_src == -1:
            # We are sending a packet, so set the in_transmission flag.
            self.in_transmission = True
            
            # The next packet will go in the same direction as data on the 
            #   link. Pop the packet from the link buffer
            [time, flow_name, packet_ID] = heapq.heappop(
                                                    self.buffers[next_pop])
            
            # Put it on the link and use the current time so we can heapify
            #   more easily.  Subtract from the buffer load to reflect that the
            #   packet is no longer on the buffer
            heapq.heappush(self.packets_on_link[next_pop],
                           (sim.network_now(), flow_name, packet_ID))
            packet_size = sim.packets[(flow_name, packet_ID)].size # in bytes
            self.buffer_load[next_pop] -= cv.bytes_to_KB(packet_size)
            self.data_on_link += cv.bytes_to_Mb(packet_size)
            
            # Calculate the transmission time as the size of the packet 
            #   divided by the link capacity (aka rate).
            packet_size = sim.packets[(flow_name, packet_ID)].size
            transmission_time =  cv.bytes_to_MB(packet_size) / self.rate
            
            # Create an event after this packet's transmission to reset the
            #   in_transmission flag.  Subtract a small amount of time to 
            #   assure it happens before the next call of this function.
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
            #   to also have an event that checks after propagation.  Because 
            #   we do not know yet, we must make the event no matter what.
            pkt2_time = rcv_time
            pkt2_event = e.Event(self.link_name, 'put_packet_on_link', [])
            sim.enqueue_event(pkt2_time, pkt2_event)
            
            
    def handoff_packet(self, list_sender):
        '''
        Description:        This changes all the appropriate variables so the 
                            Link reflects that it no longer has the Packet on 
                            it.  It then allows the endpoint to receive the 
                            Packet.
        
        Arguments:          list_sender ([sender_index]) 
                                - A list containing the index of the sender in 
                                the shared arrays.
        
        Shared Variables:   data_on_link (WRITE) 
                                - Decremented to show data has been taken off 
                                Link.
                          
                            packets_on_link (WRITE) 
                                - Packet popped off of Link.

                            ep_names (READ) 
                                - Used to get the name of the endpoint.
        
        Global Variables:   sim.packets (READ) 
                                - Used to get the size of data being taken off 
                                of the Link.

                            sim.endpoints (READ) 
                                - Used to obtain endpoint object.
        
        Limitations:        None.
        
        Known Bugs:         None.
        
        Revision History:   2015/11/16: Created
        '''
        # Unpack the argument list, which has the sender in it.
        [sender_index] = list_sender
        
        # Take the packet off of the link by removing it from the queue.
        [time, flow_name, packet_ID] = \
                heapq.heappop(self.packets_on_link[sender_index])
        packet_size = sim.packets[(flow_name, packet_ID)].size # in bytes
        self.data_on_link -= cv.bytes_to_Mb(packet_size)
        
        # Use the sender index to figure out the receiver index.
        rcv_index = (sender_index + 1) % 2
        
        # Now "hand off" the packet to the host/router.
        ep = sim.endpoints[self.ep_names[rcv_index]]
        ep.receive_packet([flow_name, packet_ID])
           
    
