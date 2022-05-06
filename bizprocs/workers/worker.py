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

        # make constant attributes
        self.facility = facility
        self.name = "Worker" + self.facility.name + str(kernel.clock) + '_' + str(num)
        self.start_time = np.nan
        self.end_time = np.nan

        # present task should keep a record in the same format
        # as the kernel event queue of what this guy is doing
        self.present_task = {}

        # guard value preventing new tasking if it's time to clock out
        self.last_task = False

        # variables for monitoring idleness
        self.idle = False
        self.idle_time = 0.0 # accumulated clock time of idleness
        self.idle_start = 0.0 # clock time of when the idleness started last

        # populate methods
        self.__addEvent__(self.name+"_Terminate",self.__terminate__)        

        # note that the class inhereiting Worker
        # should put __clockIn__ within its init function

        # IDLE state can be generalized here

    def __addWorkerEvent__(self, kernel, time_in, event_in):
            # reset the present task
            self.present_task = {}

            # if we're already clocking out just get out
            if self.last_task == True:
                return

            # add it to the kernel's queue
            time_scheduled, event_scheduled = kernel.addEvent(time_in, event_in)

            # and store what you're doing in case you go off shift
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
        # if there is a present task
        terminate_time = kernel.clock
        if len(self.present_task):
            # schedule clock out for the second after
            terminate_time = min(self.present_task, key=self.present_task.get) + 1e-1
            self.present_task = {}
        else:
            # immediately terminate
            terminate_time = kernel.clock + 1e-1
        
        self.end_time = terminate_time
        kernel.addEvent(terminate_time, self.name + "_Terminate")

        self.last_task = True


    def __terminate__(self, kernel=None):
        # remove your name from your facility worker list
        self.facility.workers.pop(self.name)

        # remove your name from the process list
        kernel.processes.pop(self.name)
        
        # remove your events from the functional dictionary
        for personal_event in self._function_dict:
            kernel.event_dictionary.pop(personal_event)
        
        # Pay the Worker for the good deeds
        self.__pay_worker__(kernel)


    # this method should be mostly invoked using super()
    def poke(self, kernel=None):
        self.idle = False
        self.idle_time += (kernel.clock - self.idle_start)


    def __idling__(self, kernel=None):
        # reset the present task
        self.present_task = {}
        self.idle = True
        self.idle_start = kernel.clock


    def __pay_worker__(self, kernel=None):
        """
        you may use seconds as the minimal unit calculation for continuous payment
        """
        labor_time = self.end_time - self.start_time
        paycheck = round(labor_time/3600 * cs.LABOR_RATE)  # Hourly rate

        kernel.DATA_STORAGE.costs['labor'] += paycheck
        # print( "{} paid ${}".format(self.name, paycheck))

        # do one last poke to log the accumulated time.
        if self.idle:
            self.poke(kernel)

        # also keep track of working time and idle time in the log
        kernel.DATA_STORAGE.work_time[self.facility.name] += labor_time
        kernel.DATA_STORAGE.idle_time[self.facility.name] += self.idle_time
        
    def report(self):
        # print metrics
        pass
