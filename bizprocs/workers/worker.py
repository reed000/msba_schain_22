"""
Worker Class
"""
import numpy as np
import pandas as pd
import constants as cs

from bizprocs.process import BusinessProcess

class Worker(BusinessProcess):
    def __init__(self, facility=None, kernel=None, num=0):
        super().__init__()       
        # print("Worker()::__init__() is getting ready for the day")        

        # make constant attributes
        self.facility = facility
        self.labor_rate = cs.LABOR_RATE
        self.name = "Worker" + self.facility.name + str(kernel.clock) + '_' + str(num)
        self.start_time = np.nan
        self.end_time = np.nan

        # populate methods
        self.__addEvent__(self.name+"_Terminate",self.__terminate__)

        # present task should keep a record in the same format
        # as the kernel event queue of what this guy is doing
        self.present_task = {}

        # note that the class inhereiting Worker
        # should put __clockIn__ within its init function


    def __clockIn__(self, facility=None, kernel=None):
        # add yourself to the kernel register
        kernel.processes[self.name] = self

        # add all of your events
        for personal_event in self._function_dict:
            kernel.event_dictionary[personal_event] = (self.name, personal_event)

        self.start_time = kernel.clock
        self.__startUpTask__(kernel)


    # should be replaced with what is appropriate for facility
    def __startUpTask__(self, kernel=None):
        pass


    def clockOut(self, kernel=None):
        # check final tasking

        # if there is a present task
        if len(self.present_task):
            # schedule clock out for the second after
            next_available_time = self.present_task.keys[0]+1.0
            kernel.addEvent(next_available_time, self.name + "_Terminate")
        else:
            # immediately terminate
            immediately = kernel.clock+1.0
            kernel.addEvent(immediately, self.name + "_Terminate")


    def __terminate__(self, kernel=None):
        # remove your name from the process list
        kernel.processes.pop(self.name)
        
        # remove your events from the functional dictionary
        for personal_event in self._function_dict:
            kernel.event_dictionary.pop(personal_event)


    def report(self):
        # Print metrics
        print( "I am a {} at ${}".format(self.worker_type, self.labor_rate))
        pass
