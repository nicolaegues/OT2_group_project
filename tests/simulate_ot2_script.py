"""
Simulate from commmand line by running: 

opentrons_simulate tests/simulate_ot2_script.py

"""


from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 7
    wells_per_iteration = 5
    volumes = np.array([[42.06915343, 13.78170516, 19.8832555 , 14.26588591],
 [42.38639251, 12.71361819, 19.40800151, 15.4919878 ],
 [43.02024142, 13.79028736, 18.16751135, 15.02195987],
 [43.1372641 , 14.09678473, 17.9605694 , 14.80538178],
 [39.87355839, 14.85761571, 21.02817419, 14.24065171],
 [39.11736333, 14.91140276, 20.03915163, 15.93208228],
 [41.82741893, 13.15822384, 16.97759113, 18.0367661 ],
 [41.91896306, 12.86883258, 20.48199618, 14.73020818],
 [36.30103228, 13.51878303, 20.67507416, 19.50511053],
 [39.60528924, 13.6106463 , 20.65727101, 16.12679345],
 [39.70719977, 13.55525648, 20.91061567, 15.82692807],
 [38.27164116, 14.86675287, 21.06043097, 15.801175  ]])

    #location selected by user when wellplate class created
    well_locs = [8, 5]

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
                

