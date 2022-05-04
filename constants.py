"""
Storing Constants
"""

# P1 tshirts
P1_PROFIT         = 4
P1_PENALTY        = 1
P1_HOLDING_COST   = 0.1
P1_WEIGHT         = 0.5
P1_INIT_INVENTORY = 10000

# P2 Hoodie       
P2_PROFIT         = 10
P2_PENALTY        = 6
P2_HOLDING_COST   = 0.3
P2_WEIGHT         = 1
P2_INIT_INVENTORY = 5000

# P3 Sweatpants   
P3_PROFIT         = 10
P3_PENALTY        = 6
P3_HOLDING_COST   = 0.3
P3_WEIGHT         = 1
P3_INIT_INVENTORY = 5000

# P4 Sneaker      
P4_PROFIT         = 20
P4_PENALTY        = 10
P4_HOLDING_COST   = 0.6
P4_WEIGHT         = 1.5
P4_INIT_INVENTORY = 3333

# Workes
LABOR_RATE       = 22.5

# Fullfillment Center:

Fullfillment = 5000000 

# Stage 1 Inbound Receiving
DELIVERY_COST           = 1000
DELIVERY_COST_WEEKLY    = 50000       #2600000
DELIVERY_COST_DAILY     = 10000        #3600000
# DELIVERY_PENALTY_WEEKLY = 50000
# DELIVERY_PENALTY_DAILY  = 10000
PARKING_LIMIT           = 50000

# Stage 2 Stowing

STOWERLIMIT                 = 12
STOWER_PICKUP_TIME          = 120
STOWER_TO_STORAGE_TIME      = 120
STOWER_TRAVEL_TIME          = 60
STOWER_STOW_TIME_PER_UNIT   = 10

# Stage 3 Picking

PICKER_TO_STORAGE_TIME  = 120
PICKER_TRAVEL_TIME      = 60
PICKER_TIME_PER_UNIT    = 10
PICKER_TO_PACKING_TIME  = 30

# Stage 4 Packing

PACKER_BASE_TIME        = 30
PACKER_TIME_PER_ITEM    = 10

PACK_STATION_COST = 50000
FXD_FACILITY      = 5000000
ORDER_EXPIRATION = 72 * 60 * 60 # 72 hours -> Seconds

# Stage 5 SHIP

# Order Distributions
# (0:4) 0 
# (4:8) 1 
# (8:16) 2
# (16:24) 3

P_UPPER_LIM = {
    "P1": 9,
    "P2": 7,
    "P3": 7,
    "P4": 6
}

DISTRIBUTION = {
        "SUN_0" : {
            "order_lambda": 0.014950108,
            "order_k": 0.825400379,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "SUN_1" : {
            "order_lambda": 0.009354449,
            "order_k": 0.813506147,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "SUN_2" : {
            "order_lambda": 0.046020589,
            "order_k": 1.043594378,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "SUN_3" : {
            "order_lambda": 0.054902163,
            "order_k": 1.065202304,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "MON_0" : {
            "order_lambda": 0.007676763,
            "order_k": 0.806597743,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "MON_1" : {
            "order_lambda": 0.004650986,
            "order_k": 0.794128153,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "MON_2" : {
            "order_lambda": 0.023369416,
            "order_k": 1.016883001,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
         "MON_3" : {
            "order_lambda": 0.027818894,
            "order_k": 1.025788681,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "TUE_0" : {
            "order_lambda": 0.005457647,
            "order_k": 0.851159743,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.279811678
        },

        "TUE_1" : {
            "order_lambda": 0.003405856,
            "order_k": 0.793215822,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "TUE_2" : {
            "order_lambda": 0.01759182,
            "order_k": 1.00550951,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "TUE_3" : {
            "order_lambda": 0.021136697,
            "order_k": 1.016530023,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "WED_0" : {
            "order_lambda": 0.012979123,
            "order_k": 0.83198385,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "WED_1" : {
            "order_lambda": 0.008428623,
            "order_k": 0.799600429,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "WED_2" : {
            "order_lambda": 0.040469894,
            "order_k": 1.038453896,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "WED_3" : {
            "order_lambda": 0.048182209,
            "order_k": 1.055312734,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "THU_0" : {
            "order_lambda": 0.007519394,
            "order_k": 0.832069084,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "THU_1" : {
            "order_lambda": 0.004605762,
            "order_k": 0.802866434,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "THU_2" : {
            "order_lambda": 0.023427775,
            "order_k": 1.012079446,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
         "THU_3" : {
            "order_lambda": 0.028139021,
            "order_k": 1.021664922,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "FRI_0" : {
            "order_lambda": 0.01673338,
            "order_k": 0.830819899,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "FRI_1" : {
            "order_lambda": 0.010584041,
            "order_k": 0.817082575,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "FRI_2" : {
            "order_lambda": 0.052033437,
            "order_k": 1.052963834,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "FRI_3" : {
            "order_lambda": 0.06192768,
            "order_k": 1.070590736,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "SAT_0" : {
            "order_lambda": 0.019186519,
            "order_k": 0.809705627,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "SAT_1" : {
            "order_lambda": 0.011782825,
            "order_k": 0.803073579,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },
        "SAT_2" : {
            "order_lambda": 0.05905927,
            "order_k": 1.03393815,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        },

        "SAT_3" : {
            "order_lambda": 0.070010711,
            "order_k": 1.053554645,
            "P1_mean": 1.116795576,
            "P1_std": 0.993274658,
            "P2_mean": 0.558259652,
            "P2_std": 0.724923748,
            "P3_mean": 0.56008554,
            "P3_std": 0.725549543,
            "P4_mean": 0.279811678,
            "P4_std": 0.520832732
        }
    }