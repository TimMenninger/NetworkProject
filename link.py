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
        # Name of the Link, each name is a unique string (e.g. "link_L1")
        self.link_name = the_link_name

        # Flag indicating whether you can transmit a Packet onto the beginning
        # of the Link
        self.free = True 

        # Throughput of the link (in MB/S) 
        self.rate = the_rate

        # How much data can be stored in the buffer (in KB)
        self.buffer_size = the_buffer_size

        # Amount of time it takes to send Packet down link (in ms)
        self.delay = the_delay

        # Define the endpoints so we know how to define flow on this 
        # half-duplex link. Could be a Router or Host. 'the_endpoints' is 
        # passed in as a tuple of host_name and/or router_name.  Additionally,
        # sort the end_points that are passed in so that end_points[0] is 
        # always the endpoint with the lexicographically less name and 
        # endpoints[1] is always the endpoint with the lexicographically 
        # greater name
        self.endpoints = tuple(sorted(the_endpoints))

        # Router buffer which will hold the Packet before the
        # corresponding Packet are transmitted to Link 
        self.buffers = (queue.Queue(), queue.Queue())
        
        # Packet currently on the link
        self.packets_carrying = []
        
        # Amount of data on link (in MB)
        self.current_load = 0.0

        # Python dictionary representing how many Packets are on the link
        # currently
        # Key: 0 -> Value: Number of Packet traveling from low endpoint to 
        #                  high endpoint (source = 0) 
        # Key: 1 -> Value: Number of Packet traveling form high endpoint to 
        #                  low endpoint (source = 1)
        self.num_on_link = {0 : 0, 1 : 0}

        # A 2-entry dictionary which stores the current load on each of the 
        # link buffers corresponding to endpoint 0 and endpoint 1.  The loads
        # are stored in KB
        self.buffer_current_load = {0 : 0, 1: 0}
 
    def space_for_packet(self, packet, ep):
        '''
        Returns true if there is room on the Link buffer for the endpoint 
        'ep' to enqueue the packet 'packet'.
        '''
        cur_buf_load = self.buffer_current_load[ep] # In KB
        packet_size = cv.bits_to_KB(packet.size) # In KB
        return cur_buf_load + packet_size <= self.buffer_size        
        
#
# put_packet_on_buffer
#
# Description:      
#
# Arguments:        self (Link)
#                   argument_list ([string, string, string]) - A list of
#                       arguments to the function, representing the endpoint
#                       name, flow name and packet name, respectively.
#
# Return Values:    (integer) - A status integer that indicates the success or
#                       lack thereof of the function.
#
# Shared Variables: self.buffers (WRITE) - This function enqueues a packet onto
#                       one of the buffers (potentially).
#                   self.end_points (READ) - This is read to determine which
#                       buffer should be altered, if any.
#                   self.buffer_current_load (READ) - This is used to determine
#                       if there is space on the buffer to enqueue a packet.
#                   self.buffer_size (READ) - This is used to determine if there
#                       is enough space on the buffer to enqueue a packet.
#
# Global Variables: sim.packets (READ) - This dictionary is read from to get a
#                       packet instance from its flow and packet names.
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
        
    def put_packet_on_buffer(self, argument_list):
        '''
        Adds a Packet to the buffer queue where it will wait to be transmitted
        along this link.
        '''
        
        # Unpack the argument list.
        [endpoint_name, flow_name, packet_name] = argument_list
        
        flow = sim.flows[flow_name]

        # For ease and code readability, extract the packet
        packet = flow.awaiting_ack[(flow_name, packet_name)]
        
        # Figure out which endpoint this packet was received from.
        ep = 0
        other_ep = 1
        if self.endpoints[1] == endpoint_name:
            ep = 1
            other_ep = 0
        
        # We want to check which endpoint the packet came from then put the
        # packet in the appropriate buffer, but only if there is enough space
        # in the buffer.
        print(str(self.buffer_current_load[ep]))
        print(str(cv.bits_to_KB(packet.size)))
        print(str(self.buffer_size))
        if self.space_for_packet(packet, ep):
            
            # Put the Packet identifier into the buffer queue and update its 
            # current load
            self.buffers[ep].put((flow_name, packet_name))
            self.buffer_current_load[ep] += cv.bits_to_MB(packet.size)

            # Enqueue an event to put the first Packet onto the link
            put_event = e.Event(self.link_name, 'put_packet_on_link', [])
            heapq.heappush(sim.event_queue, (sim.network_now(), put_event))

            return ct.SUCCESS

        return ct.LINK_FULL
            

