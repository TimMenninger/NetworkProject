#
# event.py
#
# This file contains the event class, which is a class describing a particular
# event using its actor, function call and parameter list.
#


from CS143Project.objects.packet import *
from CS143Project.objects.link import *
from CS143Project.objects.flow import *
from CS143Project.objects.router import *
from CS143Project.objects.simulator import *
from CS143Project.objects.host import *

class Event:

	def __init__(self, in_actor, in_function, in_parameters):
    	'''
		Create an event for the network and all of the information necessary
		for execution.
		'''
                
		#! Description: When the event is called, the Simulator should call
		#       (self.executor).(self.function)(self.parameters)
                
		# The object (e.g. Router) that will be executing the event
		self.actor = in_actor
                
 		# Function to be executed by the object
		self.function = in_function
                
		# List of parameters for the function being executed
		self.parameters = in_parameters
                
                
		def print_contents():
		'''
		Prints contents of this event.
		'''
