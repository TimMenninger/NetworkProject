################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# constants.py
#
# This contains the constants module. It stores the constants
# that are referred to from all of the modules in the project.
#
################################################################################

# Log output filename 
OUTPUT_LOG_FILE = "misc/log/case_0.log"

# Data output filenames
TIMES_OUT = "misc/data/times.csv"
LINK_RATE_OUT = "misc/data/link_rate.csv"
BUFFER_OCC_OUT = 'misc/data/buffer_occupancy.csv'
PACKET_LOSS_OUT = 'misc/data/packet_loss.csv'
FLOW_RATE_OUT = 'misc/data/flow_rate.csv'
WINDOW_SIZE_OUT = 'misc/data/window_size.csv'
PACKET_DELAY_OUT = 'misc/data/packet_delay.csv'

# Test case file names
TEST_CASE_0_FILENAME = "misc/test_configs/case_0.txt"
TEST_CASE_1_FILENAME = "misc/test_configs/case_1.txt"
TEST_CASE_2_FILENAME = "misc/test_configs/case_2.txt"

# Smallest timestep we use
TIME_BIT = 0.00001

# How often to record the network status in milliseconds
RECORD_TIME = 1

# How often to send routing packets to configure routing tables (in ms)
CONFIG_PKT_TIME = 50

# Network objects
TYPE_FLOW = 0
TYPE_LINK = 1
TYPE_ROUTER = 2
TYPE_HOST = 3
TYPE_PACKET = 4

# Congestion Control algorithm
FLOW_FAST_TCP       = 0
FLOW_TCP_RENO       = 1

# Packet types
PACKET_DATA         = 0
PACKET_ACK          = 1
PACKET_ROUTING      = 2

# Packet sizes in bytes
PACKET_DATA_SIZE    = 1024  # Size of data Packet in bytes
PACKET_ACK_SIZE     = 64    # Size of ack Packet in bytes
PACKET_ROUTING_SIZE = 64    # Size of routing Packet in bytes

# Ack packet prefix
PACKET_ACK_PREFIX = 'ack_'

# Status codes
SUCCESS             = 0     # Operation was success
LINK_ERROR          = 1     # Unknown error with link
LINK_FULL           = 2     # Link was full

# Time constants
RECORDING_INTERVAL  = 10    # Number of milliseconds between each network 
                            # status recording
MAX_SIMULATION_TIME = 1e6   # Maximum number of milliseconds the network should 
                            # run

# Initial values
ACK_TIMEOUT_FACTOR  = 3     # Number of milliseconds to wait for acknowledgement
                            # before timeout
INITIAL_ASSUMED_RTT = 100   # Before we know the round trip time, we need to
                            #   define an initial one that we assume (in ms)
INITIAL_WINDOW_SIZE = 4     # The initial window size for each flow.

# The name of the flow used for inter-router communication
ROUTING_FLOW        = 'routing_flow'
