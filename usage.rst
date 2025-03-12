Usage Guide
===========

Introduction
------------
This package provides a flexible, open-source system for the **Opentrons OT-2 liquid-handling lab robot**, designed to optimize dye ratios using various **optimization algorithms** for precision **colour matching**. 

Using **Python** and an external **wired webcam** or **iPhone**, the system captures images of **well plates** and extracts **RGB values** for analysis. Users can select from four different optimization algorithms to iteratively adjust dye ratios and achieve their **target colour**:

- **Simplex Method**
- **Bayesian Optimization**
- **Particle Swarm Optimization**
- **Differential Evolution**

The system enables users to iteratively refine dye mixtures for accurate colour reproduction in **lab automation workflows**.


Installation
------------

You can install this package using **pip** (if supported in the future) or install it directly from the source repository.

### **Option 1: Install via pip**
*(To be confirmed when package is registered on PyPI)*

.. code-block:: python

    pip install my_package_name  # Placeholder name


### **Option 2: Install from source**

Clone the repository from GitHub and install manually:

.. code-block:: python

    import os
    os.system("git clone https://github.com/nicolaegues/OT2_group_project.git")
    os.chdir("OT2_group_project")
    os.system("pip install .")


Basic Usage
-----------

*(To be completed once code implementation is finalized.)*


Advanced Examples
-----------------

Below are some advanced use cases of the package, focusing on image processing and the different optimization algorithms.

### **1. Image Processing Example**
*(Example to be added once image processing pipeline is implemented.)*

### **2. Using the Optimization Algorithms**
*(Example to be added for each of the four optimization algorithms.)*


Common Pitfalls & Troubleshooting
---------------------------------

*(To be completed as issues arise during system testing.)*


Further Resources
-----------------

For additional details, please refer to:

- *(Documentation URL to be added once available.)*
- *(Relevant research papers, tutorials, or guides to be included as applicable.)*


---

This document will be updated as more functionalities are developed and tested.


