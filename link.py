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

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import simulator so we can access global dictionaries
import simulate as sim

# Import the constants and the conversion functions
import constants as ct
import conversion as cv

# Import the queue Python package for the link buffers which are FIFO
import queue

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
        # Name of the Link, each name is a unique string (i.e. "L1")
        self.link_name = the_link_name

        # Flag indicating which direction the Link is sending data in (could 
        # indicate that it's sending data in neither direction)
        self.in_use = ct.LINK_NOT_USED

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
        # higher name
        self.end_points = tuple(sorted(the_endpoints))

        # Router buffer which will hold the Packet before the
        # corresponding Packet are transmitted to Link 
        self.buffers = (queue.Queue(), queue.Queue())
        
        # Packet currently on the link
        self.packets_carrying = []
        
        # Amount of data on link (in MB)
        self.current_load = 0.0

        # A 2-entry dictionary which stores the current load on each of the 
        # link buffers corresponding to to endpoint 0 and endpoint 1
        self.buffer_current_load = {0 : 0, 1: 0}
        
        
#
# enqueue_packet
#
# Description:      This enqueues a packet onto the buffer at the end that the
#                   packet was received from.
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
#                   2015/11/3: Changed the link buffers to use the python queue
#                              data structure and only store the flow_name and 
#                              packet_name
#
        
    def enqueue_packet(self, argument_list):
        '''
        Adds a Packet to the buffer queue where it will wait to be transmitted
        along this link.
        '''
        
        # Unpack the argument list.
        [endpoint_name, flow_name, packet_name] = argument_list
        
        # For ease and code readability, extract the packet
        packet = sim.packets[(flow_name, packet_name)]
        
        # Figure out which endpoint this packet was received from.
        ep = 0
        if self.end_points[1] == endpoint_name:
            ep = 1
        
        # We want to check which endpoint the packet came from then put the
        # packet in the appropriate buffer, but only if there is enough space
        # in the buffer.
        if self.buffer_current_load[ep] + packet.size <= self.buffer_size:
            
            # Put the packet into the buffer queue and update its current load.
            self.buffers[ep].put((flow_name, packet_name))
            self.buffer_current_load[ep] += cv.bits_to_MB(packet.size)
            
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
#                   2015/11/3: Changed the link buffers to use the python queue
#                              data structure and only store the flow_name and 
#                              packet_name
#

    def dequeue_packet(self, argument_list):
        '''
        Dequeues a Packet from the Packet queue to transmit along this link.
        '''
        
        # Unpack the argument list.
        [endpoint] = argument_list
        
        # Dequeue the next packet from the buffer at the argued endpoint. Then,
        # update the load on the buffer.
        packet = self.buffers[endpoint].get()

        # Remove the Packet size from the correct buffer_current_load
        self.buffer_current_load[ep] -= cv.bits_to_MB(packet.size)
            
        # Return flow name and packet ID
        return packet[0], packet[1]
        
        
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
#                              changes.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/29: Created
#                   2015/11/3: Simplified method to try to limit the enqueuing
#                              of carry events to when the Link is free and 
#                              data is already being transmitted in the 
#                              direction that the current Packet wants to be 
#                              transmitted in
#
        
    def enqueue_carry_event(self):
        '''
        Peeks at the next packet that is to be sent.  This returns which
        endpoint the packet is at, its flow and packet names and the time
        that must be waited until the link will be able to carry it to the
        other end as well as enqueues the appropriate event.
        '''
        
        # First, check which next packet should be sent next.  Decide to 
        # send the oldest packet on either buffer.
        ep = 0
        if self.buffers[1].queue(0) < self.buffers[0].queue(0):
            ep = 1
            
        # Put the Packet in a container, note: it does not pop the Packet from
        # the link buffer -- that happens in carry_packet()
        packet = self.buffers[ep].queue[0]
        
        # We know that every single Packet will take at least 
        # packet size (MB) / link rate (MB/s) = (s) time to be transmitted
        # onto the link
        transmission_time = cv.bits_to_MB(packet.size) / self.rate
 
        # The Link has to be "free" in order for us to be able to transmit 
        # a Packet
        if self.free:
            # The packet must also go in the direction of the current flow. 
            # For example, if the endpoint that we're sending a Packet from is 
            # 0 and the Link is already sending data towards the "higher" 
            # hostname, then we do not have to wait for the direction of the 
            # data transfer within the Link to change and we can enqueue a 
            # Packet transmission event.    
            if ep == 0 and self.in_use == LINK_USED_HIGH or \
               ep == 1 and self.in_use == LINK_USED_LOW:
                # Create a carry event that will carry the Packet to the other 
                # end of the Link
                carry_event = e.Event(self, carry_packet, [ep])
                heapq.heappush(sim.event_queue, (sim.network_now(), carry_event))
                lockdown_link(transmission_time)
        
        return ep, packet.flow_name, packet.ID, time_delay
        

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
#                   2015/11/3: Added bits to MB conversion, switched receive
#                              event Host to be the Host at the other end of 
#                              the Link, fixed time_delay error 
#

    def carry_packet(self, argument_list):
        '''
        Updates the Link to reflect that a packet is now in transmission.
        '''
        
        # Unpack the arguments
        [endpoint] = argument_list
        
        # Dequeue from the buffer at the argued endpoint.  This will give us
        # the packet description we are looking for.
        flow_name, packet_name = self.dequeue_packet(endpoint)
        
        # Get the packet size
        packet_size = sim.packets[(flow_name, packet_name)].size
        
        # Put the packet into the link itself and update our size tracker.
        self.packets_carrying.append((flow_name, packet_name))
        self.link_current_load += cv.bits_to_MB(packet_size)
        
        # Enqueue an event to receive this packet at the other end of the Link
        # after the propogation delay
        other_endpoint = (endpoint + 1) % 2
        receive_event = e.Event(sim.endpoints[self.endpoints[other_endpoint]], 
                                                        receive_packet, [])
        
        # Enqueue the receive_event
        heapq.heappush(sim.event_queue, 
            (sim.network_now + link.delay, receive_event))
    
#
# free_link()
#
# Description:      Sets self.free = True.  It's called after the transmission                   onto the Link and then enqueues an event that re-frees the
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
# Revision History: 2015/11/3: Created function 
    
    def free_link(self, argument_list):
        '''
        Sets self.free = True.  It's called after the transmission onto the Link 
        and then enqueues an event that re-frees the time for putting a Packet 
        onto a Link has elapsed to free up the Link for use. 
        ''' 
        self.free = True

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
# Revision History: 2015/11/3: Created function       

    def lockdown_link(self, argument_list):
        '''
        Sets self.free = False while a Packet is being transmitted onto the 
        Link and then enqueues an event that re-frees the Link 
        (self.free = True) after the Packet has been fully transmitted.
        '''
        # Unpack the arguments
        [transmission_time] = argument_list

        # Lock the link so that no other Packet may be transmitted 
        self.free = False

        # Enqueue a free link event to start after the current Packet 
        # transmission
        free_link_event = e.Event(self, free_link, [])
        heapq.heappush(sim.event_queue, 
            (sim.network_now() + transmission_time, free_link_event))

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
