################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# status.py
#
# This contains the code to record the network status at fixed time intervals.
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

# Import the queue Python package for the link buffers which are FIFO
import queue

# Import heapq library so we can use it for our events.
import heapq 

# Matplotlib has everything we need for graphing.
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import time

# Data structures that store the data for network metrics

time_recordings         = np.empty(1)
link_rate_readings      = { }   # Indexed by link name, stores link rates
buffer_occ_recordings   = { }   # Indexed by link name, stores buffer occupancies
packet_loss_recordings  = { }   # Indexed by link name, stores packet loss
flow_rate_recordings    = { }   # Indexed by flow name, stores flow rates
packet_delay_recordings = { }   # Indexed by flow name, stores packet delays (RTT)
window_size_recordings  = { }   # Indexed by flow name, stores window sizes

fig_link, ax_link = plt.subplots(3, 1, figsize=(12, 7))
fig_flow, ax_flow = plt.subplots(3, 1, figsize=(12, 7))

fig_link.tight_layout()
fig_flow.tight_layout()

times = open(ct.TIMES_OUT, 'w')
times.write("time\n")

link_rates = open(ct.LINK_RATE_OUT, 'w')
link_rates.write("link_name,link_rate\n")

buffer_occs = open(ct.BUFFER_OCC_OUT, 'w')
buffer_occs.write("link_name,buffer_occ_1,buffer_occ_2\n")

packet_loss = open(ct.PACKET_LOSS_OUT, 'w')
packet_loss.write('link_name,packet_loss\n')

flow_rates = open(ct.FLOW_RATE_OUT, 'w')
flow_rates.write('flow_name,flow_rate\n')

window_sizes = open(ct.WINDOW_SIZE_OUT, 'w')
window_sizes.write('flow_name,window_size\n')

packet_delays = open(ct.PACKET_DELAY_OUT, 'w')
packet_delays.write('flow_name,packet_delay\n')

def construct_plots():

    # Officially stop writing to all the files
    times.close()
    link_rates.close()
    buffer_occs.close()
    packet_loss.close()
    flow_rates.close()
    window_sizes.close()
    packet_delays.close()
    
    # Pull in the time recordings
    tms = pd.read_csv(ct.TIMES_OUT, dtype={'time': np.int32})
    time_max = tms['time'].max()

    # Pull in the link_rate recordings
    lr = pd.read_csv(ct.LINK_RATE_OUT, dtype={'link_name': str, 'link_rate': np.float64})

    # Pull in the buffer_occupancy recordings 
    bf = pd.read_csv(ct.BUFFER_OCC_OUT, dtype={'link_name': str, 'buffer_occ_1': np.float64, 'buffer_occ_2': np.float64})

    # Pull in the packet_loss recordings
    pl = pd.read_csv(ct.PACKET_LOSS_OUT, dtype={'link_name': str, 'packet_loss': np.int32})

    # Pull in the flow_rate recordings
    fr = pd.read_csv(ct.FLOW_RATE_OUT, dtype={'flow_name': str, 'flow_rate': np.float64})

    # Pull in the window_size recordings
    ws = pd.read_csv(ct.WINDOW_SIZE_OUT, dtype={'flow_name': str, 'window_size': np.int32})

    # Pull in the packet_delay recordings
    py = pd.read_csv(ct.PACKET_DELAY_OUT, dtype={'flow_name': str, 'packet_delay': np.float64})

    # Plot link rate per link
    ax_link[0].plot(tms['time'], lr['link_rate'])
    #ax_link[0].set_title("Link Rate")
    ax_link[0].set_xlim((0, time_max))
    ax_link[0].set_xlabel('Time (ms)')
    ax_link[0].set_ylabel('Link Late (Mbps)')

    # Plot buffer occupancy per link for buffers 1 and 2
    ax_link[1].plot(tms['time'], bf['buffer_occ_1'])
    ax_link[1].plot(tms['time'], bf['buffer_occ_2'])
    ax_link[1].set_xlim((0, time_max))
    #ax_link[1].set_title("Buffer Occupancy")
    ax_link[1].set_xlabel('Time (ms)')
    ax_link[1].set_ylabel('Buffer Occupancy (pkts)')    

    # Plot packet loss per link
    ax_link[2].plot(tms['time'], pl['packet_loss'])
    ax_link[2].set_xlim((0, time_max))
    #ax_link[2].set_title("Packet Loss")
    ax_link[2].set_xlabel('Time (ms)')
    ax_link[2].set_ylabel('Packet Loss (pkts)')  

    # Plot the flow_rate recordings
    ax_flow[0].plot(tms['time'], fr['flow_rate'])
    ax_flow[0].set_xlim((0, time_max))
    #ax_flow[0].set_title("Flow Rate")
    ax_flow[0].set_xlabel('Time (ms)')
    ax_flow[0].set_ylabel('Flow Rate (Mbps)') 

    # Plot the window_size recordings
    ax_flow[1].plot(tms['time'], ws['window_size'])
    ax_flow[1].set_xlim((0, time_max))
    #ax_flow[1].set_title("Window Size")
    ax_flow[1].set_xlabel('Time (ms)')
    ax_flow[1].set_ylabel('Window Size (pkts)') 

    # Plot the packet_delay recordings
    ax_flow[2].plot(tms['time'], py['packet_delay'])
    ax_flow[2].set_xlim((0, time_max))
    ax_flow[2].set_ylim((0, py['packet_delay'].max() + 10))
    #ax_flow[2].set_title("Packet Delay")
    ax_flow[2].set_xlabel('Time (ms)')
    ax_flow[2].set_ylabel('Packet Delay (ms)')    

    plt.show()

    
