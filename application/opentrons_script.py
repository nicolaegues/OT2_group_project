
import sys
from opentrons import protocol_api
import numpy as np


#creates array with volumes, in future this will come from the optimisation program
#volume = np.array([[20.0, 30.0, 40.0] for i in range(14)])
iter_n = int(open('iter_count.txt').read())
volume = np.load('values.npy')

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

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
    for i in range(num_liquids):
        amt = volume[:, i]
        for j in range(iter_size):
            #calculates current column and row to pipette into
            current_col = start_col + j % 12
            current_row = start_row + (start_col + j) // 12

            #transfers X amount of liquid i into the well
            if i != num_liquids - 1:
                left_pipette.transfer(amt[j], reservoir[f'A{i+1}'], row[current_row][current_col])
            #if it is on the last liquid, it mixes the well
            else:
                left_pipette.transfer(amt[j], reservoir[f'A{i+1}'], row[current_row][current_col], mix_after = (3,20))







