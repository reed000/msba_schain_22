"""
Business Process
"""
import numpy as np
import pandas as pd
import constants as cs

class BusinessProcess:
    def __init__(self, name=None):
        self._function_dict = {}
        self.name = name

    def __addEvent__(self, event_name, event_function):
        self._function_dict[event_name] = event_function

    def handleEvent(self, event_name:str, kernel=None):
        kernel.addLogs("Clock {} :: Handling event: {} doing {}", [kernel.clock, self.name, event_name])

        return self._function_dict[event_name](kernel)
        