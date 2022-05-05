"""
Business Process :: Pooling()
"""
import numpy as np
import pandas as pd
import constants as cs
import math

from bizprocs.process import BusinessProcess
from bizprocs.facilities.storing import Storage

DAILY_DELIVER_FILE = 'strategies/daily_delivery.csv'
WEEKLY_DELIVER_FILE = 'strategies/weekly_delivery.csv'

class Pooling(BusinessProcess):

    def __init__(self):
        super().__init__(name="Pooling")
        self.__addEvent__("DeliveryIn",self.__getDelivery__)
        self.delivery_queue = {}

    def startup(self, kernel=None):
        if kernel.options['DELIVERY_SCHEDULE'] == "DAILY":
            kernel.DATA_STORAGE.add_cost('delivery', cs.DELIVERY_COST_DAILY)
            self.__read_strategy__(DAILY_DELIVER_FILE, kernel)

        elif kernel.options['DELIVERY_SCHEDULE'] == "WEEKLY":
            kernel.DATA_STORAGE.add_cost('delivery', cs.DELIVERY_COST_WEEKLY)
            self.__read_strategy__(WEEKLY_DELIVER_FILE, kernel)
        else:
            self.__read_strategy__('_TEST_', kernel)

    def __read_strategy__(self, file_path, kernel=None):
        """ Reading Delivery Strategy to self.delivery_queue
        param file_path: string of file path of queue 
        return: None
        """

        timestamp = 0
        if file_path == "_TEST_":
            # HARDCODE DELIVERIES
            for q in [32400, 378000, 723600, 1069200, 1414800]:
                # kernel.addEvent(new_time, "DeliveryIn") ----- OLD CODE
                # ADD to Kernel EVENT_QUEUE, get the deconflicted time
                new_time, _ = kernel.addEvent(q, "DeliveryIn")

                self.delivery_queue[new_time] = {
                    'P1': 400,
                    'P2': 500,
                    'P3': 600,
                    'P4': 700
                }

        else:
            # DYNAMIC FILE DELIVERIES
            delivery_df = pd.read_csv(file_path)
            for index, row in delivery_df.iterrows():
                # self.delivery_queue[row['Timestamp']] = {
                #     'P1': row['P1'],
                #     'P2': row['P2'],
                #     'P3': row['P3'],
                #     'P4': row['P3']
                # }
                # kernel.addEvent(row['Timestamp'], "DeliveryIn") ----- OLD CODE

                # ADD to Kernel EVENT_QUEUE, get the deconflicted time
                new_time, _ = kernel.addEvent(row['Timestamp'], "DeliveryIn")

                self.delivery_queue[new_time] = {
                    'P1': row['P1'],
                    'P2': row['P2'],
                    'P3': row['P3'],
                    'P4': row['P3']
                }
                
        return self.delivery_queue
 
    def get_ship_weight(self, shipment):
        weight = 0
        weight += shipment['P1'] * cs.P1_WEIGHT
        weight += shipment['P2'] * cs.P2_WEIGHT
        weight += shipment['P3'] * cs.P3_WEIGHT
        weight += shipment['P4'] * cs.P4_WEIGHT
        return weight

    def __getDelivery__(self, kernel=None):
        shipment = self.delivery_queue[kernel.clock]

        try:
            del self.delivery_queue[kernel.clock]
        except KeyError:
            pass
        # print(self.delivery_queue.keys())

        # TODO Check weights
        curr_parking_weight = kernel.DATA_STORAGE.get_parking_weight()
        ship_weight = self.get_ship_weight(shipment)

        surplus = (curr_parking_weight + ship_weight) - cs.PARKING_LIMIT
        # print("DELIVERY {} PROCESS: {} {}".format(kernel.clock, ship_weight, surplus))
        if surplus <= 0:
            # Add shipment to parking
            kernel.DATA_STORAGE.add_parking_shipment(shipment)
        else:
            frac = surplus/ship_weight
            
            new_ship = {
                'P1' : math.floor(shipment['P1'] * frac),
                'P2' : math.floor(shipment['P2'] * frac),
                'P3' : math.floor(shipment['P3'] * frac),
                'P4' : math.floor(shipment['P4'] * frac)
                }

            # allow max shipment
            kernel.DATA_STORAGE.add_parking_shipment(new_ship)

            # add return penalty cost
            if kernel.options['DELIVERY_SCHEDULE'] == "DAILY":
                kernel.DATA_STORAGE.add_cost('delivery', cs.DELIVERY_COST_DAILY)
            elif kernel.options['DELIVERY_SCHEDULE'] == "WEEKLY":
                kernel.DATA_STORAGE.add_cost('delivery', cs.DELIVERY_COST_WEEKLY)

        # print("DELIVERY {} PROCESSED: {} {}".format(kernel.clock, ship_weight, surplus))
                        
        # Poke the stowage workers in case they are being lazy
        kernel.addEvent(kernel.clock + 1e-1, "PokeWorkersStorage")