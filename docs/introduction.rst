Introduction
============

Experimental Automation & Optimisation
--------------------------------------
The automation of experimental processes has the potential to revolutionise 
workflows of scientists in both academic and industrial laboratories.
Leveraging robotics enables experiments to become more accurate, safe and 
reproducible while decreasing the overall experimental time. 
Scientists can also focus on the more important aspects of their research 
through automating laborious and repetitive tasks.

A major benefit of experimental automation is the opportunities it brings for 
implementing automated, closed-loop experimental optimisation.
Experimental optimisation is the procedure of finding parameter values that 
optimise a response in the least number of trial runs.
Traditional experimental optimisation procedures, such as grid-search 
optimisation, are often time and resource inefficient.
Automation enables the integration of more efficient optimisation algorithms, 
such as particle swarm optimisation, within a closed-loop framework.
This gives scientists the power to harness the full capabilities of both 
experimental automation and modern experimental optimisation techniques.

Although experimental automation and optimisation offer great potential, in 
practice there are a wide range challenges that arise when integrating them 
into laboratories.
Automation is an expensive endeavour with logistical factors such as the cost 
of equipment, installation, maintenance, consumables and lab space requiring 
careful consideration.
Technical factors like retraining staff or hiring staff with programming 
experience can further increase the costs and time needed.
In particular, these challenges are pronounced in the settings of small to 
medium scale laboratories, such as in academia, where budgets are limited and 
research goals are ever changing.

Opentrons OT-2 Robot
--------------------
`Opentrons <https://opentrons.com/>`_ is a US-based biotech business that 
specialises in manufacturing liquid handling robots to further the field of 
experimental automation.
Their mission is to make robotics more accessible to laboratories, tackling the 
challenges mentioned in the previous section and empowering scientists with 
experimental automation.

The `Opentrons OT-2 <https://opentrons.com/robots/ot-2>`_ is an affordable 
bench-top liquid handling robot designed to automate lab work such as 
dispensing, mixing and transferring liquids. 
It supports the use of up to two single-channel or eight-channel pipette heads, 
enabling the handling of liquids between 1μL and 1000μL in volume.
The OT-2 is a modular robot and compatible with ANSI/SLAS-compliant lab 
equipment, making it a flexible platform that can be customised to perform more 
complex tasks and experiments.

A highlight of the OT-2 is its open-source software, which allows scientists to 
develop custom protocols that meet their experimental requirements. 
Opentrons provides the `Opentrons API <https://docs.opentrons.com/v2/>`_ 
through the ``opentrons`` package for developing custom protocols that control 
the OT-2. 
Developed protocols can be uploaded to the OT-2 through the 
`Opentrons App <https://opentrons.com/ot-app>`_ which offers a straightforward
graphical user interface for robot calibration, protocol management and 
protocol execution.

What Does OptoBot Do?
---------------------
**OptoBot** is a package for implementing automated experimental optimisation 
using the `Opentrons OT-2 <https://opentrons.com/robots/ot-2>`_ liquid handling 
robot.
It aims to provide scientists with a simple interface for implementing 
closed-loop experimental optimisation in their own work with minimal 
programming experience.

In its current implementation OptoBot focuses on automating and optimising 
colorimetric experiments. 
These are experiments where the experimental products can be assessed based on 
their measured RGB colour using a camera. 
For example, an experiment where red, green and blue liquids (e.g. food 
colouring) along with water are mixed to produce a pre-defined target colour. 
The experimental setup of such an experiment is shown below.

.. figure:: _static/example-setup.png
    :alt: Example Experimental Setup
    :align: center
    :width: 350

    Figure: An example experimental setup for a colorimetric experiment.

OptoBot can also be used to semi-automate and optimise other experiments 
but manual measurements of experimental products and manual inputs are 
required. 
We aim to develop features for automating a wider range of experiments in the 
future.

OptoBot addresses the wider challenge of decreasing the programming barrier 
for integrating automated experimental optimisation in small to medium scale 
laboratories.
While the `Opentrons API <https://docs.opentrons.com/v2/>`_ provides a powerful 
and comprehensive interface for controlling the OT-2, it does not come with 
built-in features for experimental optimisation.
Furthermore, the lack of open-source packages in this area is an important  
driving factor for development of OptoBot.
