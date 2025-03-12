
from opentrons import protocol_api
import numpy as np

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):

    iter_count = 7
    volume = np.array([[29.76736542, 25.37957633, 15.72223769],
 [29.99290995, 24.25973718, 15.23811039],
 [29.81482166, 24.10469473, 16.41188552],
 [29.27962927, 22.96150055, 14.86124743],
 [31.41511171, 25.12932117, 14.77954048],
 [31.72858105, 24.90261097, 12.61336342],
 [32.54986668, 21.58628161, 14.32830123],
 [29.59585739, 24.50951308, 14.66931344],
 [31.26780467, 24.18569784, 15.99460891],
 [32.71292545, 26.12484091, 14.55332488],
 [29.79981649, 22.42784613, 14.96377826],
 [30.89079421, 22.85087132, 20.18083191]])

    total_volume = 150.0

    #location selected by user when wellplate class created
    well_loc = 5

    #concentrations used must come in a num of wells x num of liquids size array
    iter_size = volume.shape[0]
    num_liquids = volume.shape[1]

    #calculate which row and col to start on depending on iteration size and number
    #assuming 96 wells, making 12 a variable could change this
    start_row = (iter_size * iter_count) // 12
    start_col = (iter_size * iter_count) % 12

    #loading the tips, reservoir and well plate into the program
    tips = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    reservoir = protocol.load_labware("nest_12_reservoir_15ml", 2)
    #well plate in the middle for optimal camera placement, in future let user select
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat", well_loc)
    left_pipette = protocol.load_instrument("p300_single_gen2", "right", tip_racks=[tips])
    row = plate.rows()

    #Adds water so that it fills up to the same volume each time
    buffer = total_volume - np.sum(volume, axis = 1)
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

