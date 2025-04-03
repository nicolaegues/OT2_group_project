
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 3
    wells_per_iteration = 12
    volumes = np.array([[35.72546745, 18.26097629, 21.03816139, 14.97539487],
 [43.62463269, 18.67985558, 13.83991534, 13.85559639],
 [42.53708583, 15.35115282, 20.34677786, 11.76498349],
 [38.55399482, 21.85056911, 19.03472159, 10.56071448],
 [35.02066286, 21.45450213, 20.9066929 , 12.61814211],
 [33.13258503, 20.81110734, 16.90418006, 19.15212756],
 [38.47975209, 15.38159209, 19.28526611, 16.85338972],
 [36.31340274, 18.87122987, 19.87435375, 14.94101364],
 [35.30061784, 19.79972465, 20.92670936, 13.97294815],
 [30.1841676 , 18.81670422, 20.07683576, 20.92229241],
 [38.39017898, 17.51542156, 20.5741931 , 13.52020636],
 [36.05980426, 15.47631157, 23.19325693, 15.27062724]])

    #location selected by user when wellplate class created
    well_locs = [5, 8]

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

            if liquid != num_liquids - 1:
                left_pipette.transfer(liquid_volume, liquid_source, target_well, new_tip = "never")
            else: 
                left_pipette.transfer(liquid_volume, liquid_source, target_well, new_tip = "never", mix_after=(3, 20 ))

        #bin the tip
        left_pipette.drop_tip()

    # for well in target_wells:
    #     left_pipette.pick_up_tip()
    #     left_pipette.mix(3, 20, well)
    #     left_pipette.drop_tip()
                

