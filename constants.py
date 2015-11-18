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




TIME_BIT = .00001

# Test case file names
TEST_CASE_0_FILENAME = "misc/test_configs/case_0.txt"
TEST_CASE_1_FILENAME = "misc/test_configs/case_1.txt"
TEST_CASE_2_FILENAME = "misc/test_configs/case_2.txt"

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

# Status codes
SUCCESS             = 0     # Operation was success
LINK_ERROR          = 1     # Unknown error with link
LINK_FULL           = 2     # Link was full

# Time constants
RECORDING_INTERVAL  = 10    # Number of milliseconds between each network 
                            # status recording
MAX_SIMULATION_TIME = 1e6   # Maximum number of milliseconds the network should 
                            # run


ACK_TIMEOUT_FACTOR  = 2     # Number of milliseconds to wait for acknowledgement
                            # before timeout
INITIAL_ASSUMED_RTT = 50    # Before we know the round trip time, we need to
                            #   define an initial one that we assume (in ms)
INITIAL_WINDOW_SIZE = 16     # The initial window size for each flow.
