#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# conversion.py
#
# This contains the conversion module.  This is where functions that convert
# between common network units (i.e., MB, bits) are defined and implemented.
#

# Conversion helper functions

def MB_to_bits(num_in_MB):
	'''
	Converts the parameter to bits and returns the result.
	'''
	return num_in_MB * (8 * (10 ** 6))

def bits_to_MB(num_in_bits):
	'''
	Converts the parameter to MB and returns the result.
	'''
	return (1.0 * num_in_bits) / (8 * (10 ** 6))
	
def MB_to_bytes(num_in_MB):
	'''
	Converts the parameter to bytes.
	'''
	return num_in_MB * (10 ** 6)
