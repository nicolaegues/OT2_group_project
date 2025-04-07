# Tests Overview

<p align="justify">
The <code>tests</code> folder contains various scripts that allow the user to 
test the main functionalities of the optobot package before connecting to the 
robot.
<!--><!-->
The following things can be tested beforehand.
</p>

## 1. Testing of the Optimisation Process
<p align="justify">
Since no actual liquid-mixing and subsequent measuring/colour recording 
is done (in the colour-mixing experiment case), this is tested by simply 
optimizing the inputs liquid volumes directly (instead of any intermediate 
measurements).
<!--><!-->
This is the default setup of the <code>test_main.py</code> script, and can be 
run at the command line using the following command from the root directory.
</p>

```
$ python -m tests.test_main
```

+ By default, the resulting data from these experiments is stored in the folder 
```test_results_data```.

## 2. Testing of the Colour Extraction Process
<p align="justify">
To test the well detection methods, the user should open <code>test_main.py</code> 
and change the <code>measurement_function</code> argument of the 
<code>OptimisationLoop</code> class from <code>test_measurement_function</code> 
(the default) to <code>measurement_function</code>.
<!--><!-->
This way <code>test_colors.py</code> is called as the measurement function.
<!--><!-->
This script skips the usual picture-taking step and uses the image found in the 
folder <code>test_data</code> as the "captured" image directly.
<!--><!-->
One iteration should be sufficient to test the detection methods work. 
</p>

+ After this change, run it using the following command from the root directory.

```
$ python -m tests.test_main
```

## 3. Simulation of an Example Generated OT2 Run Script
<p align="justify">
The file <code>simulate_ot2_script.py</code> is an example of a generated 
opentrons run script. 
The outputs of the robot can be simulated by running the following command 
from the root directory.
</p>

```
$ opentrons_simulate tests/simulate_ot2_script.py
```