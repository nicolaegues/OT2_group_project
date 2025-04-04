
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 15
    wells_per_iteration = 12
    volumes = np.array([[45.14562631, 19.4343801 , 16.33371344,  9.08628015],
 [46.85562636, 19.07446532, 15.81107952,  8.2588288 ],
 [44.40531543, 20.16005787, 17.85321768,  7.58140903],
 [47.17884112, 18.60026518, 15.85309196,  8.36780174],
 [46.91512231, 18.17611884, 15.92923689,  8.97952196],
 [47.21762066, 19.70038006, 15.23235785,  7.84964143],
 [46.93755945, 17.96363481, 15.99818913,  9.1006166 ],
 [47.69613052, 18.09784267, 15.46623206,  8.73979474],
 [46.07628248, 15.39715424, 16.26490801, 12.26165528],
 [48.09137308, 19.94205215, 14.34315027,  7.62342449],
 [47.21119321, 20.57132923, 15.5705304 ,  6.64694716],
 [50.37216066, 19.29792684, 12.94874872,  7.38116378]])

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

            #if liquid != num_liquids - 1:
            left_pipette.transfer(liquid_volume, liquid_source, target_well, new_tip = "never" )

        #bin the tip
        left_pipette.drop_tip()

    for well in target_wells:
        left_pipette.pick_up_tip()
        left_pipette.mix(3, 20, well)
        left_pipette.drop_tip()
                

