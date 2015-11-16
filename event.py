################################################################################
#
# Ricky Galliani, Tim Menninger, Rush Joshi, Schaeffer Reed
# Network Simulator Project
# CS 143 -- Fall 2015
#
# event.py
#
# This file contains the event class, which is a class describing a particular
# event using its actor, function call and parameter list.
#
################################################################################






################################################################################
#                                                                              #
#                               Imported Modules                               #
#                                                                              #
################################################################################

# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h
import event as e

# Import the constants and the conversion functions
import constants as ct
import conversion as cv


################################################################################
#                                                                              #
#                                  Event Class                                 #
#                                                                              #
################################################################################

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
                
                
    def get_elements(self):
        '''
        Returns the actor, function and parameters for this event.
        '''
        return self.actor, self.function, self.parameters
