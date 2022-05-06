"""
Business Process :: Ordering()
Generate Orders
"""
import numpy as np
import pandas as pd
import constants as cs
import math
import warnings

from bizprocs.process import BusinessProcess
from ..utilities.order import Order
from scipy.stats import truncnorm
from scipy.stats import weibull_min


class Orders(BusinessProcess):
    def __init__(self):
        super().__init__(name="Orders")
        self.__addEvent__("OrderUp",self.__newOrder__)
        self.master_orders = {}

    def __generateOrderInterval__(self, day, shift):
        """
        Weibull Model on a 4 shift basis to generate Next order interval
        """
        lambda_value = cs.DISTRIBUTION['{}_{}'.format(day, shift)]['order_lambda']
        k_value = cs.DISTRIBUTION['{}_{}'.format(day, shift)]['order_k']
  
        # order_time = weibull_min.rvs(k_value, loc=0, scale=1/lambda_value, size=1)[0]
        order_time = (1/lambda_value) * np.random.weibull(k_value)

        return(round(order_time))

    def __generateProductQuant__(self, day, shift, product):
        """
        Normal Distribution to generate product distribution
        """
        n_val = cs.DISTRIBUTION['{}_{}'.format(day, shift)]['{}_n'.format(product)]
        p_val = cs.DISTRIBUTION['{}_{}'.format(day, shift)]['{}_p'.format(product)]

        p_min = 0
        p_max = cs.P_UPPER_LIM[product]
        
        # TODO easy method discrete norm
        # self.__get_truncated_normal__(mean_val, std_val, p_min, p_max)
        # prod_quant = max(min(round(np.random.normal(mean_val, std_val)), p_max), 0)

        # Method Gamma
        # prod_quant = min(round(np.random.gamma(1.5, scale=1.1, size=1)[0]), p_max)

        # No max
        prod_quant = round(np.random.negative_binomial(n_val, p_val, size=1)[0])
        
        return prod_quant
        
    def __get_truncated_normal__(self, mean=0, sd=1, low=0, upp=10):
        return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

    def __generateOrder__(self, kernel=None):
        """
        Normal Distribution to generate product distribution
        """
        order_dict = {
                 'P1' : 0,
                 'P2' : 0,
                 'P3' : 0,
                 'P4' : 0
            }
        order_valid = False
        while order_valid == False:
            # pull clock
            # extract day and shift
            day, shift = kernel.get_day_and_shift(kernel.clock)
            shift = int(shift)
            
            for p in order_dict.keys():
                # get product quant
                quant = self.__generateProductQuant__(day, shift, p)
                order_dict[p] = quant
            
            order_valid = Orders.__validateOrder__(order_dict, 0, kernel)
        
        # get order time
        order_int = self.__generateOrderInterval__(day, shift)

        # ADD to Next Order to Event_Queue AT clock+Interval: get the deconflicted time
        new_time, _ = kernel.addEvent(kernel.clock + order_int, "OrderUp")

        if kernel.options['SAVE_ORDERS']:
            kernel.DATA_STORAGE.save_order(new_time, order_dict)

        # Append VALID ORder to master orders
        self.master_orders[new_time] = order_dict

    def startup(self, kernel=None):
        # POPULATE SIMULATION: introduce distribution simulated orders
        if not kernel.options['ORDER_TEST']:
            self.__generateOrder__(kernel)
        else:
            print("READING ORDER FILE: {}".format(kernel.options['ORDER_FILE']))
            order_df = pd.read_csv(kernel.options['ORDER_FILE'])

            for index, row in order_df.iterrows():
                order_dict = {
                     'P1' : row['QtyShirt'],
                     'P2' : row['QtyHoodie'],
                     'P3' : row['QtySweatpants'],
                     'P4' : row['QtySneakers']
                }

                # order validity check, if not just move along
                order_valid = Orders.__validateOrder__(order_dict, index, kernel)
                if not order_valid:
                    continue

                # final paranoia check on the data
                if not order_dict:
                    warnings.warn("EMPTY! {}, {}".format(order_dict, index))

                # ADD to Kernel EVENT_QUEUE, get the deconflicted time
                new_time, _ = kernel.addEvent(row['OrderTimeInSec'], "OrderUp")

                # Save Master Orders
                self.master_orders[new_time] = order_dict

    def __newOrder__(self, kernel=None):
        # Pull From Master Orders
        new_order = self.master_orders[kernel.clock]
        
        if not new_order:
            warnings.warn("EMPTY! {} at {}".format(new_order, kernel.clock))
        
        # ADD to Kernal orders queue - CREATE new ORDER()
        das_order = Order(kernel.clock, new_order)

        # kernel.orders.append(das_order)
        kernel.orders.put(das_order)

        # Poke the picker workers in case they are being lazy
        kernel.addEvent(kernel.clock + 1e-1, "PokeWorkersPicking")

        # Generate Next Order
        if not kernel.options['ORDER_TEST']:
            self.__generateOrder__(kernel)
            # TODO: delete from master_orders

    @staticmethod
    def __validateOrder__(order, order_index, kernel):
        contents = np.array(list(order.values()))
        valid = True
        if any(contents < 0) or all(contents == 0):
            if kernel.options['ORDER_TEST']:
                warnings.warn("Order {} had non-valid entry at index {}".format(order, order_index))
            valid = False

        return valid