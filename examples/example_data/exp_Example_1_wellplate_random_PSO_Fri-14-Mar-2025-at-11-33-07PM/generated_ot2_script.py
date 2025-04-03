
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 7
    wells_per_iteration = 12
    volumes = np.array([[29.39314544, 25.8534327 , 19.35730806, 15.3961138 ],
 [24.88848336, 19.60751669, 23.30756416, 22.19643578],
 [22.48063785, 21.61181264, 21.60203444, 24.30551507],
 [15.78427279, 24.2487547 , 25.0987759 , 24.86819661],
 [ 9.64378549, 25.69433812, 26.43557973, 28.22629666],
 [15.81801603, 24.80372087, 24.26342162, 25.11484148],
 [13.83817589, 23.94502306, 26.32565766, 25.89114339],
 [13.83098566, 23.81261775, 26.51038354, 25.84601305],
 [15.29256137, 23.49290651, 24.249587  , 26.96494512],
 [11.70898967, 25.43671166, 25.33245607, 27.52184261],
 [12.65764774, 25.2335975 , 25.79320775, 26.315547  ],
 [19.48036518, 21.81066722, 22.73272235, 25.97624525]])

    #location selected by user when wellplate class created
    well_locs = [5]

    #concentrations used must come in a num of wells x num of liquids size array
    iter_size = volumes.shape[0]
    num_liquids = volumes.shape[1]

    if 1 not in protocol.deck or protocol.deck[1] is None:
        #loading the tips, reservoir and well plate into the program
        tips = protocol.load_labware("opentrons_96_tiprack_1000ul", 1)
        reservoir = protocol.load_labware("nest_12_reservoir_15ml", 2)
        
        plates = {}
        for idx, loc in enumerate(well_locs):
            plates[f"plate_{idx+1}"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", loc)
        
        left_pipette = protocol.load_instrument("p1000_single_gen2", "right", tip_racks=[tips])
    
    else:
        #retrieve existing labware
        tips = protocol.deck[1]
        reservoir = protocol.deck[2]
        plates = {f"plate_{idx+1}": protocol.deck[loc] for idx, loc in enumerate(well_locs)}
        left_pipette = protocol.loaded_instruments["right"]

    start_index = (iteration_count * wells_per_iteration) 
    current_plate_idx = start_index // 96
    plate = plates[f"plate_{current_plate_idx+1}"]  # Get the correct plate
    print(f"plate_{current_plate_idx+1}")

    well_count = iteration_count - current_plate_idx*8

    for liquid in range(num_liquids): 

        left_pipette.pick_up_tip() #one tip for each dye-distribution into all the wells. then a new tip for another color distribution into all the wells. 

        target_wells = []
        for well, volume_set in enumerate(volumes):

            #multiplying by factor of 8: this way we first fill A1 - A12, then B1-B12. instead of A1-H1, then A2-H2.... 
            well_index = well * 8 + well_count

            target_well = plate.wells()[well_index] 
            target_wells.append(target_well)

            
            liquid_volume = volume_set[liquid]
            liquid_source = reservoir[f'A{liquid+1}']

            #if liquid != num_liquids - 1:
            left_pipette.transfer(liquid_volume, liquid_source, target_well, new_tip = "never" )

        #bin the tip
        left_pipette.drop_tip()

    for well in target_wells:
        left_pipette.pick_up_tip()
        left_pipette.mix(3, 20, well)
        left_pipette.drop_tip()
                

