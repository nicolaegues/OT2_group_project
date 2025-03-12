
from opentrons import protocol_api
import numpy as np

#creates array with volumes, in future this will come from the optimisation program
#volume = np.array([[20.0, 30.0, 40.0] for i in range(14)])

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}
iter_n = 7
volume = np.array([[32.27928945, 15.31411936, 14.32297021],
 [29.91591755, 18.38420229, 11.75526386],
 [28.55523819, 16.9928687 , 12.32607531],
 [31.02684205, 18.89839121, 14.90423154],
 [28.47081224, 18.91068978, 12.45424157],
 [27.34710928, 19.11241488, 17.6542183 ],
 [30.35384543, 17.94747343, 11.28707793],
 [28.23056294, 17.16285103, 12.93696837],
 [31.79585052, 19.00137705, 12.91314399],
 [30.36779772, 20.89957326, 12.27255246],
 [30.74312183, 20.0929996 , 14.72100424],
 [30.61725902, 16.55086064, 13.17730137]])

#need to have some way for the user to select labware type and number
well_loc = 5

#concentrations used must come in a num of wells x num of liquids size array
iter_size = volume.shape[0]
num_liquids = volume.shape[1]

#calculate which row and col to start on depending on iteration size and number
#assuming 96 wells, making 12 a variable could change this
start_row = (iter_size * iter_n) // 12
start_col = (iter_size * iter_n) % 12


def run(protocol: protocol_api.ProtocolContext):

    #loading the tips, reservoir and well plate into the program
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", 2)
    #well plate in the middle for optimal camera placement, in future let user select
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat", well_loc)
    left_pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])
    row = plate.rows()

    #Adds water so that it fills up to the same volume each time
    volume = np.load('./data/values.npy')
    buffer = 150 - np.sum(volume, axis = 1)
    #water will now be the first liquid to be added
    volume = np.hstack([buffer.reshape(-1,1), volume])

    for i in range(num_liquids+1):
        if i != num_liquids - 1:
            left_pipette.pick_up_tip()
        amt = volume[:, i]
        for j in range(iter_size):
            #calculates current column and row to pipette into
            current_col = (start_col + j) % 12
            current_row = start_row + (start_col + j) // 12

            #transfers X amount of liquid i into the well
            if i != num_liquids - 1:
                left_pipette.transfer(amt[j], reservoir[f'A{i+1}'], row[current_row][current_col], new_tip = 'never')
            #if it is on the last liquid, it mixes the well
            else:
                left_pipette.pick_up_tip()
                left_pipette.transfer(amt[j], reservoir[f'A{i+1}'], row[current_row][current_col], mix_after = (2,20), new_tip = 'never')
                left_pipette.drop_tip()
        if i != num_liquids - 1:
            left_pipette.drop_tip()

