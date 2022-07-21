# Toolbox Blender

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

Material preview  |  Wireframe preview
:----------------:|:------------------:
![Material preview](https://bit.ly/3zoV67P)  |  ![Wireframe preview](https://bit.ly/3PsXoIw)


## TELEMAC

* Works with 2D and 3D files
* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Linearly interpolate mesh and vertex colors (for both type of sequences) to render smoother animations

### Screenshots

Material preview |  Wireframe preview
:---------------:|:------------------:
![Material preview](https://bit.ly/3PqZ84S)  |  ![Wireframe preview](https://bit.ly/3yWhzYh)
