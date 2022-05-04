import constants as cs

class DataStore():
    def __init__(self):
        self.parking = {
                'P1':0,
                'P2':0,
                'P3':0,
                'P4':0
            }

        self.storage = {
            'Area1': {'P1':0,
                      'P2':0,
                      'P3':0,
                      'P4':0},
            'Area2': {'P1':0,
                      'P2':0,
                      'P3':0,
                      'P4':0},
            'Area3': {'P1':0,
                      'P2':0,
                      'P3':0,
                      'P4':0},
            'Area4': {'P1':0,
                      'P2':0,
                      'P3':0,
                      'P4':0}
        }

        # TODO temporary to test out picker functionality
        self.temp_packing = {
            'P1':0,
            'P2':0,
            'P3':0,
            'P4':0
        }


        # dictionary to store working time (in seconds)
        self.work_time = {
            "Packing" : 0.0,
            "Picking" : 0.0,
            "Storage" : 0.0
        }


        # dictionary to store idle time (in seconds)
        self.idle_time = {
            "Packing" : 0.0,
            "Picking" : 0.0,
            "Storage" : 0.0
        }


        # TODO Add total IDLE time 
        self.costs = {
                'labor': 0,
                'delivery': 0,
                'lost_sales': 0,
                'facilities_fxd': cs.FXD_FACILITY, #$5M for year
                'packing_stn': 0,
                'inventory_hldg': 0
            }
        self.revenue = 0
        self.product = ['P1', 'P2', 'P3', 'P4']
        self.product_names = ['Tshirt', 'Hoodie', 'Sweatpants', 'Sneakers']

        # dictionary of format {time : all logs}
        # to eventually dump into a dataframe at simulation end
        self._state_dict = {}
    
    def get_KPIs(self):
        kpi = {
            "                   Revenue": self.revenue,
            "        (Delivery Expense)": self.costs['delivery'],
            "      {Lost Sales Penalty)": self.costs['lost_sales'],
            "           (Labor Expense)": self.costs['labor'],
            "   (Facilities Fixed Cost)": self.costs['facilities_fxd'],
            " (Packing Station Expense)": self.costs['packing_stn'],
            "  (Inventory Holding Cost)": self.costs['inventory_hldg'],
            "------------TOTAL PROFIT =": self.revenue - self.get_total_cost(),
            "--------------------------": "--------------------------",
            "    Total Parking Weight =": "{:.2f} %".format(self.get_parking_weight()),
            "-----Utilization Storage =": "{:.2f} %".format(100.*(self.work_time["Storage"] - self.idle_time["Storage"]) / self.work_time["Storage"]),
            "-----Utilization Picking =": "{:.2f} %".format(100.*(self.work_time["Picking"] - self.idle_time["Picking"]) / self.work_time["Picking"]),
            "-----Utilization Packing =": "{:.2f} %".format(100.*(self.work_time["Packing"] - self.idle_time["Packing"]) / self.work_time["Packing"])
        }
        return kpi

    def __str__(self):
        out_str = "KPIs\n"
        out_str += str(self.parking)
        out_str += str(self.get_total_cost)
        # out_str += "\n KPIS: \n{}".format(str(self.get_KPIs()))       ## TODO ENABLE FOR FINAL OUTPUT

        return out_str
            
    def get_parking_weight(self):
        weight = 0
        weight += self.parking['P1'] * cs.P1_WEIGHT
        weight += self.parking['P2'] * cs.P2_WEIGHT
        weight += self.parking['P3'] * cs.P3_WEIGHT
        weight += self.parking['P4'] * cs.P4_WEIGHT
        return weight


    def __get_curr_inventory__(self):
        """ Add up all inventory
        """ 
        # Start with Parking
        total_inventory = self.parking

        # Add Storage
        for area in self.storage:
            for prod in self.storage[area]:
                total_inventory[prod] += self.storage[area][prod]
        
        # Add Packing/Outbound TODO
        return total_inventory
    
    def add_holding_cost(self):                                        # TODO IMPLEMENT USAGE
        """Add holding cost at daily level
        """
        inventory = self.get_curr_inventory()
        for prod in inventory:
            if prod == 'P1':
                self.costs['inventory_hldg'] += inventory[prod] * cs.P1_HOLDING_COST
            elif prod == 'P2':
                self.costs['inventory_hldg'] += inventory[prod] * cs.P2_HOLDING_COST
            elif prod == 'P3':
                self.costs['inventory_hldg'] += inventory[prod] * cs.P3_HOLDING_COST
            else:
                self.costs['inventory_hldg'] += inventory[prod] * cs.P4_HOLDING_COST
    
    def get_max_cnt_parking(self):
        """Return Max Count Parking Spot
        """
        max_cnt_parking = 0
        max_Park = 'N/A'
        for p in self.product:
            if self.parking[p] > max_cnt_parking:
                max_cnt_parking = self.parking[p]
                max_Park = p
        
        return max_Park
    
    def get_max_weight_parking(self):
        """Return Max Weight Parking Spot
        """
        weight_now = {
            'P1' : self.parking['P1'] * cs.P1_WEIGHT,
            'P2' : self.parking['P2'] * cs.P2_WEIGHT,
            'P3' : self.parking['P3'] * cs.P3_WEIGHT,
            'P4' : self.parking['P4'] * cs.P4_WEIGHT
        }

        max_weight_key = max(weight_now, key=weight_now.get)

        # if it's a list that means there's equivalent values
        if type(max_weight_key) is list:
            # arbitrarily pick the first one
            max_weight_key = max_weight_key[0]
        
        return max_weight_key

    def add_parking_shipment(self, shipment):
        """Add Delivery shipment to Parking Inventory
        shipment = Dict{} with product and count
        """
        for p in self.product:
            self.parking[p] = self.parking[p] + shipment[p]
    
    def add_cost(self, cost_key, value):
        self.costs[cost_key] = self.costs[cost_key] + value
    
    def get_total_cost(self):
        total = 0
        for k in self.costs.keys():
            total += self.costs[k]
        
        return total
    
    def get_profit(self):
        return (self.revenue - self.get_total_cost())
        
    def save_state(self, time=0.0):
        
        self._state_dict[time] = {
            'parking_p1'            : self.parking['P1'],
            'parking_p2'            : self.parking['P2'],
            'parking_p3'            : self.parking['P3'],
            'parking_p4'            : self.parking['P4'],
            'storage_a1_p1'         : self.storage['Area1']['P1'],
            'storage_a1_p2'         : self.storage['Area1']['P2'],
            'storage_a1_p3'         : self.storage['Area1']['P3'],
            'storage_a1_p4'         : self.storage['Area1']['P4'],
            'storage_a2_p1'         : self.storage['Area2']['P1'],
            'storage_a2_p2'         : self.storage['Area2']['P2'],
            'storage_a2_p3'         : self.storage['Area2']['P3'],
            'storage_a2_p4'         : self.storage['Area2']['P4'],
            'storage_a3_p1'         : self.storage['Area3']['P1'],
            'storage_a3_p2'         : self.storage['Area3']['P2'],
            'storage_a3_p3'         : self.storage['Area3']['P3'],
            'storage_a3_p4'         : self.storage['Area3']['P4'],
            'storage_a4_p1'         : self.storage['Area4']['P1'],
            'storage_a4_p2'         : self.storage['Area4']['P2'],
            'storage_a4_p3'         : self.storage['Area4']['P3'],
            'storage_a4_p4'         : self.storage['Area4']['P4'],
            'temp_packing_p1'       : self.temp_packing['P1'],
            'temp_packing_p2'       : self.temp_packing['P2'],
            'temp_packing_p3'       : self.temp_packing['P3'],
            'temp_packing_p4'       : self.temp_packing['P4'],
            'costs_labor'           : self.costs['labor'],
            'costs_delivery'        : self.costs['delivery'],
            'costs_lost_sales'      : self.costs['lost_sales'],
            'costs_facilities_fxd'  : self.costs['facilities_fxd'],
            'costs_packing_stn'     : self.costs['packing_stn'],
            'costs_inventory_hldg'  : self.costs['inventory_hldg'],
            'revenue'               : self.revenue,
            'time_worked_storage'   : self.work_time['Storage'],
            'time_worked_picking'   : self.work_time['Picking'],
            'time_worked_packing'   : self.work_time['Packing'],
            'time_idled_storage'    : self.idle_time['Storage'],
            'time_idled_picking'    : self.idle_time['Picking'],
            'time_idled_packing'    : self.idle_time['Packing'],
        }