#
# dequeue_packet
#
# Description:      This dequeues a packet from the argued endpoint, thereby
#                   removing it from the list, and returns it.
#
# Arguments:        self (Link)
#                   argument_list ([string]) - A list containing the endpoint
#                       index from which a packet should be dequeued.
#
# Return Values:    (string) - The flow name of the dequeued packet.
#                   (string) - The name of the packet dequeued.
#
# Shared Variables: self.buffers (WRITE) - One of the buffers in this loses a
#                       packet.
#                   self.buffer_current_load (WRITE) - Updated to reflect one
#                       one fewer packet.
#
# Global Variables: sim.packets (READ) - Read to get the packet instance from
#                       the flow and packet names.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created function handle and docstring.
#                   2015/10/29: Filled in function
#                   2015/11/03: Changed the link buffers to use the python queue
#                               data structure and only store the flow_name and 
#                               packet_name
#

    def dequeue_packet(self, argument_list):
        '''
        Dequeues a Packet from the Packet queue to transmit along this link.
        '''
        
        # Unpack the argument list.
        [ep] = argument_list
        
        # Dequeue the next Packet from the buffer at the argued endpoint. Then,
        # update the load on the buffer.
        flow_name, packet_ID = self.buffers[ep].get()

        # Retrieve the Packet object to dequeue
        packet = sim.flows[flow_name].awaiting_ack[(flow_name, packet_ID)]

        # Remove the Packet size from the correct buffer_current_load
        self.buffer_current_load[ep] -= cv.bits_to_MB(packet.size)
            
        # Return flow name and packet ID
        return flow_name, packet_ID
        
        
#
# enqueue_carry_event
#
# Description:      This decides which of the two buffers should have a packet
#                   popped then sent down the link, then creates an event that
#                   will pop from that buffer and send the packet.
#
# Arguments:        self (Link)
#
# Return Values:    ep (integer) - The index of the endpoint that contains the
#                       next packet to be sent.
#                   packet.flow_name (string) - The name of the flow the packet
#                       is a part of.
#                   packet.ID (string) - The ID of the packet to be sent.
#                   time_delay (integer) - The amount of time it would take in
#                       theory for this event to occur in real life.  This will
#                       be the amount of time waited before executing the event.
#
# Shared Variables: self.buffers (READ) - Read from to determine which buffer
#                       is more worthy of sending a packet.
#                   self.flowing_from (READ) - Read to determine which direction
#                       the current flow is going.
#                   self.rate (READ) - Used to determine the time delay before
#                       the packet gets sent.
#                   self.link_current_load (READ) - Used to determine the time
#                       until the packet gets sent.
#
# Global Variables: sim.packets (READ) - Used to get the packet instance from
#                       the flow name and packet name.
#
# Limitations:      2015/11/3: Need to consider how to enqueue carry events 
#                              when a Packet is dequeued from an endpoint that
#                              would require that the direction of data flow
#                              changes.-
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#                   2015/11/03: Simplified method to try to limit the enqueuing
#                               of carry events to when the Link is free and 
#                               data is already being transmitted in the 
#                              direction that the current Packet wants to be 
#                              transmitted in
#
        
    def put_packet_on_link(self, args):
        '''
        
        '''
        # First, check which next packet should be sent next.  Decide to 
        # send the oldest packet on either buffer.
        ep = 0
        other_ep = 1
        if self.buffers[ep].qsize() < self.buffers[other_ep].qsize(): 
            ep = 1
            other_ep = 0
        
        if self.buffers[ep].qsize() == 0:
            return
               
        # Put the Packet in a container, note: it does not pop the Packet from
        # the link buffer -- that happens in carry_packet()
        flow_name, packet_name = self.buffers[ep].queue[0]

        # Retrieve the Packet object
        packet = sim.flows[flow_name].awaiting_ack[(flow_name, packet_name)]
        
        # We know that every single Packet will take at least 
        # packet size (MB) / link rate (MB/s) = (s) time to be transmitted
        # onto the link
        transmit_time = cv.bits_to_MB(packet.size) / self.rate
 
        # The Link has to be "free" in this direction in order for us to be 
        # able to transmit a Packet
        # This happens in 1 of 2 situations: 
        #   1) Both endpoints are not sending data down the link at this time
        #   2) Only our endpoint is ending data down the link at this time
        # We have to create and enqueue two carry events: 
        #   1) After the transmit time (if data flow direction doesn't have to
        #      change direction)
        #   2) After the transmit and propagation delay (if data flow does have
        #      to change direction)
        if self.num_on_link[other_ep] == 0:
            carry_event_1 = e.Event(self.link_name, 'carry_packet', [ep])
            carry_event_2 = e.Event(self.link_name, 'carry_packet', [ep])
            time_1 = sim.network_now() + transmit_time
            time_2 = time_1 + self.delay
            heapq.heappush(sim.event_queue, (time_1, carry_event_1))
            heapq.heappush(sim.event_queue, (time_2, carry_event_2))
            self.lockdown_link([transmit_time])
        
