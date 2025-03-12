
import sys
from opentrons import protocol_api
import numpy as np


def generate_script(iter_n, volume):
    array_str = np.array2string(volume, separator = ', '.replace('\n', ''))
    code_template = f'''
from opentrons import protocol_api
import numpy as np

#creates array with volumes, in future this will come from the optimisation program
#volume = np.array([[20.0, 30.0, 40.0] for i in range(14)])

requirements = {{"robotType": "OT-2", "apiLevel": "2.16"}}
iter_n = {iter_n}
volume = np.array({array_str})

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
                left_pipette.transfer(amt[j], reservoir[f'A{{i+1}}'], row[current_row][current_col], new_tip = 'never')
            #if it is on the last liquid, it mixes the well
            else:
                left_pipette.pick_up_tip()
                left_pipette.transfer(amt[j], reservoir[f'A{{i+1}}'], row[current_row][current_col], mix_after = (2,20), new_tip = 'never')
                left_pipette.drop_tip()
        if i != num_liquids - 1:
            left_pipette.drop_tip()

'''
    with open('generated_script.py', 'w') as file:
        file.write(code_template)

iter_n = int(open('./data/iter_count.txt').read())
volume = np.load('./data/values.npy')

generate_script(iter_n, volume)




