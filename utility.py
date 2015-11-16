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

def print_dict_keys(dict_name, dict):
	'''
	Prints the keys of a dictionary.
	'''
	print("- " + dict_name + " -")
	for key in dict.keys():
		print("\t" + key)