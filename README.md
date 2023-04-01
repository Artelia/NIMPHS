# NIMPHS

**N**umerous **I**nstruments to **M**anipulate and **P**ost-process **H**ydraulic **S**imulations.

## Short description

Import OpenFOAM (.foam) and TELEMAC (.slf) files in Blender, and make use of its powerful 3D renderers to generate images and animations!

## Documentation

Installation guide and documentation can be found here: [NIMPHS documentation](https://artelia.github.io/NIMPHS/)

## Features overview

### OpenFOAM

* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Clip mesh by a scalar

#### Screenshots

Wireframe preview                     |  Material preview
:------------------------------------:|:-----------------------------------:
![Wireframe](https://bit.ly/3APEsPi)  |  ![Material](https://bit.ly/3pOWB9u)

### TELEMAC

* Works with 2D and 3D files
* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Linearly interpolate mesh and vertex colors (for both type of sequences) to render smoother animations
* Extract point data from one vertex as time series
* Generate volumes from TELEMAC-3D simulations

#### Screenshots

Wireframe preview                     |  Material preview
:------------------------------------:|:-----------------------------------:
![Wireframe](https://bit.ly/3QLQXRv)  |  ![Material](https://bit.ly/3RflFCa)

## Gallery

Here are some creations made with NIMPHS.

### OpenFOAM

Model A                                              | Model B
:---------------------------------------------------:|:---------------------------------------------------:
![OpenFOAM gallery, model A](https://bit.ly/3RfjvT4) | ![OpenFOAM gallery, model B](https://bit.ly/3AJNIDx)

Model C                                              | Model D
:---------------------------------------------------:|:------------------------------:
![OpenFOAM gallery, model C](https://bit.ly/3ApCGTJ) | ![None](https://bit.ly/3TnnKOG)

### TELEMAC

Model A                                              | Model B
:---------------------------------------------------:|:---------------------------------------------------:
![OpenFOAM gallery, model A](https://bit.ly/3pLn4om) | ![OpenFOAM gallery, model B](https://bit.ly/3clNytA)

## Contributing

![Contributor Covenant v2.1](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)

We welcome contributions and hope that our [contributing guide](https://github.com/Artelia/NIMPHS/blob/main/CONTRIBUTING.md)
will help you to start easily.Make sure to read the [code of conduct](https://github.com/Artelia/NIMPHS/blob/main/CODE_OF_CONDUCT.md)
before contributing.

## Citing NIMPHS

There is a [paper about NIMPHS](https://joss.theoj.org/papers/10.21105/joss.04868)!

If you are using NIMPHS in your research, please cite our work.

> Olart et al., (2023). NIMPHS: Numerous Instruments to Manipulate and Post-process Hydraulic Simulations. Journal of Open Source Software, 8(83), 4868, https://doi.org/10.21105/joss.04868

### Bibtex

```
@article{Olart2023,
    doi = {10.21105/joss.04868},
    url = {https://doi.org/10.21105/joss.04868},
    year = {2023},
    publisher = {The Open Journal},
    volume = {8},
    number = {83},
    pages = {4868},
    author = {Félix Olart and Thibault Oudart and Olivier Bertrand and Mehdi-Pierre Daou},
    title = {NIMPHS: Numerous Instruments to Manipulate and Post-process Hydraulic Simulations}, journal = {Journal of Open Source Software}
} 
```