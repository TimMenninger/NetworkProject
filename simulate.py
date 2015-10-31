#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# simulate.py
#
# This module contains functions that are required to carry out a network 
# simulation.
#

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

def compute_routing_tables():
	'''
	Sets the routing tables for the network.
	'''
	
def create_initial_events():
	'''
	This takes the set of flows and their descriptors and fills the event queue
	with events that signify the start of the respective flow.
	'''