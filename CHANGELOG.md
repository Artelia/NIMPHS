# Change log

## [0.3.0] - WIP

### Added

* **Edit > Preferences > Addons > Toolsbox blender**

    * Indicate specific settings for:
        * Logging level
        * Name of the extensions of files to import for each module

### Fixed

### Changed

--------------------------------------------------------------------------------

## [0.2.0] - 2022-06-02

This version implements new features to manipulate TELEMAC files.
It also comes with new features for the OpenFOAM module. See the *added* section for more details.

### Added

* **View 3D > Sidebar > OpenFOAM**

    * Small OpenFOAM icon
    * Select 'None' under preview 'points data'
    * Option: decompose polyhedra
    * Option: triangulate
    * Option: case type ('decomposed' or 'reconstructed')

* **View 3D > Sidebar > TELEMAC**

    * Small TELEMAC icon

    * Import a TELEMAC file (.slf)
        * Reload the file when temporary data is not loaded
        * Can import 2D/3D files:
            * Case: 2D
                * Tries two generate two objects
                    * One with z-values set to 'BOTTOM' or 'FOND'
                    * One with z-values set to 'WATER DEPTH', 'HAUTEUR D'EAU', 'FREE SURFACE or 'SURFACE LIBRE'
            * Case: 3D
                * Tries two generate an object per plane
                    * z-values of the generated objects are set to 'ELEVATION Z' or 'COTE Z'
    
    * Preview
        * Select a time step
        * Select the set of data to preview (point data, visible in "material preview")
        * Option: normalize (remap vertices in [-1;1])

    * Create a sequence
        * Type a list of point data variables to import as vertex colors
        * Give a name to the sequence
        * Type: mesh sequence
            * Select start/end time points
            * Behaviour: *generates a shape key for each time step in the selected time frame. Ideal for short sequences.*
        * Type: streaming sequence
            * Select a start frame
            * Select the length of the animation
            * Behaviour: *generates the mesh which corresponds to the current frame and time point. Updates automatically when the frame changes. Ideal for long sequences.*

    * Preview objects are generated under a collection named 'TBB_TELEMAC'
    * Values for vertex colors are ramaped into [0;1] using global min/max

* **Object properties > OpenFOAM Streaming sequence**

    * *This panel is only accessible for streaming sequences*

    * Option: shade smooth
    * Option: decompose polyhedra
    * Option: triangulate
    * Option: case type ('decomposed' or 'reconstructed')

* **Object properties > TELEMAC Streaming sequence**

    * *This panel is only accessible for streaming sequences*

    * Streaming sequence settings
        * Update checkbox (enable/disable updates for this sequence)
        * Edit the start frame
        * Edit the length of the animation
        * Option: shade smooth
        * Option: normalize
        * Edit the list of point data to import each frame
        * Interpolate (interpolates vertices and vertex colors)
            * Select interpolation method
            * Select the number of time steps to add between each time point

* **Object properties > TELEMAC Mesh sequence**

    * *This panel is only accessible for mesh sequences*

    * Mesh sequence settings
        * Edit the list of point data to import each frame

### Fixed

* **OpenFOAM**

    * Create sequence operator was not using 'load_openfoam_file'

### Changed

* **Files**

    * Global file architecture (changed module name from 'src' to 'tbb')
    * Now using absolute paths instead of relative paths for imports
    * Now using an autoloader to register classes
    * Refactored some utils functions and classes so they can be used for both modules

* **UI**

    * Split 'Blender toolsbox panel' into two different panels (OpenFOAM / TELEMAC)

* **OpenFOAM**

    * Preview objects are now generated under a collection named 'TBB_OpenFOAM'
    * Renamed 'OpenFOAM sequence settings' into 'OpenFOAM Streaming sequence' in the object properties for streaming sequences

* **Properties**

    * Refactored organization of properties (see schema in the docs)

--------------------------------------------------------------------------------

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