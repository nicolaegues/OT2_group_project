import numpy as np

"""
- need to think about whether we want a deeper wellplate for better mixing of the colors. I have a picture of the alterantive - only issue is that it is squared. 
- how do we do it such that for red, for example, it doesn't go back to the reservoir every time for each well but gathers multiple well volumes at once?
- user input options for labware and positioning (in main). 
- comment all codes properly

"""


def generate_script(
    filepath, iter_count, wells_per_iteration, liquid_volumes, well_locs
):
    """
    Generates an opentrons script for one iteration

    params:
        iter_count (int):
            the current iteration number the program is on, used for calculating which wells to pippette into
        volume (ndarray):
            array containing volume of each liquid in uL.
            row size = iteration count
            column size = number of liquids
        well_loc (int):
            Position of the well plate in the OT2. Default: 5 (the middle of the robot).
        total_volume (float):
            Total volume to be pipetted in each well. Default: 150uL.
    """

    # This is used so that it works with .npy files, might need to be changed if we call this function from wellplate_classes
    array_str = np.array2string(liquid_volumes, separator=", ".replace("\n", ""))
    code_template = f"""
from opentrons import protocol_api
import numpy as np

requirements = {{"robotType": "OT-2", "apiLevel": "2.16"}}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = {iter_count}
    wells_per_iteration = {wells_per_iteration}
    volumes = np.array({array_str})

    #location selected by user when wellplate class created
    well_locs = {well_locs}

    #concentrations used must come in a num of wells x num of liquids size array
    iter_size = volumes.shape[0]
    num_liquids = volumes.shape[1]

    if 1 not in protocol.deck or protocol.deck[1] is None:
        #loading the tips, reservoir and well plate into the program
        tips = protocol.load_labware("opentrons_96_tiprack_1000ul", 1)
        reservoir = protocol.load_labware("nest_12_reservoir_15ml", 2)
        
        plates = {{}}
        for idx, loc in enumerate(well_locs):
            plates[f"plate_{{idx+1}}"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", loc)
        
        left_pipette = protocol.load_instrument("p1000_single_gen2", "right", tip_racks=[tips])
    
    else:
        #retrieve existing labware
        tips = protocol.deck[1]
        reservoir = protocol.deck[2]
        plates = {{f"plate_{{idx+1}}": protocol.deck[loc] for idx, loc in enumerate(well_locs)}}
        left_pipette = protocol.loaded_instruments["right"]

    start_index = (iteration_count * wells_per_iteration) 
    current_plate_idx = start_index // 96
    plate = plates[f"plate_{{current_plate_idx+1}}"]  # Get the correct plate
    print(f"plate_{{current_plate_idx+1}}")

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
            liquid_source = reservoir[f'A{{liquid+1}}']

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
                

"""
    with open(filepath, "w") as file:
        file.write(code_template)
