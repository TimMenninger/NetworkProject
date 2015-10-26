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