#
# carry_packet
#
# Description:      Simulates the link carrying the packet.  This pops a packet
#                   from the appropriate buffer and then changes the link
#                   attributes to reflect the packet on the link and enqueues
#                   an event for the other end to receive the packet.  Along
#                   with this event, this calculates how much time should pass
#                   before the reception is made.
#
# Arguments:        self (Link)
#                   argument_list ([string]) - A list containing the index of
#                       the endpoint that the packet is being sent from.
#
# Return Values:    None.
#
# Shared Variables: self.packets_carrying (WRITE) - The packet that is being put
#                       onto the link is added to this list.
#                   self.link_current_load (WRITE) - Updated to reflect the new
#                       load on the link.
#                   self.delay (READ) - Used to determine the time that should
#                       pass before the packet is received.
#
# Global Variables: sim.packets (READ) - Used to get a packet instance from a
#                       flow name and a packet name.
#
# Limitations:      None.
#
# Known Variables:  None.
#
# Revision History: 2015/10/29: Created
#                   2015/11/03: Added bits to MB conversion, switched receive
#                               event Host to be the Host at the other end of 
#                               the Link, fixed time_delay error 
#

    def carry_packet(self, argument_list):
        '''
        Updates the Link to reflect that a packet is now being carried down 
        the link.
        '''
        
        # Unpack the arguments
        [ep] = argument_list
        
        # Dequeue from the buffer at the argued endpoint.  This will give us
        # the packet description we are looking for.
        flow_name, packet_ID = self.dequeue_packet([ep])
        
        # Retrieve the Packet object to dequeue
        packet = sim.flows[flow_name].awaiting_ack[(flow_name, packet_ID)]
        
        # Put the Packet onto the Link itself and update the attributes
        self.packets_carrying.append((flow_name, packet_ID))
        self.current_load += cv.bits_to_MB(packet.size)
        self.num_on_link[ep] += 1

        # Enqueue an event to receive this packet at the other end of the Link
        # after the propagation delay
        other_ep = (ep + 1) % 2
        other_host_name = sim.endpoints[self.endpoints[other_ep]].host_name
        receive_event = e.Event(other_host_name, 'receive_packet', [])
        
        # Enqueue the receive_event
        receive_time = sim.network_now() + self.delay
        heapq.heappush(sim.event_queue, (receive_time, receive_event))
    
#
# free_link()
#
# Description:      Sets self.free = True.  It's called after the transmission
#                   onto the Link and then enqueues an event that re-frees the
#                   time for putting a Packet onto a Link has elapsed to free
#                   up the Link for use. 
#
# Arguments:        self (Link)
#                   argument_list ([]) empty, unused
#
# Return Values:    None.
#
# Shared Variables: self.free (WRITE)
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/03: Created function 
    
    def free_link(self, argument_list):
        '''
        Called after the transmission onto the Link.  It enqueues an event 
        that tells the Link for putting a Packet onto a Link has elapsed to 
        free up the Link for use. 
        ''' 
        put_event = e.Event(self.link_name, 'put_packet_on_link', [])
        heapq.heappush(sim.event_queue, (sim.network_now() + ct.TIME_BIT, put_event))

#
# lockdown_link
#
# Description:      Sets self.free = False while a Packet is being transmitted
#                   onto the Link and then enqueues an event that re-frees the
#                   Link (self.free = True) after the Packet has been 
#                   transmitted.
#
# Arguments:        self (Link)
#                   argument_list([time_delay]) (float)
#
# Return Values:    None.
#
# Shared Variables: self.free (WRITE)
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/03: Created function
#

    def lockdown_link(self, argument_list):
        '''
        Enqueues an event that re-frees the Link after the Packet has been 
        fully transmitted.
        '''
        # Unpack the arguments
        [time] = argument_list

        # Lock the link so that no other Packet may be transmitted 
        self.free = False

        # Enqueue a free link event to start after the current Packet 
        # transmission
        free_link_event = e.Event(self.link_name, 'free_link', [])
        heapq.heappush(sim.event_queue, (sim.network_now() + time, free_link_event))

#
# print_contents
#
# Description:      Prints the attributes and their contained values.  This is
#                   used mainly for debugging purposes.
#
# Arguments:        self (Link)
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
        Prints the status of all atributes of this Pink.
        '''
