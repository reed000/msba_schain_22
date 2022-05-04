
#⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠆⠜⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⠿⠿⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿
#⣿⣿⡏⠁⠀⠀⠀⠀⠀⣀⣠⣤⣤⣶⣶⣶⣶⣶⣦⣤⡄⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿
#⣿⣿⣷⣄⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⡧⠇⢀⣤⣶⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣾⣮⣭⣿⡻⣽⣒⠀⣤⣜⣭⠐⢐⣒⠢⢰⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⣏⣿⣿⣿⣿⣿⣿⡟⣾⣿⠂⢈⢿⣷⣞⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣷⣶⣾⡿⠿⣿⠗⠈⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⠋⠉⠑⠀⠀⢘⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⣿⡿⠟⢹⣿⣿⡇⢀⣶⣶⠴⠶⠀⠀⢽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⣿⣿⣿⡿⠀⠀⢸⣿⣿⠀⠀⠣⠀⠀⠀⠀⠀⡟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
#⣿⣿⣿⡿⠟⠋⠀⠀⠀⠀⠹⣿⣧⣀⠀⠀⠀⠀⡀⣴⠁⢘⡙⢿⣿⣿⣿⣿⣿⣿⣿⣿
#⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⠗⠂⠄⠀⣴⡟⠀⠀⡃⠀⠉⠉⠟⡿⣿⣿⣿⣿
#⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⠾⠛⠂⢹⠀⠀⠀⢡⠀⠀⠀⠀⠀⠙⠛⠿⢿
                GOT EM

# # # # # # # # # # # # # # # # # #
# Notional data structures below  #
# # # # # # # # # # # # # # # # # #

    # eventID : {busProc name,  function}
#    event_dictionary = {
#        'DeliveryIn' : ('parking','EventDelivery'))
#    }

    # tuple: (TIMESTAMP, eventID)
#    self.event_queue = [
#        (800  , DockDelivery),
#        (1600 , ReceiveOrders),
#        (3200 , WorkerStorage_2347_0_TransitStorage),
#        (3210 , WorkerStorage_2347_0_StowItem),
#        (3330 , WorkerStorage_2347_0_TransitParking),
#    ]


Update:
- Orders needed to be generated at clock+interval - no stack overflow!
- Added Order file to options
- Added a function to generate midnightstrikes times in kernel
- Added profs folder for snakeviz
Questions:
- Do we need to poke stowers at end of getDelivery to Parking?
- Do we need a Close Order event to check time or process Revenue?


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



