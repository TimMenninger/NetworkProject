############################################################################
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
############################################################################


############################################################################
#                                                                          #
#                                   Functions                              #
#                                                                          #
############################################################################


def MB_to_bits(num_in_MB):
    '''
    Converts the parameter given in MB to bits and returns the result.
    '''
    return num_in_MB * (8 * (10 ** 6))

def MB_to_bytes(num_in_MB):
	'''
	Converts the parameter given in MB to bytes and returns it.
	'''
	return num_in_MB * (10 ** 6)

def bits_to_KB(num_in_bits):
    '''
    Converts the parameter given in bits to KB and returns the result.
    '''
    return num_in_bits / 8000

def KB_to_bits(num_in_KB):
    '''
    Converts the parameter given in KB to bits and returns the result.
    '''
    return num_in_KB * 8000
    
def bytes_to_Mb(num_in_bytes):
    '''
    Converts the parameter given in bytes to Mb and returns it.
    '''
    return (1.0 * num_in_bytes) / (8 * 10 ** 6)

def KB_to_bytes(num_in_KB):
	'''
	Converts the parameter given in KB to bytes and returns it.
	'''
	return num_in_KB * 1000

def bits_to_MB(num_in_bits):
    '''
    Converts the parameter to MB and returns the result.
    '''
    return (1.0 * num_in_bits) / (8 * (10 ** 6))


def MB_to_KB(num_in_MB):
    '''
    Converts the parameter given in MB to KB and returns the result.
    '''
    return num_in_MB * 1000
    
    
def bytes_to_MB(num_in_bytes):
    '''
    Converts the parameter given in bytes to MB and returns it.
    '''
    return (1.0 * num_in_bytes) / (10 ** 6)



