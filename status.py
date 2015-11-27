################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# status.py
#
# This contains the code to record the network status at fixed time intervals
# and report the condition of the network at all times throughout the 
# simulation after the networks completion. This involves writing the data 
# collected from the network to a set of output files from which plots 
# that report network metrics can be generated.
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
time_recordings       = np.empty(1)
link_rate_readings    = { } # Indexed by link name, stores link rates
buffer_oc_readings    = { } # Indexed by link name, stores buffer occupancies
packet_loss_readings  = { } # Indexed by link name, stores packet loss
flow_rate_readings    = { } # Indexed by flow name, stores flow rates
packet_delay_readings = { } # Indexed by flow name, stores packet delays (RTT)
window_size_readings  = { } # Indexed by flow name, stores window sizes


#
# open_data_files
#
# Description:      This file opens file instances for each of the six metrics
#                   that must be plotted (as per the project specifications).  
#                   Thus, it enables us to write data collected from the 
#                   network to output files (one file for each metric).        
#
# Arguments:        None
#
# Return Values:    None.
#
# Global Variables:  All the file instances (global to the status module)
#                    - times
#                    - link_rates
#                    - buffer_occs
#                    - packet_loss
#                    - flow_rates
#                    - window_sizes
#                    - packet_delays
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#

def open_data_files():
    '''
    Opens all of the data files that are written to throughout the network
    simulation for data collection.  Additionally, this function writes the 
    'header' line on the first line of each file essentially assigning the 
    attributes for each of the tables.  After the simulation, the data within 
    these files is loaded into pandas DataFrames for easy aggregating/plotting.
    '''
    t = open(ct.TIMES_OUT, 'w')                 # times recordings 
    t.write("time\n")

    lr = open(ct.LINK_RATE_OUT, 'w')            # link rate recordings
    lr.write("link_name,link_rate\n")

    bo = open(ct.BUFFER_OCC_OUT, 'w')           # buffer occupancy recordings
    bo.write("link_name,buffer_occ_1,buffer_occ_2\n")

    pl = open(ct.PACKET_LOSS_OUT, 'w')          # packet loss recordings
    pl.write('link_name,packet_loss\n')

    fr = open(ct.FLOW_RATE_OUT, 'w')            # flow rate recordings
    fr.write('flow_name,flow_rate\n')

    ws = open(ct.WINDOW_SIZE_OUT, 'w')          # window size recordings
    ws.write('flow_name,window_size\n')

    p = open(ct.PACKET_DELAY_OUT, 'w')          # packet delay recordings
    p.write('flow_name,packet_delay\n')

    return (t, lr, bo, pl, fr, ws, p)

# Open the 7 different data files 
(times, 
 link_rates, 
 buffer_occs, 
 packet_loss, 
 flow_rates, 
 window_sizes, 
 packet_delays) = open_data_files()


#
# close_data_files
#
# Description:      This function closes all of the data files that were 
#                   written to throughout the network simulation. It is 
#                   essential that the files are 'closed' in order for pandas
#                   to be able to easily load the data into DataFrames.      
#
# Arguments:        None
#
# Return Values:    None.
#
# Global Variables:  All the file instances (global to the status module)
#                    - times
#                    - link_rates
#                    - buffer_occs
#                    - packet_loss
#                    - flow_rates
#                    - window_sizes
#                    - packet_delays
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#

def close_data_files():
    '''
    Closes all of the data files that are written to throughout the network
    simulation.  This function exists because if the files are not closed 
    then pandas cannot load the data within them into pandas DataFrames.
    '''
    # Officially stop writing to all the files
    times.close()
    link_rates.close()
    buffer_occs.close()
    packet_loss.close()
    flow_rates.close()
    window_sizes.close()
    packet_delays.close()

#
# plot_per_link_metrics
#
# Description:      Uses the matplotlib module to build the three per-link
#                   plots; it is called from construct_plots() where the plots  
#                   are rendered for the user.  The three plots produced are:  
#                       - link rate vs. time           
#                       - buffer occupancy vs. time        
#                       - packet loss vs. time       
#
# Arguments:        None
#
# Return Values:    None.
#
# Global Variables: None
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#

