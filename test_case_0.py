
from CS143Project.objects.flow import *
from CS143Project.objects.host import *
from CS143Project.objects.link import *
from CS143Project.objects.packet import *
from CS143Project.objects.router import *

def main():
	'''
	'''
	# Manually enter the network topology, for now
	H1 = Host("H1")
	H2 = Host("H2")
	L1 = Link("L1", 10, 10, 64)
	F1 = Flow("F1", "H1", "H2", 20, 0)
	
	# Make the Packet that splice up the data within the flow
	F1.make_packets()

	# Print out the various network components
	L1.print_contents()
	F1.print_contents(False)

if __name__ == "__main__":
    main()
