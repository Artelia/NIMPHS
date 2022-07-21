# Toolbox Blender

Import OpenFOAM (.foam) and TELEMAC (.slf) files inside Blender, and make use of its powerful 3D renderer to generate photorealistic images and animations!

Built with:

* [PyVista](https://github.com/pyvista/pyvista)
* [Stop-motion-OBJ add-on](https://github.com/neverhood311/Stop-motion-OBJ)

## OpenFOAM

* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Clip by a scalar

### Screenshots

Main panel - material preview |  Main panel - wireframe preview
:----------------------------:|:-------------------------------:
![Material preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_openfoam_a.png)  |  ![Wireframe preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_openfoam_b.png)

<p align="center">
  <img alt="Shading preview" width="716" height="460" src="https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_openfoam_c.png"/>
</p>

## TELEMAC

* Works with 2D and 3D files
* Preview the imported file in the viewport
* Create sequences to render animations
    * Mesh sequence (generates a mesh for each time point in the selected time range)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory)
* Import point data as vertex colors (color attributes)
* Linearly interpolate mesh and vertex colors (for both type of sequences) to render smoother animations

### Screenshots

Main panel - material preview |  Main panel - wireframe preview
:----------------------------:|:-------------------------------:
![Material preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_telemac_a.png)  |  ![Wireframe preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_telemac_b.png)

<p align="center">
  <img alt="Shading preview" width="694" height="430" src="https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_telemac_c.png"/>
</p>
