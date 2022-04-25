"""
Business Process :: Pooling()
"""
import numpy as np
import pandas as pd
import constants as cs

from bizprocs.process import BusinessProcess

class Pooling(BusinessProcess):

    def __init__(self):
        super().__init__()
        self.__addEvent__("getDelivery",self.__getDelivery__)
        

    def startup(self, kernel=None):
        # TODO - option for weekly or yearly deliveries
        # possibly governed by constant
        if kernel.options['DELIVERY_SCHEDULE'] == "DAILY":
            self.__scheduleDailyDeliveries__(kernel)            
        elif kernel.options['DELIVERY_SCHEDULE'] == "WEEKLY":
            self.__scheduleWeeklyDeliveries__(kernel)


    def __scheduleDailyDeliveries__(self, kernel):
        # TODO - don't hardcode.
        # Load in from either strategies/daily_delivery.txt
        kernel.event_queue[32400]   = "DeliveryIn"
        kernel.event_queue[378000]  = "DeliveryIn"
        kernel.event_queue[723600]  = "DeliveryIn"
        kernel.event_queue[1069200] = "DeliveryIn"
        kernel.event_queue[1414800] = "DeliveryIn"
        kernel.event_queue[1760400] = "DeliveryIn"     
        kernel.event_queue[2106000] = "DeliveryIn"     
        kernel.event_queue[2451600] = "DeliveryIn"     
        kernel.event_queue[2797200] = "DeliveryIn"     
        kernel.event_queue[3142800] = "DeliveryIn"         


    def __scheduleWeeklyDeliveries__(self, kernel):
        # TODO - don't hardcode.
        # Load in from either strategies/weekly_delivery.txt
        kernel.event_queue[378000]  = "DeliveryIn"
        kernel.event_queue[982800]  = "DeliveryIn"
        kernel.event_queue[1587600] = "DeliveryIn"
        kernel.event_queue[2192400] = "DeliveryIn"
        kernel.event_queue[2797200] = "DeliveryIn"      


    def __getDelivery__(self, kernel=None):
        print("getting a delivery in Pooling()")

        # TODO Check weights
        
        kernel.DATA_STORAGE['parking']['P1'] += np.random.randint(1,100)
        kernel.DATA_STORAGE['parking']['P2'] += np.random.randint(1,100)
        kernel.DATA_STORAGE['parking']['P3'] += np.random.randint(1,100)
        kernel.DATA_STORAGE['parking']['P4'] += np.random.randint(1,100)

        # Update Costs
            # 