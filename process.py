"""
Business Process
"""
import numpy as np
import pandas as pd
import constants as cs

class BusinessProcess:
    def __init__(self):
        self._function_dict = {}

    def __addEvent__(self, event_name, event_function):
        self._function_dict[event_name] = event_function

    def handleEvent(self, event_name:str, kernel=None):
        print("handling event: {}".format(event_name)) 
        return self._function_dict[event_name](kernel)
        