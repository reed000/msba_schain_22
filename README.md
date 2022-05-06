## Supply Chain Analytics Project
M4 - Supply Chain - Final Project
May 2022
Ayush Agrawal
Reed Abraham
Ferenc Feher
Harry Xu

## Run Steps

1. Ensure Constants.cs has Warehouse defaults set accordingly
2. Decision Factors are set in driver.py 
    > See Below for instructions **Simulation Inputs**
3. Ensure python environment is setup with packages listed in env.yaml
4. Run via cmd:
    > python driver.py

## Simulation Inputs

- SET_RUNTIME: This is the time in seconds for the whole year
- SET SHIFTS
    - This is a shift example. It records 21 shift times across the week
    - This format example is set for Storage, Picking, Packing workers
```
    stowing_shift = {
        "SUN": [50, 50, 50],
        "MON": [50, 50, 50],
        "TUE": [50, 50, 50],
        "WED": [50, 50, 50],
        "THU": [50, 50, 50],
        "FRI": [50, 50, 50],
        "SAT": [50, 50, 50]
        }
```
- SET PROGRAM OPTIONS
```
    'DELIVERY_SCHEDULE'    : ['DAILY', 'WEEKLY']
    'STORAGE_MECHANIC'     : ['DESIGNATED', 'RANDOM'] 
    'STORAGE_WORKERS'      :  # of workers via worker shifts
    'PICKING_MECHANIC'     : ['DESIGNATED', 'RANDOM']
    'PICKING_WORKERS'      :  # of workers via worker shifts
    'PACKING_WORKERS'      :  # of workers via worker shifts
    'PACKING_STATIONS'     :  # of total packing stations
```
- SET DEBUG VARIABLES
```
    'KENNY_LOGGINS'        :  False To disable Logging output - significant extra runtime
    'SAVE_DATA'            :  True to save output csv in order to process KPI over time
    'SAVE_ORDERS'          :  True to save order list 
    'FINAL_ECHO'           :  True to print KPI output
    'ORDER_TEST'           :  False to avoid using order test sample
    #'ORDER_FILE'           : 'strategies/final-project-2022m4_orders.csv' Set when order file is used
```

## Simulation Outputs

- The following output will be seen in the terminal.
- This progress displays the simulation over the set time and will update as it ends the simulation 
100%|##############################################################################################################################################################| 1728000.0/1728000 [02:55<00:00, 9860.85it/s]
- After the progress the KPIs are printed out as a result. This includes a summary of the costs
```
Runtime:  31536000
Delivery Option:  DAILY
Storage:  DESIGNATED
31536000.60000001it [04:39, 112943.09it/s]                                                                                     
                   Revenue  :  20841972
        (Delivery Expense)  :  10000
      {Lost Sales Penalty)  :  313907
           (Labor Expense)  :  7688439
   (Facilities Fixed Cost)  :  5000000
 (Packing Station Expense)  :  150000
  (Inventory Holding Cost)  :  0
------------TOTAL PROFIT =  :  7679626
--------------------------  :  --------------------------
    Total Parking Weight =  :  194.00 %
-----Utilization Storage =  :  64.41 %
-----Utilization Picking =  :  63.30 %
-----Utilization Packing =  :  54.67 %
```
- output/simout.csv - This will be a file contatining a time analysis of all KPIs and can be read using the post-proc


# # # # # # # # # # # # # # # # # #
# Notional data structures below  #
# # # # # # # # # # # # # # # # # #

This is the event dictionary that maps a specific event name to its event function
    # eventID : {busProc name,  function}
#    event_dictionary = {
#        'DeliveryIn' : ('parking','EventDelivery'))
#    }

This is a MinHeap Implementation of the event queue.
It stores the smallest next timestampl in the front of the list for a O(1) runtime.
    # tuple: (TIMESTAMP, eventID)
#    self.event_queue = [
#        (800  , DockDelivery),
#        (1600 , ReceiveOrders),
#        (3200 , WorkerStorage_2347_0_TransitStorage),
#        (3210 , WorkerStorage_2347_0_StowItem),
#        (3330 , WorkerStorage_2347_0_TransitParking),
#    ]

## Simulation Architecture
Executors
- driver.py : Main class to set options and run simulation
- kernel.py : Maintains timeline instance for one specific simulation run

data
- data_store.py : Class to store KPIs and warehouse states over time for the kernel

strategies
- This stores the daily, weekly, adn order strategy files

Business Processses
- ordering.py : Manages order distribution store orer info / load order times to event queue
- packing.py : Manages Packing station queue and process of orders to shipment
- pooling.py : Manages Accepting deliveries and processing to parking 
- storing.py : Manages Storing new deliveries from parking to inventory
- picking.py : Manages Picking inventory

Workers:
- worker : generic worker class to manage idle state, start, end, labor rate
- stowage : Manages storing inventory to parking and reading delivery queues with specific strategy
- picker : manage travel inventory to with specific strategy
- packer : Manages accepting station queues to delivery

Utilities
- order.py : Manage each order data and helper funcitons for checking expire and total
- station.py - Manage station queue

Misc folders to ignore
- Research Notebooks
- logs/
- profs/
- strategies/
- legacy

## Core Functions
process_delivery
- DATA
    - Parking Inventory
    - total freight cost
- Steps
    - check weight on each shipment
        if parking + new_shipment < 50,000, ok  
        if > 50,000, take max constant fraction rounded down, add pentalty cost
    - update Inventory
    - add cost
- Future Steps
    - process_parking_inventory (move to storage)

process_parking_inventory  (either ordered stowing or random stowing)
- DATA  
    - Parking Inventory 
    - Storage Inventory
    - Timer
- Steps
    - check which Parking Inventory has highest weight 
    - Parking Inventory update 
    - Storage Inventory update 
    - Record total time used stowing

process_picking (either picking from ordered storage or random storage policy)
- DATA  
    - Order Items
    - Storage Inventory
    - Lost Sales
    - Timer
- Steps
    - check if order can be fufilled
        - if not, record Lost Sales
    - Storage Inventory update
    - Record total time used picking
- Future Steps
    - process_packing

process_packing 
- DATA 
    - Order Items
    - Packing Stations Orders
    - Timer
- Steps
    - Send to the least # of orders in the station
    - Update Packing Station
    - Record total time used packing
- Future Steps
    - process_shipping


process_shipping
- DATA
    - Order Items
- Steps
    - Record revenue
