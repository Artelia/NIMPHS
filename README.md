# Toolsbox Blender

Import OpenFOAM / TELEMAC files inside Blender and generate astonishing renders!

## OpenFOAM

* Preview the imported file in the viewport
* Create a sequence (uses the [Stop-motion-OBJ add-on](https://github.com/neverhood311/Stop-motion-OBJ))
    * Mesh sequence (generates a mesh for each time point in the selected time range, ideal for small meshes)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory, ideal for large meshes)
* Import data as vertex colors
* Clip by a scalar

### Screenshots

Main panel - material preview |  Main panel - wireframe preview
:----------------------------:|:-------------------------------:
![Material preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_openfoam_a.png)  |  ![Wireframe preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_openfoam_b.png)

<p align="center">
  <img alt="Shading preview" width="716" height="460" src="https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_openfoam_c.png"/>
</p>

## TELEMAC

* Preview the imported file in the viewport (works with 2D / 3D simulations)
* Create a sequence
    * Mesh sequence (generates a shape key for each time point in the selected time range, ideal short sequences)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory, ideal for long sequences)
* Import data as vertex colors
* Interpolate mesh and vertex colors (for both type of sequences)

### Screenshots

Main panel - material preview |  Main panel - wireframe preview
:----------------------------:|:-------------------------------:
![Material preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_telemac_a.png)  |  ![Wireframe preview](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_telemac_b.png)

<p align="center">
  <img alt="Shading preview" width="694" height="430" src="https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.3.0/docs/source/images/readme/screenshot_telemac_c.png"/>
</p>