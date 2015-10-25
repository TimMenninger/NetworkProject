class Event:

        def __init__(self, execution_time, object_executing, function_executing, parameters):
                '''
                Create an event for the network and all of the information necessary
                for execution.
                '''
                
                #! Description: At time self.execution_time milliseconds, the Simulator should
                #       call (self.executor).(self.function)(self.parameters)
                
                # The time (in simulation time milliseconds) the event is to occur
                self.execution_time = execution_time
                
                # The object (e.g. Router) that will be executing the event
                self.executor = object_executing
                
                # The function to be executed by the object
                self.function = function_executing
                
                # A list of parameters for the function being executed
                self.parameters = parameters
                
                
        def print_contents():
                '''
                Prints contents of this event.
                '''
