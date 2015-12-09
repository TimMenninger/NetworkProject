##########################################################################
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
##########################################################################

# Output figure dimensions
FIG_WID				 = 12
FIG_LEN 			 = 7

# Directories that outputs are written to
OUTPUT_DIRECTORY	 = "../out/"
INPUT_DIRECTORY		 = "../in/"
DATA_DIRECTORY		 = OUTPUT_DIRECTORY + "data/"
LOG_DIRECTORY		 = OUTPUT_DIRECTORY + "log/"
TESTS_DIRECTORY		 = INPUT_DIRECTORY  + "test_configs/"

# Log output filenames
MAIN_LOG_FILE 	 	 = LOG_DIRECTORY    + "main.log"
HOST_LOG_FILE 	     = LOG_DIRECTORY    + "host.log"
ROUTER_LOG_FILE 	 = LOG_DIRECTORY    + "router.log"
FLOW_LOG_FILE    	 = LOG_DIRECTORY    + "flow.log"

# Data output filenames
TIMES_OUT 			 = DATA_DIRECTORY   + "times.csv"
LINK_RATE_OUT 		 = DATA_DIRECTORY   + "link_rate.csv"
BUFFER_OCC_OUT 		 = DATA_DIRECTORY   + "buffer_occupancy.csv"
PACKET_LOSS_OUT 	 = DATA_DIRECTORY   + "packet_loss.csv"
HOST_RECEIVE_OUT 	 = DATA_DIRECTORY   + "host_receive.csv"
HOST_SEND_OUT 		 = DATA_DIRECTORY   + "host_send.csv"
FLOW_RATE_OUT 		 = DATA_DIRECTORY   + "flow_rate.csv"
WINDOW_SIZE_OUT 	 = DATA_DIRECTORY   + "window_size.csv"
PACKET_DELAY_OUT 	 = DATA_DIRECTORY   + "packet_delay.csv"

# Test case file names
TEST_CASE_0_FILENAME = TESTS_DIRECTORY  + "case_0.txt"
TEST_CASE_1_FILENAME = TESTS_DIRECTORY  + "case_1.txt"
TEST_CASE_2_FILENAME = TESTS_DIRECTORY  + "case_2.txt"

# Smallest timestep we use.  Needs to be ~0 because it is used to ensure one
#   "simultaneous" event occurs before another.
TIME_BIT 			 = 0		# Changed to zero because the heapqueue has
								#	been re-implemented to not need this...

# How often to record the network status in milliseconds
RECORD_TIME 		 = 1

# The number of network recordings used to produce rate metrics 
RECORD_DELTA 	     = 75

# The number of seconds for each recording delta (in seconds)
DELTA_SECS 			 = (RECORD_TIME * RECORD_DELTA) / 1000

# How often to send routing packets to configure routing tables (in ms)
CONFIG_PKT_TIME 	 = 500

# The number of milliseconds before routers assume they are receiving no more
#	useful packets to update routing tables.
ROUTING_TIMEOUT		 = 150

# Network objects
TYPE_FLOW 			 = 0
TYPE_LINK 			 = 1
TYPE_ROUTER 		 = 2
TYPE_HOST 			 = 3
TYPE_PACKET 		 = 4

# Congestion Control algorithm
FLOW_FAST_TCP        = 0
FLOW_TCP_RENO        = 1
DEFAULT_ALG          = FLOW_TCP_RENO

# Packet types
PACKET_DATA          = 0
PACKET_ACK           = 1
PACKET_ROUTING       = 2

# Packet sizes in bytes
PACKET_DATA_SIZE     = 1024  		# Size of data Packet in bytes
PACKET_ACK_SIZE      = 64    		# Size of ack Packet in bytes
PACKET_ROUTING_SIZE  = 64    		# Size of routing Packet in bytes

# Ack packet prefixt
PACKET_ACK_PREFIX 	 = 'ack_'

# Status codes
SUCCESS              = 0    		# Operation was success
LINK_ERROR           = 1    		# Unknown error with link
LINK_FULL            = 2    		# Link was full


MAX_SIMULATION_TIME  = 1e6  		# Maximum number of milliseconds the 
									# 	network should run
                            
# Initial values
ACK_TIMEOUT_FACTOR  = 3     # Number of milliseconds to wait for acknowledgement
                            # before timeout
INITIAL_ASSUMED_RTT = 500.0 # Before we know the round trip time, we need to
                            #   define an initial one that we assume (in ms)
INITIAL_WINDOW_SIZE = 1.0   # The initial window size for each flow.

ALPHA_VALUE 		= 15 	# The alpha value for FAST TCP window update in 
							#	pkts/sec

# How often FAST TCP window update should be called (in milliseconds)
FAST_TCP_PERIOD		 = 100
							# Optimal values:
FAST_TCP_TIMEOUT_FACTOR = 8 # Case 0: 8, Case 1: 1.35, Case 2:

# The name of the flow used for inter-router communication
ROUTING_FLOW         = 'routing_flow'

# The guessed number of consecutive packets that are sent (on average) on a
#	link before transmission must stop to reverse direction of data travel
#	on the half-duplex links.
CONSEC_PKTS			 = 10

# The number of consecutive epochs with no routing table update before 
# 	deciding the router has nothing more to learn from routing packets and can 
# 	start using the new routing table
MAX_NO_IMPROVES		 = 3


