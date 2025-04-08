
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iteration_count = 3
    wells_per_iteration = 48
    volumes = np.array([[27.23891782, 20.        ,  4.50009344,  8.26098874],
 [27.23713118, 20.        ,  4.50063702,  8.2622318 ],
 [27.23766534, 20.        ,  4.50112681,  8.26120785],
 [27.23767696, 20.        ,  4.50014446,  8.26217858],
 [27.23746864, 20.        ,  4.49965453,  8.26287683],
 [27.23551004, 20.        ,  4.49943296,  8.265057  ],
 [27.2416505 , 20.        ,  4.50038264,  8.25796686],
 [27.23517149, 20.        ,  4.49747775,  8.26735076],
 [27.23802524, 20.        ,  4.50415787,  8.25781689],
 [27.24246303, 20.        ,  4.50095222,  8.25658475],
 [27.23765994, 20.        ,  4.5002025 ,  8.26213756],
 [27.23842388, 20.        ,  4.50018279,  8.26139333],
 [27.23251264, 20.        ,  4.50164718,  8.26584018],
 [27.23743562, 20.        ,  4.49758979,  8.26497459],
 [27.2462622 , 20.        ,  4.50137867,  8.25235914],
 [27.23480088, 20.        ,  4.49918197,  8.26601714],
 [27.23754589, 20.        ,  4.50024693,  8.26220718],
 [27.23940435, 20.        ,  4.50172066,  8.25887499],
 [27.24580103, 20.        ,  4.4976753 ,  8.25652367],
 [27.23881871, 20.        ,  4.5007397 ,  8.26044159],
 [27.23755032, 20.        ,  4.5001086 ,  8.26234108],
 [27.23766944, 20.        ,  4.49954772,  8.26278284],
 [27.23612058, 20.        ,  4.49897507,  8.26490435],
 [27.23778278, 20.        ,  4.50004991,  8.26216731],
 [27.2373874 , 20.        ,  4.49987449,  8.26273811],
 [27.24591836, 20.        ,  4.50168627,  8.25239536],
 [27.2372571 , 20.        ,  4.50012275,  8.26262015],
 [27.23176706, 20.        ,  4.49908843,  8.26914451],
 [27.23826498, 20.        ,  4.50001514,  8.26171988],
 [27.23668781, 20.        ,  4.50018492,  8.26312727],
 [27.23829135, 20.        ,  4.50143282,  8.26027583],
 [27.23877998, 20.        ,  4.50057482,  8.2606452 ],
 [27.23909461, 20.        ,  4.50064509,  8.2602603 ],
 [27.23807015, 20.        ,  4.5007983 ,  8.26113155],
 [27.23747184, 20.        ,  4.50039201,  8.26213615],
 [27.23787382, 20.        ,  4.49972276,  8.26240342],
 [27.23718385, 20.        ,  4.49803713,  8.26477902],
 [27.23830242, 20.        ,  4.50036491,  8.26133266],
 [27.23373125, 20.        ,  4.49892881,  8.26733994],
 [27.23607066, 20.        ,  4.50306631,  8.26086304],
 [27.2372364 , 20.        ,  4.50035052,  8.26241308],
 [27.2387174 , 20.        ,  4.49872392,  8.26255868],
 [27.23326923, 20.        ,  4.49911002,  8.26762075],
 [27.23017435, 20.        ,  4.49904265,  8.270783  ],
 [27.23737318, 20.        ,  4.50042772,  8.2621991 ],
 [27.23954633, 20.        ,  4.50043868,  8.260015  ],
 [27.23683363, 20.        ,  4.50162695,  8.26153942],
 [27.23825497, 20.        ,  4.50136116,  8.26038387]])

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
                

