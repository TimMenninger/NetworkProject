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


################################################################################
#                                                                              #
#                                   Functions                                  #
#                                                                              #
################################################################################


#
# MB_to_bits
#
# Description:		This converts the argued number of megabytes to the number
#					of bits it represents.
#
# Arguments:		num_in_MB (integer) - The number of megabytes to be
#						conerted to bits.
#
# Return Values:	(integer) - The number of bits that make up the argued
#						value.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/??: Created
#

def MB_to_bits(num_in_MB):
	'''
	Converts the parameter to bits and returns the result.
	'''
	return num_in_MB * (8 * (10 ** 6))
	


#
# bits_to_MB
#
# Description:		This converts the argued number of bits to the number of
#					of megabytes it represents.
#
# Arguments:		num_in_bits (integer) - The number of bits to be converted
#						to bits.
#
# Return Values:	(integer) - The number of MB that make up the argued number
#						of bits.
#
# Global Variables:	None.
#
# Limitations:		None.
#
# Known Bugs:		None.
#
# Revision History: 2015/10/??: Created
#

def bits_to_MB(num_in_bits):
	'''
	Converts the parameter to MB and returns the result.
	'''
	return (1.0 * num_in_bits) / (8 * (10 ** 6))