def plot_per_link_metrics(tms, time_max):
    '''
    Builds the three per-link plots: 
        1. link rate vs. time
        2. buffer occupancy vs. time
        3. packet loss vs. time
    '''
    # Create a matplotlib figure to display all of the per-link metrics
    fig_link, ax_link = plt.subplots(3, 1, figsize=(12, 7))
    
    # Have matplotlib manage the layout of the plots
    fig_link.tight_layout()

    # Pull in the link_rate, packet_loss, buffer_occupancy and recordings
    lr = pd.read_csv(ct.LINK_RATE_OUT, 
                     dtype={'link_name': str, 'link_rate': np.float64})
    bf = pd.read_csv(ct.BUFFER_OCC_OUT, 
                     dtype={'link_name': str, 'buffer_occ_1': np.float64, 
                                              'buffer_occ_2': np.float64})
    pl = pd.read_csv(ct.PACKET_LOSS_OUT, 
                     dtype={'link_name': str, 'packet_loss': np.int32})

    # Get the names of all the links in the system.
    all_links = sim.links.keys()

    for link_name in all_links:
        lr_link = lr[lr['link_name'] == link_name]
        bf_link = bf[bf['link_name'] == link_name]
        pl_link = pl[pl['link_name'] == link_name]

        # --- PLOT LINK RATE ---
        # Plot link rate per link  versus time
        ax_link[0].plot(tms['time'], lr['link_rate'], label=link_name)
        ax_link[0].set_title("Link Rate")
        ax_link[0].set_xlim((0, time_max))
        ax_link[0].set_xlabel('Time (ms)')
        ax_link[0].set_ylabel('Link Late (Mbps)')
        ax_link[0].legend()

        # --- PLOT BUFFER OCCUPANCY ---
        # Plot buffer occupancy per link for buffers 1 and 2  versus time
        ax_link[1].plot(tms['time'], bf_link['buffer_occ_1'], 
                                                label=link_name + ", buffer 1")
        ax_link[1].plot(tms['time'], bf_link['buffer_occ_2'], 
                                                label=link_name + ", buffer 2")
        ax_link[1].set_xlim((0, time_max))
        ax_link[1].set_title("Buffer Occupancy")
        ax_link[1].set_xlabel('Time (ms)')
        ax_link[1].set_ylabel('Buffer Occupancy (pkts)') 
        ax_link[1].legend()   

        # --- PLOT PACKET LOSS ---
        # Plot packet loss per link versus time
        ax_link[2].plot(tms['time'], pl['packet_loss'], label=link_name)
        ax_link[2].set_xlim((0, time_max))
        ax_link[2].set_title("Packet Loss")
        ax_link[2].set_xlabel('Time (ms)')
        ax_link[2].set_ylabel('Packet Loss (pkts)') 
        ax_link[2].legend()

#
# plot_per_flow_metrics
#
# Description:      Uses the matplotlib module to build the three per-flow
#                   plots; it is called from construct_plots() where the plots 
#                   are rendered for the user.  The three plots produced are 
#                       - flow rate vs. time           
#                       - packet delay vs. time        
#                       - window size vs. time       
#
# Arguments:        None
#
# Return Values:    None.
#
# Global Variables: None
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#

