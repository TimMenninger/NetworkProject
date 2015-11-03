################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# utilities.py
#
# This contains the utilities module.  This is where a number of random 
# utility functions are defined.
#
################################################################################






################################################################################
#                                                                              #
#                                   Functions                                  #
#                                                                              #
################################################################################

#
# print_dict_keys
#
# Description:      Prints all of the items in the dictionary.
#
# Arguments:        dict_name (string) - The name of the dictionary.
#                   dict (dictionary) - The dictionary whose contents are to be
#                       printed.
#
# Return Values:    None.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/22: Created
#

def print_dict_keys(dict_name, dict):
    '''
    Prints the keys of a dictionary.
    '''
    print("- " + dict_name + " -")
    for key in dict.keys():
        print("\t" + key)
