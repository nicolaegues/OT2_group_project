Usage Guide
===========

Introduction
------------
This package provides a flexible, open-source system for the **Opentrons OT-2 liquid-handling lab robot**, designed to optimize dye ratios using various **optimization algorithms** for precision **colour matching**. 

Using **Python** and an external **wired webcam** or **iPhone**, the system captures images of **well plates** and extracts **RGB values** for analysis. Users can select from two different optimization algorithms to iteratively adjust dye ratios and achieve their **target colour**:

- **Bayesian Optimization** (Guassian Process or Random Forest)
- **Particle Swarm Optimization**

The system enables users to iteratively refine dye mixtures for accurate colour reproduction in **lab automation workflows**.


Installation
------------

You can install this package using **pip** (if supported in the future) or install it directly from the source repository.

**Option 1: Install via pip**

.. code-block:: bash

    $ pip install OptoBot


**Option 2: Install from source**

Clone the repository from GitHub and install manually:

.. code-block:: bash

    $ git clone https://github.com/nicolaegues/OptoBot.git
    $ cd OT2_group_project
    $ pip install .


Basic Usage
-----------

*(To be completed once code implementation is finalized.)*


Common Pitfalls & Troubleshooting
---------------------------------

This package contains two options for image processing:

1. **Grid-based detection** - Users click on two wells within the well plate image and the programme generates a grid based on these points.
2. **Contour detection** - The programme automatically detects the wells within the well plate image.

Users may not be able to successfully use Contour Detection depending on the quality of their camera and the environments lighting. Grid-based detection acts as a reliable fallback option. 


---

This document will be updated as more functionalities are developed and tested.


