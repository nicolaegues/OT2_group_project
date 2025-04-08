FAQ & Notes
===========

+ When I use the ``get_colours`` function and run an optimisation script, I get 
  errors related to figures not appearing. What should I do?

*If using a Linux OS, ensure that the Python bindings for the chosen graphical 
user interface backend are installed and up to date.*

*For the Tkinter backend, use the following command to update bindings.*

.. code-block:: bash
    
    $ sudo apt install python3-tk

*For the Qt5 backend, use the following command to update bindings.*

.. code-block:: bash
    
    $ sudo apt install python3-pyqt5


Under Development
-----------------

True Automated Optimisation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The current implementation of OptoBot was developed in an environment where the 
Opentrons OT-2 robot was not connected to the internet.
This meant that 3rd-party Python packages could not be installed on the OT-2 
(through *SSH*), limiting the complexity of the OT-2 protocol script.
As a consequence, the current implementation of OptoBot handles the optimisation 
process on the user's computer and generates an OT-2 protocol script between 
iterations of optimisation.
The user has to upload the generated OT-2 protocol script at each iteration of 
optimisation, making the optimisation loop semi-automated.
Despite its semi-automated nature, the current implementation of OptoBot is 
flexible and offers easier integration with custom measurement processes of 
experimental response variables.

A feature for users that have an environment where their Opentrons OT-2 is 
connected to the internet and want to take advantage of a true automated 
optimisation loop is under development. 
This feature will generate a OT-2 protocol script that contains the entire 
experimental optimisation workflow, where the instructions for the OT-2 are 
updated in real-time at each iteration of optimisation.
The user will have to upload the generated OT-2 protocol script to the OT-2 
just once and the whole process will be automated.
Although this feature implements a true automated optimisation loop, it is less 
flexible as the measurement of experimental response variables between each 
iteration of optimisation have to be automated through the OT-2 itself.
Manual measurement processes of experimental response variables will not be 
supported and users should use the default semi-automated version that OptoBot 
offers in its current implementation.
