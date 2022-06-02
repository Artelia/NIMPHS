# Change log

## [0.2.0] - 2022-06-02

This version implements new features to manipulate TELEMAC files.
It also comes with new features for the OpenFOAM module. See the *added* section for more details.

### Added

* **View 3D > Blender toolsbox panel > OpenFOAM**

    * 

### Fixed

### Changed

* Global file architecture
*

## [0.1.0] - 2022-04-19

First release of the add-on. This version implements the first features. See the *added* section for more details.

### Added

* **View 3D > Sidebar > Blender toolsbox panel > OpenFOAM**

    * Import an OpenFOAM file (.foam)
        * Reload the file when temporary data is not loaded

    * Preview
        * Select a time step
        * Select the set of data to preview (point data, visible in "material preview")
        * Clip
            * Clip by a scalar
                * Select a scalar
                * Type a value
                * Invert

    * Create a sequence
        * Type a list of point data variables to import as vertex colors
        * Give a name to the sequence
        * Type: mesh sequence (uses the [Stop-motion-OBJ add-on](https://github.com/neverhood311/Stop-motion-OBJ))
            * Select start/end time points
            * Behaviour: *generates a mesh for each time step in the selected time frame and shows the mesh which corresponds to the current frame and time point. Ideal for small meshes.*
        * Type: streaming sequence
            * Select a start frame
            * Select the length of the animation
            * Behaviour: *generates the mesh which corresponds to the current frame and time point. Updates automatically when the frame changes. Ideal for large meshes.*

* **Object properties > OpenFOAM Sequence settings**

    * *This panel is only accessible for streaming sequences*

    * Streaming sequence settings
        * Update checkbox (enable/disable updates for this sequence)
        * Edit the start frame
        * Edit the length of the animation
        * Edit the list of point data to import each frame
        * Clip settings
            * Clip by a scalar
                * Select a scalar
                * Type a value
                * Invert