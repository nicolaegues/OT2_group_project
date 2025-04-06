The `tests` folder contains various scripts that allow the user to test the main functionalities of the optobot package before connecting to the robot.
Following things can be tested beforehand: 

1) Testing of the optimisation process
    - Since no actual liquid-mixing and subsequent measuring/colour recording is done (in the colour-mixing experiment case), 
    this is tested by simply optimizing the inputs liquid volumes directly (instead of any intermediate measurements). This is the default setup of the `test_main.py` script, and can be run at the command line via folling (from the root directory): 

    ```
    $ python -m tests.test_main
    ```

    By default, the resulting data from these experiments is stored in the folder `test_results_data` .

2) Testing of the colour extraction process
    - To test the well detection methods, the user should open `test_main.py` and change the following: 
        - the `measurement_function` argument of the `OptimisationLoop` class in `test_main.py` needs to be changed from `test_measurement_function` (the default) to `measurement_function`. This way `test_colors.py` is called as the measurement function. This script skips the usual picture-taking step and uses the image found in the folder `test_data` as the "captured" image directly. One iteration should be sufficient to test the detection methods work. 

    - After this change, run it with the same command as in (1). 


3) Simulation of an example generated OT2 run script

    The file `simulate_ot2_script.py` is an example of a generated opentrons run script. The outputs of the robot can be simulated by running the follwing from the root directory: 

    ```
    $ opentrons_simulate tests/simulate_ot2_script.py
    ```