def plot_per_flow_metrics(tms, time_max):
    '''
    Builds the three per-flow plots: 
        1. flow rate vs. time
        2. packet delay vs. time
        3. window size vs. time
    ''' 
    # Create a matplotlib figure to display all of the per-flow metrics
    fig_flow, ax_flow = plt.subplots(3, 1, figsize=(12, 7))

    # Have matplotlib manage the layout of the plots
    fig_flow.tight_layout()

    # Pull in the flow_rate recordings, window_size, packet_delay recordings
    fr = pd.read_csv(ct.FLOW_RATE_OUT, 
                     dtype={'flow_name': str, 'flow_rate': np.float64})
    ws = pd.read_csv(ct.WINDOW_SIZE_OUT, 
                     dtype={'flow_name': str, 'window_size': np.int32})
    py = pd.read_csv(ct.PACKET_DELAY_OUT, 
                     dtype={'flow_name': str, 'packet_delay': np.float64})

    # Get the names of all the flows in the system.
    all_flows = sim.flows.keys()

    for flow_name in all_flows:
        # Pull out the rows of the DataFrames containing data for this flow 
        fr_flow = fr[fr['flow_name'] == flow_name]
        ws_flow = ws[ws['flow_name'] == flow_name]
        py_flow = py[py['flow_name'] == flow_name]

        # --- PLOT FLOW RATE ----
        # Plot the flow_rate recordings versus time for this link
        ax_flow[0].plot(tms['time'], fr_flow['flow_rate'], label=flow_name)
        ax_flow[0].set_xlim((0, time_max))
        ax_flow[0].set_title("Flow Rate")
        ax_flow[0].set_xlabel('Time (ms)')
        ax_flow[0].set_ylabel('Flow Rate (Mbps)') 
        ax_flow[0].legend()

        # --- PLOT WINDOW SIZE ---
        # Plot the window_size recordings versus time for this flow
        ax_flow[1].plot(tms['time'], ws_flow['window_size'], label=flow_name)
        ax_flow[1].set_xlim((0, time_max))
        ax_flow[1].set_title("Window Size")
        ax_flow[1].set_xlabel('Time (ms)')
        ax_flow[1].set_ylabel('Window Size (pkts)') 
        ax_flow[1].legend()

        # --- PLOT PACKET DELAY --- 
        # Plot the packet_delay recordings  versus time for this flow
        ax_flow[2].plot(tms['time'], py_flow['packet_delay'], label=flow_name)
        ax_flow[2].set_xlim((0, time_max))
        ax_flow[2].set_ylim((0, py['packet_delay'].max() + 10))
        ax_flow[2].set_title("Packet Delay")
        ax_flow[2].set_xlabel('Time (ms)')
        ax_flow[2].set_ylabel('Packet Delay (ms)')  
        ax_flow[2].legend()

#
# construct_plots
#
# Description:      Constructs the six required plots to satisfy the project
#                   specfications.  This includes a plot for the 3 per-link
#                   metrics and a plot for the 3 per-flow metrics. 
#
# Arguments:        None
#
# Return Values:    None.
#
# Global Variables: None
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#

def construct_plots():
    '''
    Constructs (via plot_per_link_metrics() and plot_per_flow_metrics())
    and displays the six required plots:
    1. link rate vs. time            (per link) 
    2. buffer occupancy vs. time     (per link, per buffer) 
    3. packet loss vs. time          (per link)
    4. flow rate vs. time            (per flow) 
    5. packet delay vs. time         (per flow)) 
    6. window size vs. time          (per flow)
    '''
    # Stop writing to all of the output files so that we can pull data from
    # them and load them into pandas DataFrames.
    close_data_files()

    # Pull in the time recordings which are used for both the per-link and
    # per-flow metrics.
    tms = pd.read_csv(ct.TIMES_OUT, dtype={'time': np.int32})
    time_max = tms['time'].max()

    # Plot the per-link metrics.
    plot_per_link_metrics(tms, time_max)

    # Plot the per-flow metrics.
    plot_per_flow_metrics(tms, time_max) 

    # Render the plots.
    plt.show()


#
# update_and_write_link_data
#
# Description:      This function updates the link data structures given the new 
#                   data that has been collected within the network.  
#                   Additionally, it writes the data to the three link output
#                   files.  
#
# Arguments:        link (Link) 
#
# Return Values:    None.
#
# Global Variables: 
#                    - link_rate_readings (WRITE)
#                    - buffer_occ_readings (WRITE)
#                    - packet_loss_readings (WRITE)
#                    - link_rates (WRITE)
#                    - buffer_occs (WRITE)
#                    - packet_loss (WRITE)
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#    

