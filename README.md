# Toolsbox Blender

Import OpenFOAM files inside Blender and generate astonishing renders!

## Main features

### OpenFOAM

* Preview the imported file in the viewport
* Create a sequence (uses the [Stop-motion-OBJ add-on](https://github.com/neverhood311/Stop-motion-OBJ))
    * Mesh sequence (generates a mesh for each time point in the selected time range, ideal for small meshes)
    * Streaming sequence (generates a mesh when the frame changes and only keeps one mesh in memory, ideal for large meshes)
* Clip by a scalar

## Screenshots
![Main panel of the add-on](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.1.0/imgs/screenshot_a.png "Main panel")

![Object properties panel for streaming sequences](https://gitlab.arteliagroup.com/water/hydronum/toolsbox_blender/-/raw/release/0.1.0/imgs/screenshot_b.png "Object properties panel")