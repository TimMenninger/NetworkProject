############################################################################
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
############################################################################


############################################################################
#                                                                          #
#                               Imported Modules                           #
#                                                                          #
############################################################################


# Import network objects
import packet as p
import link as l
import flow as f
import router as r
import host as h

# Import the constants and the conversion functions
import constants as ct
import conversion as cv


############################################################################
#                                                                          #
#                                  Event Class                             #
#                                                                          #
############################################################################


class Event:

    def __init__(self, in_actor, in_function, in_parameters):
        '''
        Description:        Create an event for the network and all of the 
                            information necessary for execution.

        Arguments:          in_actor (string)
                                - A string indicating which actor is carrying 
                                out this particular event (i.e., "H1").

                            in_function (string)
                                - A string indicating what action is to be 
                                executed for this particular event (i.e., 
                                'check_ack_timeout).

                            in_parameters (list of variable types)
                                - A list containing the parameters that are 
                                necessary to carry out the input function 
                                (i.e., [flow_name (string), packet_ID (string)] 
                                for host.receive_packet())

        Shared Variables:   self.actor (WRITE) 
                                - Initialized
                            
                            self.function (WRITE) 
                                - Initialized
                            
                            self.parameters (WRITE) 
                                - Initialized

        Global Variables:   None.

        Limitations:        None.

        Known Bugs:         None.

        Revision History:   10/20/15: Created
        '''     
        # The object (e.g. Router) that will be executing the event
        self.actor = in_actor
                
        # Function to be executed by the object
        self.function = in_function
                
        # List of parameters for the function being executed
        self.parameters = in_parameters
           

    def get_elements(self):
        '''
        Description:        Returns the attributes of this event.

        Arguments:          None.

        Return Values:      self.actor (string) 
                                - The name of the actor for the event.

                            self.function (string) 
                                - The name of the function for the event.

                            self.parameters (list) 
                                - A list of arguments for the function.

        Shared Variables:   self.actor (READ) 
                                - Returned

                            self.function (READ) 
                                - Returned

                            self.parameters (READ) 
                                - Returned

        Global Variables:   None.

        Limitations:        None.

        Known Bugs:         None.

        Revision History:   11/02/15: Created
        '''
        return self.actor, self.function, self.parameters


