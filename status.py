############################################################################
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
import warnings

############################################################################
#                                                                          #
#                             Status Functions                             #
#                                                                          #
############################################################################


def open_data_files():
    '''
    Description:        This function opens file instances for each of the six 
                        metrics that must be plotted (as per the project 
                        specifications). Thus, it enables us to write data 
                        collected from the network to output files (one file 
                        for each metric).        

    Arguments:          None

    Return Values:      None.

    Global Variables:   ct.TIMES_OUT (WRITE)

                        ct.LINK_RATE_OUT (WRITE)

                        ct.BUFFER_OCC_OUT (WRITE)

                        ct.PACKET_LOSS_OUT (WRITE)

                        ct.FLOW_RATE_OUT (WRITE)

                        ct.WINDOW_SIZE_OUT (WRITE)

                        ct.PACKET_DELAY_OUT (WRITE)

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
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


def close_data_files():
    '''
    Description:        This function closes all of the data files that were 
                        written to throughout the network simulation. It is 
                        essential that the files are 'closed' in order for 
                        pandas to be able to easily load the data into 
                        DataFrames.      

    Arguments:          None

    Return Values:      None.

    Shared Variables:   times (WRITE)

                        link_rates (WRITE)

                        buffer_occs (WRITE) 

                        packet_loss (WRITE)

                        flow_rates (WRITE)

                        window_sizes (WRITE)

                        packet_delays (WRITE)

    Global Variables:   All the file instances (global to the status module)
                    
    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
    '''
    # Officially stop writing to all the files
    times.close()
    link_rates.close()
    buffer_occs.close()
    packet_loss.close()
    flow_rates.close()
    window_sizes.close()
    packet_delays.close()


def plot_per_link_metrics(tms, time_max):
    '''
    Description:        Uses the matplotlib module to build the three per-link
                        plots; it is called from construct_plots() where the 
                        plots are rendered for the user.  The three plots 
                        produced are:  
                          - link rate vs. time           
                          - buffer occupancy vs. time        
                          - packet loss vs. time       

    Arguments:          time_max (integer)
                            - Used as the maximum x-coordinate on the plots.

    Return Values:      None.

    Global Variables:   sim.links (READ)

                        ct.LINK_RATE_OUT (READ)

                        ct.BUFFER_OCC_OUT (READ)

                        ct.PACKET_LOSS_OUT (READ)

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
    '''
    # Get the names of all the links in the system.
    all_links = list(sim.links.keys())

    # Create a matplotlib figure to display link rate metrics for each link
    fig_link_rate, ax_link_rate = plt.subplots(len(all_links), 1, 
                                            figsize=(ct.FIG_WID, ct.FIG_LEN))

    # Create a matplotlib figure to display buffer occupancy metrics for each 
    # link
    fig_buf_occ, ax_buf_occ = plt.subplots(len(all_links), 1, 
                                        figsize=(ct.FIG_WID, ct.FIG_LEN))

    # Create a matplotlib figure to display packet loss metrics for each 
    # link
    fig_pack_loss, ax_pack_loss = plt.subplots(len(all_links), 1, 
                                        figsize=(ct.FIG_WID, ct.FIG_LEN))

    # Let matplotlip straighten out/properly-size figures
    fig_link_rate.tight_layout()
    fig_buf_occ.tight_layout()
    fig_pack_loss.tight_layout()

    # Pull in the link_rate, packet_loss, buffer_occupancy and recordings
    lr = pd.read_csv(ct.LINK_RATE_OUT, 
                     dtype={'link_name': str, 'link_rate': np.float64})
    bf = pd.read_csv(ct.BUFFER_OCC_OUT, 
                     dtype={'link_name': str, 'buffer_occ_1': np.float64, 
                                              'buffer_occ_2': np.float64})
    pl = pd.read_csv(ct.PACKET_LOSS_OUT, 
                     dtype={'link_name': str, 'packet_loss': np.int32})

    if len(all_links) > 1:
        for i, link_name in enumerate(all_links):

            lr_link = lr[lr['link_name'] == link_name]
            bf_link = bf[bf['link_name'] == link_name]
            pl_link = pl[pl['link_name'] == link_name]

            # --- PLOT LINK RATE ---
            # Plot link rate per link versus time
            plot_metric(ax_link_rate[i],                     # Plot
                        tms['time'],                         # X
                        lr_link['link_rate'],                # Y
                        "Link Rate (" + link_name + ")",     # Title
                        "seconds",                           # X-axis
                        "Mbps",                              # Y-axis
                        None,                                # Line label
                        time_max,                            # Max-X
                        False)                               # No legend

            # --- PLOT BUFFER OCCUPANCY ---
            # Plot buffer occupancy per link for buffers 1 and 2 versus time

            # First, buffer 1
            plot_metric(ax_buf_occ[i],                          # Plot
                        tms['time'],                            # X
                        bf_link['buffer_occ_1'],                # Y
                        "Buffer Occupancy (" + link_name + ")", # Title
                        "seconds",                              # X-axis
                        "pkts",                                 # Y-axis
                        "buffer 1",                             # Line label
                        time_max,                               # Max-X
                        True)                                   # Yes legend


            # Next, buffer 2
            plot_metric(ax_buf_occ[i],                          # Plot
                        tms['time'],                            # X
                        bf_link['buffer_occ_2'],                # Y
                        "Buffer Occupancy (" + link_name + ")", # Title
                        "seconds",                              # X-axis
                        "pkts",                                 # Y-axis
                        "buffer 2",                             # Line label
                        time_max,                               # Max-X
                        True)                                   # Yes legend


            # --- PLOT PACKET LOSS ---
            # Plot packet loss per link versus time
            plot_metric(ax_pack_loss[i],                        # Plot
                        tms['time'],                            # X
                        pl_link['packet_loss'],                 # Y
                        "Packet Loss (" + link_name + ")",      # Title
                        "seconds",                              # X-axis
                        "pkts",                                 # Y-axis
                        None,                                   # Line label
                        time_max,                               # Max-X
                        False)                                  # Yes legend

    else: # Only 1 link 
        link_name = all_links[0]

        # --- PLOT LINK RATE ---
        # Plot link rate per link  versus time
        plot_metric(ax_link_rate,                        # Plot
                    tms['time'],                         # X
                    lr['link_rate'],                     # Y
                    "Link Rate (" + link_name + ")",     # Title
                    "seconds",                           # X-axis
                    "Mbps",                              # Y-axis
                    None,                                # Line label
                    time_max,                            # Max-X
                    False)                               # No legend

        # --- PLOT BUFFER OCCUPANCY ---
        # Plot buffer occupancy per link for buffers 1 and 2  versus time
        
        # First, buffer 1
        plot_metric(ax_buf_occ,                             # Plot
                    tms['time'],                            # X
                    bf['buffer_occ_1'],                     # Y
                    "Buffer Occupancy (" + link_name + ")", # Title
                    "seconds",                              # X-axis
                    "pkts",                                 # Y-axis
                    "buffer 1",                             # Line label
                    time_max,                               # Max-X
                    True)                                   # Yes legend


        # Next, buffer 2
        plot_metric(ax_buf_occ,                             # Plot
                    tms['time'],                            # X
                    bf['buffer_occ_2'],                     # Y
                    "Buffer Occupancy (" + link_name + ")", # Title
                    "seconds",                              # X-axis
                    "pkts",                                 # Y-axis
                    "buffer 2",                             # Line label
                    time_max,                               # Max-X
                    True)                                   # Yes legend

        # --- PLOT PACKET LOSS ---
        # Plot packet loss per link versus time 
        plot_metric(ax_pack_loss,                           # Plot
                    tms['time'],                            # X
                    pl['packet_loss'],                      # Y
                    "Packet Loss (" + link_name + ")",      # Title
                    "seconds",                              # X-axis
                    "pkts",                                 # Y-axis
                    None,                                   # Line label
                    time_max,                               # Max-X
                    False)                                  # Yes legend


def plot_per_flow_metrics(tms, time_max):
    '''
    Description:        Uses the matplotlib module to build the three per-flow
                        plots; it is called from construct_plots() where the 
                        plots are rendered for the user.  The three plots 
                        produced are: 
                            - flow rate vs. time           
                            - packet delay vs. time        
                            - window size vs. time       

    Arguments:          time_max (integer)
                            - Used as the maximum x-coordinate on the plots.

    Return Values:      None.

    Global Variables:   sim.flows (READ)

                        ct.FLOW_RATE_OUT (READ)

                        ct.WINDOW_SIZE_OUT (READ)

                        ct.PACKET_DELAY_OUT (READ)

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
    ''' 
    # Get all the names of the flows except the routing flow, which we don't
    # need to plot metrics for
    all_flows = [x for x in list(sim.flows.keys()) if x != ct.ROUTING_FLOW]

    # Create a matplotlib figure to display flow rate metrics for each flow
    fig_flow_rate, ax_flow_rate = plt.subplots(len(all_flows), 1, 
                                            figsize=(ct.FIG_WID, ct.FIG_LEN))

    fig_win_size, ax_win_size = plt.subplots(len(all_flows), 1, 
                                            figsize=(ct.FIG_WID, ct.FIG_LEN))

    fig_pack_del, ax_pack_del = plt.subplots(len(all_flows), 1, 
                                            figsize=(ct.FIG_WID, ct.FIG_LEN))

    # Let matplotlip straighten out/properly-size figures
    fig_flow_rate.tight_layout()
    fig_win_size.tight_layout()
    fig_pack_del.tight_layout()

    # Pull in the flow_rate recordings, window_size, packet_delay recordings
    fr = pd.read_csv(ct.FLOW_RATE_OUT, 
                     dtype={'flow_name': str, 'flow_rate': np.float64})
    ws = pd.read_csv(ct.WINDOW_SIZE_OUT, 
                     dtype={'flow_name': str, 'window_size': np.int32})
    py = pd.read_csv(ct.PACKET_DELAY_OUT, 
                     dtype={'flow_name': str, 'packet_delay': np.float64})

    if len(all_flows) > 1:
        for i, flow_name in enumerate(all_flows):
            # Pull out the rows of the DataFrames containing data for this flow 
            fr_flow = fr[fr['flow_name'] == flow_name]
            ws_flow = ws[ws['flow_name'] == flow_name]
            py_flow = py[py['flow_name'] == flow_name]

            # --- PLOT FLOW RATE ----
            # Plot the flow_rate recordings versus time for this link
            plot_metric(ax_flow_rate[i],                        # Plot
                        tms['time'],                            # X
                        fr_flow['flow_rate'],                   # Y
                        "Flow Rate (" + flow_name + ")",        # Title
                        "seconds",                              # X-axis
                        "Mbps",                                 # Y-axis
                        None,                                   # Line label
                        time_max,                               # Max-X
                        False)                                  # No legend

            # --- PLOT WINDOW SIZE ---
            # Plot the window_size recordings versus time for this flow
            plot_metric(ax_win_size[i],                         # Plot
                        tms['time'],                            # X
                        ws_flow['window_size'],                 # Y
                        "Window Size (" + flow_name + ")",      # Title
                        "seconds",                              # X-axis
                        "pkts",                                 # Y-axis
                        None,                                   # Line label
                        time_max,                               # Max-X
                        False)                                  # No legend

            # --- PLOT PACKET DELAY --- 
            # Plot the packet_delay recordings  versus time for this flow
            plot_metric(ax_pack_del[i],                         # Plot
                        tms['time'],                            # X
                        py_flow['packet_delay'],                # Y
                        "Packet Delay (" + flow_name + ")",     # Title
                        "seconds",                              # X-axis
                        "milliseconds",                         # Y-axis
                        None,                                   # Line label
                        time_max,                               # Max-X
                        False)                                  # No legend

    else: # only 1 Flow! 
        flow_name = all_flows[0]

        # --- PLOT FLOW RATE ----
        # Plot the flow_rate recordings versus time 
        plot_metric(ax_flow_rate,                           # Plot
                    tms['time'],                            # X
                    fr['flow_rate'],                        # Y
                    "Flow Rate (" + flow_name + ")",        # Title
                    "seconds",                              # X-axis
                    "Mbps",                                 # Y-axis
                    None,                                   # Line label
                    time_max,                               # Max-X
                    False)                                  # Yes legend

        # --- PLOT WINDOW SIZE ---
        # Plot the window_size recordings versus time for this flow
        plot_metric(ax_win_size,                            # Plot
                    tms['time'],                            # X
                    ws['window_size'],                      # Y
                    "Window Size (" + flow_name + ")",      # Title
                    "seconds",                              # X-axis
                    "pkts",                                 # Y-axis
                    None,                                   # Line label
                    time_max,                               # Max-X
                    False)                                  # No legend

        # --- PLOT PACKET DELAY --- 
        # Plot the packet_delay recordings versus time 
        plot_metric(ax_pack_del,                            # Plot
                    tms['time'],                            # X
                    py['packet_delay'],                     # Y
                    "Packet Delay (" + flow_name + ")",     # Title
                    "seconds",                              # X-axis
                    "milliseconds",                         # Y-axis
                    None,                                   # Line label
                    time_max,                               # Max-X
                    False)                                  # No legend


def plot_metric(p, x, y, title, x_label, y_label, in_label, time_max, legend):
    '''
    Description:        Adds a line to a plot with the given curve parameters.

    Arguments:          p (matplotlib plot)
                            - The plot to add the metric curve to.

                        x (pandas DataFrame)
                            - The x-values.

                        y (pandas DataFrame)
                            - The y-values.

                        title (string)
                            - Title of the metric plot.

                        x_label (string)
                            - Label of the x-axis.

                        y_label (string)
                            - Label of the y-axis.

                        in_label (string)
                            - Label of the curve itself (can be None).

                        time_max (float/int)
                            - Maximum value of the x-axis.

                        legend (boolean)
                            - Whether or not to plot a legend on the plot.

    Return Values:      None.

    Global Variables:   None.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/29: Created and filled in.
    '''
    # Plot the values
    if in_label == None:
        p.plot(x, y)
    else: # There is a label, plot it as well!
        p.plot(x, y, label=in_label)
    
    p.set_title(title)              # Title
    p.set_xlim((0, time_max))       # Scale the x-axis
    p.set_xlabel(x_label)           # Set the x-axis label
    p.set_ylabel(y_label)           # Set the y-axis label
        
    if legend:
        p.legend()


def construct_plots():
    '''
    Description:        Constructs the six required plots to satisfy the 
                        project specfications.  This includes a plot for the 
                        3 per-link metrics and a plot for the 3 per-flow 
                        metrics. 

                        1. link rate vs. time            (per link) 
                        2. buffer occupancy vs. time     (per link, per buffer) 
                        3. packet loss vs. time          (per link)
                        4. flow rate vs. time            (per flow) 
                        5. packet delay vs. time         (per flow)) 
                        6. window size vs. time          (per flow)

    Arguments:          None

    Return Values:      None.

    Global Variables:   None.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
    '''
    # Stop writing to all of the output files so that we can pull data from
    # them and load them into pandas DataFrames.
    close_data_files()

    # Pull in the time recordings which are used for both the per-link and
    # per-flow metrics.
    tms = pd.read_csv(ct.TIMES_OUT, dtype={'time': np.float64})
    time_max = tms['time'].max()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # Plot the per-link metrics.
        plot_per_link_metrics(tms, time_max)

        # Plot the per-flow metrics.
        plot_per_flow_metrics(tms, time_max) 

    # Render the plots.
    plt.show()
 

def update_and_write_link_data(link):
    '''
    Description:        This function updates the link data structures given 
                        the new  data that has been collected within the 
                        network. Additionally, it writes the data to the 
                        three link output files.  

    Arguments:          link (Link) 

    Return Values:      None.

    Global Variables:   None.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
    '''
    link_name = link.link_name
    # --- WRITE TO DATA FILES ---
    
    # Link rate readings
    link_rates.write(str(link_name) + "," + str(link.data_on_link) + "\n")
    
    # Buffer occupancy recordings (two buffers for each link)
    buffer_occ_1 = link.buffer_load[0] / link.buffer_size
    buffer_occ_2 = link.buffer_load[1] / link.buffer_size

    # Buffer occupancy readings (two buffers for each link)
    buf_row = str(link_name) + "," + str(buffer_occ_1) + "," + \
              str(buffer_occ_2)
    buffer_occs.write(buf_row + "\n")
    
    # Packet loss readings
    pack_row = str(link_name) + ',' + str(link.num_packets_lost) + "\n"
    packet_loss.write(pack_row)


def update_and_write_flow_data(flow):
    '''
    Description:        This function updates the link data structures given 
                        the new data that has been collected within the 
                        network. Additionally, it writes the data to the three 
                        flow output files.  

    Arguments:          flow (Flow) 

    Return Values:      None.

    Global Variables:   None.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/19: Created and filled in.
    '''
    flow_name = flow.flow_name

    # --- WRITE TO DATA FILES ---
    
    # Flow rate readings
    flow_rates.write(str(flow_name) + "," + str(0) + "\n")
    
    # Packet delay readings
    packet_delays.write(str(flow_name) + "," + str(flow.last_RTT) + "\n")
    
    # Window size readings
    window_sizes.write(str(flow_name) + "," + str(flow.window_size) + "\n")

    
def record_network_status():
    '''
    Description:        Records the status of the network at the current time.  
                        It then creates a new event for the next network 
                        recording. Before doing this, however, it checks if 
                        there are events in the queue. 

    Arguments:          unused_list (List) 
                            - Done in this way so we can enqueue this as an 
                            event in our event queue heapqueue.  Defaults to 
                            None so it can be called without arguments.

    Return Values:      None.

    Global Variables:   network_time (READ) 
                            - Used as the independent variable when creating 
                            graphs.
                      
                        times (WRITE) 
                            - Time appended.

    Limitations:        None.

    Known Bugs:         None.

    Revision History:   2015/11/02: Created function handle and docstring.
                        2015/11/16: Filled in global arrays.
                        2015/11/18: Enqueued next network_recording event.
    '''

    # Increment the number of recordings of the network
    sim.network_recordings += 1

    # Get the names of all the links and flows in the system.
    all_links = sim.links.keys()
    # Get all the names of the flows except the routing flow, which we don't
    # need to plot metrics for
    all_flows = [x for x in list(sim.flows.keys()) if x != ct.ROUTING_FLOW]

    # Write out each time to the 'times' csv file, converting each data point
    # from milliseconds to seconds
    times.write(str(sim.network_now() / 1000) + "\n")

    # Get the link rate, buffer occupancies and packet loss for all links
    for link_name in all_links:
        # Get the link associated with this link name.
        link = sim.links[link_name]

        # Update the data structures and write link data to the 3 link output 
        # files.
        update_and_write_link_data(link)

    # Get the flow rate, packet delay and window size.
    for flow_name in all_flows:        
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