#
# record_network_status
#
# Description:      Records the status of the network at the current time.  It
#                   then creates a new event for the next network recording.
#                   Before doing this, however, it checks if there are events
#                   in the queue. 
#
# Arguments:        unused_list (List) - Done in this way so we can enqueue this
#                       as an event in our event queue heapqueue.  Defaults to
#                       None so it can be called without arguments.
#
# Return Values:    None.
#
# Global Variables: network_time (READ) - Used as the independent variable when
#                       creating graphs.
#                   times (WRITE) - Time appended
#                   link_rate_readings (WRITE) - Link rate appended
#                   buffer_occ_recordings (WRITE) - Buffer occupancy appended
#                   packet_loss_recordings (WRITE) - Packet loss appended
#                   flow_rate_recordings (WRITE) - Flow rate appended
#                   packet_delay_recordings (WRITE) - Packet Delay appended
#                   window_size_recordings (WRITE) - Window size recorded
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created function handle and docstring.
#                   2015/11/16: Filled in global arrays.
#                   2015/11/18: Enqueued next network_recording event
#
    
def record_network_status():
    '''
    Records the network status and displays it.
    '''

    # Increment the number of recordings of the network
    sim.network_recordings += 1

    # Get the names of all the links and flows in the system.
    all_links = sim.links.keys()
    all_flows = sim.flows.keys()
    
    # Get all of the readings.
    np.append(time_recordings, sim.network_now())

    times.write(str(sim.network_now()) + "\n")

    # Get the link rate, buffer occupancies and packet loss for all links
    for link_name in all_links:
        # If this is the first reading, create entries for links.
        if link_name not in link_rate_readings:
            link_rate_readings[link_name] = []
            buffer_occ_recordings[link_name] = []
            packet_loss_recordings[link_name] = []
        
        link = sim.links[link_name]

        # Update our status arrays. 
        link_rate_readings[link_name].append(link.data_on_link)
        # Update each of the buffer occupancy recordings (two buffers for 
        # each link)
        buffer_occ_1 = link.buffer_load[0] / link.buffer_size
        buffer_occ_2 = link.buffer_load[1] / link.buffer_size

        buffer_occ_recordings[link_name].append((buffer_occ_1, buffer_occ_2))
        packet_loss_recordings[link_name].append(link.num_packets_lost)
        
        link_rates.write(str(link_name) + "," + str(link.data_on_link) + "\n")
        buffer_occs.write(str(link_name) + "," + str(buffer_occ_1) + "," + str(buffer_occ_2) + "\n")
        packet_loss.write(str(link_name) + ',' + str(link.num_packets_lost) + "\n")

    # Get the flow rate, packet delay and window size.
    for flow_name in all_flows:        
        # If first reading, create entries for flows
        if flow_name not in flow_rate_recordings:
            flow_rate_recordings[flow_name] = []
            packet_delay_recordings[flow_name] = []
            window_size_recordings[flow_name] = []
        
        flow = sim.flows[flow_name]

        # Update status arrays
        flow_rate_recordings[flow_name] = 0 # TODO: Get flow rate
        packet_delay_recordings[flow_name] = flow.last_RTT
        window_size_recordings[flow_name] = flow.window_size

        flow_rates.write(str(flow_name) + "," + str(0) + "\n")
        packet_delays.write(str(flow_name) + "," + str(flow.last_RTT) + "\n")
        window_sizes.write(str(flow_name) + "," + str(flow.window_size) + "\n")

    if len(sim.event_queue) > 0:
        # Create the event that will record the network status.
        next_recording = sim.network_now() + ct.RECORD_TIME
        sim.enqueue_event(next_recording, e.Event(None, None, None))




