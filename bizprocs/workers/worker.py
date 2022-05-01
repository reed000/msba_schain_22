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
        # # print("Worker()::__init__() is getting ready for the day")        

        # make constant attributes
        self.facility = facility
        self.labor_rate = cs.LABOR_RATE
        self.name = "Worker" + self.facility.name + str(kernel.clock) + '_' + str(num)
        self.start_time = np.nan
        self.end_time = np.nan

        # present task should keep a record in the same format
        # as the kernel event queue of what this guy is doing
        self.present_task = {}

        # guard value preventing new tasking if it's time to clock out
        self.last_task = False

        # populate methods
        self.__addEvent__(self.name+"_Terminate",self.__terminate__)        

        # note that the class inhereiting Worker
        # should put __clockIn__ within its init function

    def __addWorkerEvent__(self, kernel, time_in, event_in):
            # reset the present task
            self.present_task = {}

            # if we're already clocking out just get out
            if self.last_task == True:
                return

            # add it to the kernel's queue
            time_scheduled, event_scheduled = kernel.addEvent(time_in, event_in)

            # and store what you're doing in case you go off shift
            # print("{} :: Storing {} at {} in {}"\
            #    .format(kernel.clock, event_scheduled, time_scheduled, self.name))
            self.present_task[time_scheduled] = event_scheduled

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
        # print(self.name+" is done for the day, man.")

        # print("{} :: is there a length? {}".format(kernel.clock,len(self.present_task)))
        # if there is a present task
        if len(self.present_task):
            # schedule clock out for the second after
            next_available_time = min(self.present_task, key=self.present_task.get) + 1e-3
            kernel.addEvent(next_available_time, self.name + "_Terminate")
            
            # print(str(kernel.clock) + \
            #    " {} 's last task ending {}"\
            #        .format(self.name,self.present_task))

            self.present_task = {}
        else:
            # immediately terminate
            immediately = kernel.clock + 1e-3
            kernel.addEvent(immediately, self.name + "_Terminate")

        self.last_task = True


    def __terminate__(self, kernel=None):
        # remove your name from the process list
        kernel.processes.pop(self.name)
        
        # remove your events from the functional dictionary
        for personal_event in self._function_dict:
            kernel.event_dictionary.pop(personal_event)


    def report(self):
        # # print metrics
        # print( "I am a {} at ${}".format(self.worker_type, self.labor_rate))
        pass
