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


def MB_to_bits(num_in_MB):
    '''
    Converts the parameter to bits and returns the result.
    '''
    return num_in_MB * (8 * (10 ** 6))


def bits_to_KB(num_in_bits):
    '''
    Converts the parameter to KB and returns the result.
    '''
    return num_in_bits / 8000

def KB_to_bits(num_in_KB):
    '''
    Converts the parameter to bits and returns the result.
    '''
    return num_in_KB * 8000

def bits_to_MB(num_in_bits):
    '''
    Converts the parameter to MB and returns the result.
    '''
    return (1.0 * num_in_bits) / (8 * (10 ** 6))


def MB_to_KB(num_in_MB):
    '''
    Converts the parameter to KB and returns the result.
    '''
    return num_in_MB * 1000
    
    
def bytes_to_MB(num_in_bytes):
    '''
    Converts the parameter to MB and returns it.
    '''
    return (1.0 * num_in_bytes) / (10 ** 6)





