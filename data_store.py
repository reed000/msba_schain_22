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
                    'P4':0}}

        self.costs = {
                'labor': 0,
                'delivery': 0,
                'lost_sales': 0,
                'facilities_fxd': 0,
                'packing_stn': 0,
                'inventory_hldg': 0
            }
        self.revenue = 0
        self.product = ['P1', 'P2', 'P3', 'P4']
        self.product_names = ['Tshirt', 'Hoodie', 'Sweatpants', 'Sneakers']
    
    def get_KPIs(self):
        kpi = {
            "                   Revenue": self.revenue,
            "        (Delivery Expense)": self.costs['delivery'],
            "      {Lost Sales Penalty)": self.costs['lost_sales'],
            "           (Labor Expense)": self.costs['labor'],
            "   (Facilities Fixed Cost)": self.costs['facilities_fxd'],
            " (Packing Station Expense)": self.costs['packing_stn'],
            "  (Inventory Holding Cost)": self.costs['inventory_hldg'],
            "------------TOTAL PROFIT =": self.revenue - self.get_total_cost()
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
            if prod = 'P1':
                self.costs['inventory_hldg'] += inventory[prod] * cs.P1_HOLDING_COST
            elif prod = 'P2':
                self.costs['inventory_hldg'] += inventory[prod] * cs.P2_HOLDING_COST
            elif prod = 'P3':
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

        max_weight_key = \
            [key for key, value in weight_now.items() if value == max(weight_now.values())]
        
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
