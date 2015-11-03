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
# get_info
#
# Description:      Returns the actor, function and parameters of this event
#                   instance.
#
# Arguments:        self (Event)
#
# Return Values:    self.actor (Union) - The actor for the argued event.  This
#                       can be a flow, host, link, packet, router, etc.
#                   self.function (FnPtr) - A pointer to the function that this
#                       event represents.
#                   self.parameters (List) - A list of parameters for the 
#                       function this Event represents.
#
# Shared Variables: self.actor (READ) - Returned by this function.
#                   self.function (READ) - Returned by this function.
#                   self.parameters (READ) - Returned by this function.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/11/02: Created
#
        
    def get_info(self):
        '''
        Returns the actor, function and parameters for this event.
        '''
        return self.actor, self.function, self.parameters
            
                
#
# print_contents
#
# Description:      Prints the attributes and their contained values.  This is
#                   used mainly for debugging purposes.
#
# Arguments:        self (Event)
#
# Return Values:    None.
#
# Shared Variables: None.
#
# Global Variables: None.
#
# Limitations:      None.
#
# Known Bugs:       None.
#
# Revision History: 2015/10/??: Created function handle
#
                
    def print_contents(self):
        '''
        Prints contents of this event.
        '''
