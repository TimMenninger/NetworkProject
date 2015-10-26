# Host Class

class Host:

	def __init__(self, the_host_name):
		''' 
		Initialize an instance of Host by intitializing its attributes.
		'''
		# Name of the host, each hostname is unique string (i.e., "H1")
		self.host_name = the_host_name
		
		# The link_name representing the Link to this Host
		self.link = None
		
	def set_link():
		'''
		Alters the 'links' attribute of the Host to reflect the link
		connecting the Host to the network.
		'''

	def send_packet():
		'''
		Sends a Packet from this Host to a particular destination.  Then, it 
		adds the appropriate subsequent event to the Simulator event queue.
		'''

	def receive_packet():
		'''
		Receives a Packet from a Link.  Then, it adds the appropriate event to 
		the Simulator event queue.
		'''

	def print_contents():
		'''
		Prints what is contained in all of the attributes of this Host.
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
