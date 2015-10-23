
# Packet sizes (in bits)
PACKET_DATA_SIZE = 1024 # Size of data Packet
PACKET_ACK_SIZE = 64 # Size of ack Packet
PACKET_ROUTING_SIZE = 64 # Size of routing Packet

# Constants indicating whether link is used/free
LINK_FREE = 0 # Link free in both directions
LINK_USED_HIGH = 1 # Link used in direction of higher Host/Router name
LINK_USED_LOW = -1 # Link used in direction of lower Host/Router name
		