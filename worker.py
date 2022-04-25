"""
Worker Class
"""
import numpy as np
import pandas as pd
import constants as cs

class Worker():

    def __init__(self):
        print("Kernel()::__init__() is initializing some cool stuff")
        self.worker_type = 0

        self.start_time = 0
        self.end_time = 0

        self.labor_rate = 0

        self.data = []
        
        self.startShift()
        self.endShift()

    def startShift():
        pass
    
    def endShift():
        pass 

    def report(self):
        # Print metrics
        print( "I am a {} at ${}".format(self.worker_type, self.labor_rate))
        pass


class Stower(Worker):
    def __init__(self, start_shift, end_shift):
        print("Kernel()::__init__() is initializing some cool stuff")
        self.worker_type = "STOWER"

        self.start_time = start_shift
        self.end_time = end_shift

        self.labor_rate = 22.5

        self.data = []
        

if __name__ == "__main__":
    worker1 = Stower()
    worker1.report()

