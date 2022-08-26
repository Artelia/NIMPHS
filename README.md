# NIMPHS

**N**umerous **I**nstruments to **M**anipulate and **P**ost-process **H**ydraulic **S**imulations.

### Short description

Import OpenFOAM (.foam) and TELEMAC (.slf) files in Blender, and make use of its powerful 3D renderer to generate photorealistic images and animations!

Built with:

* [PyVista](https://github.com/pyvista/pyvista)
* [Stop-motion-OBJ add-on](https://github.com/neverhood311/Stop-motion-OBJ)

## OpenFOAM

* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Clip mesh by a scalar

### Screenshots

Wireframe preview                     |  Material preview
:------------------------------------:|:-----------------------------------:
![Wireframe](https://bit.ly/3APEsPi)  |  ![Material](https://bit.ly/3pOWB9u)


## TELEMAC

* Works with 2D and 3D files
* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Linearly interpolate mesh and vertex colors (for both type of sequences) to render smoother animations
* Extract point data from one vertex as time series
* Generate volumes from TELEMAC-3D simulations

### Screenshots

Wireframe preview                     |  Material preview
:------------------------------------:|:-----------------------------------:
![Wireframe](https://bit.ly/3QLQXRv)  |  ![Material](https://bit.ly/3RflFCa)

## Gallery

Here are some creations made with NIMPHS.

### OpenFOAM

Model A                                             | Model B
:--------------------------------------------------:|:--------------------------------------------------:
![TELEMAC gallery, model A](https://bit.ly/3RfjvT4) | ![TELEMAC gallery, model B](https://bit.ly/3AJNIDx)

Model C                                              | Model D
:---------------------------------------------------:|:------------------------------:
![OpenFOAM gallery, model C](https://bit.ly/3ApCGTJ) | ![None](https://bit.ly/3TnnKOG)

### TELEMAC

Model A                                              | Model B
:---------------------------------------------------:|:----------------------------------------------:
![OpenFOAM gallery, model A](https://bit.ly/3pLn4om) | ![OpenFOAM gallery, model B](https://bit.ly/3clNytA)

