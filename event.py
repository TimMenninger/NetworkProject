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
                
                
    #
    # get_elements
    #
    # Description:      Returns the attributes of this event.
    #
    # Arguments:        None.
    #
    # Return Values:    (string) - The name of the actor for the event.
    #                   (string) - The name of the function for the event.
    #                   (list) - A list of arguments for the function.
    #
    # Shared Variables: self.actor (READ) - Returned
    #                   self.function (READ) - Returned
    #                   self.parameters (READ) - Returned
    #
    # Global Variables: None.
    #
    # Limitations:      None.
    #
    # Known Bugs:       None.
    #
    # Revision History: 11/02/15: Created
    #
                
    def get_elements(self):
        '''
        Returns the actor, function and parameters for this event.
        '''
        return self.actor, self.function, self.parameters
