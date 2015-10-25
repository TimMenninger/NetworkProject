# Host Class

class Host:

	def __init__(self, the_host_name):
		''' 
		Initialize an instance of Host by intitializing its attributes.
		'''
		# Name of the host, each hostname is unique string (i.e., "H1")
		self.host_name = the_host_name
		
		# Keep a list of links to this host.
		self.link = None
		
	def set_link():
		'''
		'''

	def send_packet():
		'''
		'''

	def receive_packet():
		'''
		'''

	def print_contents():
		'''
		'''

	# def sendPacket(self, packet):
	# 	'''
	# 	Send a packet.
	# 	'''
	# 	# Send the packet onto the link.
	# 	self.link.carry_packet(packet)
		
	# 	# We are now waiting for acknowledgement
	# 	self.waiting_for_ack[packet.ID] = packet
		
		
	# def receivePacket(self, packet):
	# 	'''
	# 	Receive a packet and react to it.
	# 	'''
	# 	# If it is an acknowledgement, update to reflect no longer waiting
	# 	if packet.type == Packet_Types.ack:
	# 		self.waitingForAck.pop(packet.ID)
		
	# 	# If it is data, record the data.
	# 	elif packet.type == Packet_Types.data:
	# 		self.receivedData.append(packet)
