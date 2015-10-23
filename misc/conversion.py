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