Notes
============

A Fully Automated Version in the Future
--------------------------------------

The package was designed to allow for a scenario where the robot does not
have a network connection. This scenario means that, for instance, no 
external python packages can be imported into the OT2 protocol script as 
this requires connecting to the robot via SSH and manually installing
the packages in the robot's terminal. 
As a consequence, the protocol script must be kept simple and cannot contain 
any optimisation funtcion calls, for example. OptoBot bypasses this by 
running a separate python function that generates a new (simple) protocol 
script at each iteration. 

However, this limits the current implementation to being semi-automatic. In the
future, this package will allow for the scenario where the robot is connected
to the network, and the user wants to take advantage of this fact to fully
automate the entire experiment. A proposed version of this - still in 
developement - can be found in the feat/network branch in the GitHub repository 
of the OptoBot package. 

In this version, the optimisation loop works just like in the current 
implementation - except that the experimental configuration and the automated 
optimisation loop are both defined within the OT2 protocol script itself. The 
call to optimise the model is hereby performed within the run() function of the
robot, after the labware is defined. At each iteration, the instructions for the 
robot are updated in real-time - all still within the same protocol script. 
The user thus only ever needs to upload one protocol to the app at the beginning. 

One downside to this implementation is that since it is fully-automated, the 
option to let the user manually input measurements is removed. In the context of 
a colorimetric expriment, this means the well detection and color extraction must 
happen fully automatically. In the future, if users do not have a way of performing 
the measurementsin an automated fashion, they should default to the original no-network
scenario.



