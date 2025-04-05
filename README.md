<p align="center">
  <img src="docs/_static/logo.png" alt="OptoBot Logo">
</p>

## Overview
<p align="justify">
Welcome! <code>OptoBot</code> is a package for implementing automated 
experimental optimisation using an <a href="https://opentrons.com/robots/ot-2">Opentrons OT-2</a> 
liquid handling robot. 
<!--><!-->
<code>OptoBot</code> aims to provide lab scientists with a simple interface for 
implementing experimental optimisation in their own work with minimal 
programming experience.
<!--><!-->
In its current implementation, <code>OptoBot</code> focuses on automating and 
optimising colorimetric experiments where experimental products can be 
assessed based on their measured RGB colour using a camera.
<!--><!-->
<code>OptoBot</code> can be used to semi-automate and optimise other 
experiments but manual measurements of experimental products and manual inputs 
are required.
</p>

## Installation
<p align="justify">
<code>OptoBot</code> can be installed from <code>PyPI</code> using the 
following command.
</p>

```
$ pip install optobot
```

<p align="justify">
<code>OptoBot</code> can also be installed from <code>source</code> using the 
following commands.
</p>

```
$ git clone git@github.com:nicolaegues/OptoBot.git
$ pip install OptoBot/.
```