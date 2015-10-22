from objects.flow import *
from objects.host import *
from objects.link import *
from objects.packet import *
from objects.router import *

def main():
	'''
	'''
	# Manually enter the network topology, for now
	H1 = Host("H1")
	H2 = Host("H2")
	L1 = Link("L1", 10, 10, 64)
	F1 = Flow("F1", "H1", "H2", 20, 0)
	
	# Fill up the flow with packets
	F1.get_packets()

	# Print out the various network components
	L1.print_contents()
	F1.print_contents(False)
	for i in range(3):
		p = F1.packets[i]
		p.print_contents()

if __name__ == "__main__":
    main()