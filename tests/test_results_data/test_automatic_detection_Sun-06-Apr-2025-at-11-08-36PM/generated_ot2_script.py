
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 1
    wells_per_iteration = 12
    volumes = np.array([[33.9897822 , 12.73147275, 28.44330007, 14.83544497],
 [35.66555807, 24.96774231, 11.40311966, 17.96357996],
 [42.80072919, 28.98011381,  7.34069657, 10.87846044],
 [53.64711456, 15.38473461,  9.93458782, 11.03356301],
 [77.21880928,  7.66896705,  2.54800904,  2.56421463],
 [49.58841405, 10.79565771, 21.41261024,  8.20331799],
 [37.25008649, 17.7993591 , 15.16407131, 19.7864831 ],
 [54.96767979, 20.85113135,  1.49608264, 12.68510622],
 [49.00620356, 18.53846862, 14.05310594,  8.40222189],
 [62.0540506 , 16.48788181,  5.50968471,  5.94838288],
 [50.96688302,  8.44602992, 23.35145556,  7.2356315 ],
 [54.85460386, 15.82054246, 13.29344515,  6.03140853]])

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
                