def update_and_write_link_data(link):
    '''
    Given a link, this function updates the global data structures that track
    the status of the link's various attributes and writes output data to the
    output files. 
    '''
    link_name = link.link_name
    # --- UPDATE STATUS DATA STRUCTURES --- 
    # Link rate readings
    link_rate_readings[link_name].append(link.data_on_link)
    # Buffer occupancy recordings (two buffers for each link)
    buffer_occ_1 = link.buffer_load[0] / link.buffer_size
    buffer_occ_2 = link.buffer_load[1] / link.buffer_size
    buffer_oc_readings[link.link_name].append((buffer_occ_1, buffer_occ_2))
    # Packet loss readings
    packet_loss_readings[link_name].append(link.num_packets_lost)
    
    # --- WRITE TO DATA FILES ---
    # Link rate readings
    link_rates.write(str(link_name) + "," + str(link.data_on_link) + "\n")
    # Buffer occupancy readings (two buffers for each link)
    buf_row = str(link_name) + "," + str(buffer_occ_1) + "," + str(buffer_occ_2)
    buffer_occs.write(buf_row + "\n")
    # Packet loss readings
    packet_loss.write(str(link_name) + ',' + str(link.num_packets_lost) + "\n")


#
# update_and_write_flow_data
#
# Description:      This function updates the link data structures given the new 
#                   data that has been collected within the network.  
#                   Additionally, it writes the data to the three flow output
#                   files.  
#
# Arguments:        flow (Flow) 
#
# Return Values:    None.
#
# Global Variables: 
#                    - flow_rate_readings (WRITE)
#                    - packet_delay_readings (WRITE)
#                    - window_size_readings (WRITE)
#                    - flow_rates (WRITE)
#                    - packet_delays (WRITE)
#                    - window_sizes (WRITE)
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/19: Created and filled in.
#  

def update_and_write_flow_data(flow):
    '''
    Given a flow, this function updates the global data structures that track
    the status of the link's various attributes and writes output data to the
    output files. 
    '''
    flow_name = flow.flow_name
    # --- UPDATE STATUS DATA STRUCTURES --- 
    # Flow rate readings
    flow_rate_readings[flow_name] = 0 # TODO: Get flow rate
    # Packet delay readings
    packet_delay_readings[flow_name] = flow.last_RTT
    # Window size readings
    window_size_readings[flow_name] = flow.window_size

    # --- WRITE TO DATA FILES ---
    # Flow rate readings
    flow_rates.write(str(flow_name) + "," + str(0) + "\n")
    # Packet delay readings
    packet_delays.write(str(flow_name) + "," + str(flow.last_RTT) + "\n")
    # Window size readings
    window_sizes.write(str(flow_name) + "," + str(flow.window_size) + "\n")


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
#                   buffer_oc_readings (WRITE) - Buffer occupancy appended
#                   packet_loss_readings (WRITE) - Packet loss appended
#                   flow_rate_readings (WRITE) - Flow rate appended
#                   packet_delay_readings (WRITE) - Packet Delay appended
#                   window_size_readings (WRITE) - Window size recorded
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
            buffer_oc_readings[link_name] = []
            packet_loss_readings[link_name] = []
        
        # Get the link associated with this link name.
        link = sim.links[link_name]

        # Update the data structures and write link data to the 3 link output 
        # files.
        update_and_write_link_data(link)

    # Get the flow rate, packet delay and window size.
    for flow_name in all_flows:        
        # If first reading, create entries for flows
        if flow_name not in flow_rate_readings:
            flow_rate_readings[flow_name] = []
            packet_delay_readings[flow_name] = []
            window_size_readings[flow_name] = []
        
        # Get the flow associated with this flow name
        flow = sim.flows[flow_name]

        # Update the data structures and write flow data to the 3 flow output
        # files
        update_and_write_flow_data(flow)

    # Create the event that will record the network status, but only if there
    #   is nothing else in the event queue.  Otherwise, this will keep the
    #   network running indefinitely.  The one flow running that is allowed
    #	is the routing flow.
    if len(sim.running_flows) > 1:
        next_recording = sim.network_now() + ct.RECORD_TIME
        sim.enqueue_event(next_recording, e.Event(None, None, None))




