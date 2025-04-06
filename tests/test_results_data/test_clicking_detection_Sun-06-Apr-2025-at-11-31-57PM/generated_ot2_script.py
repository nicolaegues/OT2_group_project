
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 1
    wells_per_iteration = 12
    volumes = np.array([[57.63360832, 11.21952245, 13.78063668,  7.36623255],
 [67.28708333,  7.5282241 , 11.1329755 ,  4.05171707],
 [48.59848642,  8.91925809, 16.0801653 , 16.4020902 ],
 [50.78232229,  7.98213621, 20.36426302, 10.87127848],
 [30.86899111, 17.40710231, 20.07650565, 21.64740092],
 [60.23765701, 11.94706197, 12.36944608,  5.44583495],
 [26.36518024, 22.59610623, 24.06552876, 16.97318477],
 [43.98610021, 25.12784236,  4.89044047, 15.99561697],
 [30.97509839, 21.86352065, 14.73255974, 22.42882122],
 [49.01581691, 15.70278363, 16.97291048,  8.30848898],
 [45.20447576,  9.70531778, 18.24683901, 16.84336745],
 [34.99921291, 13.49259095, 25.52613645, 15.98205969]])

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
                

