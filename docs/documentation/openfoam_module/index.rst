OpenFOAM
========

* :ref:`openfoam_import_file`
* :ref:`openfoam_previewing_tools`
* :ref:`openfoam_create_sequence`

.. _openfoam_import_file:

Import a file
#############

| You will find the main panel in the 3D viewport, under the panels section (on the right).
| Hit ``n`` to open this section if you do not find it (with the mouse in the 3D viewport).
| Then simply use the ``import`` button as shown here:

.. important:: 
    For large meshes (> 100k vertices), this operation can take several seconds to complete.

.. image:: /images/OpenFOAM/import_file.png
    :width: 35%
    :alt: Import an OpenFOAM file (button)
    :align: center

|

.. _openfoam_previewing_tools:

Previewing tools
################

| Once you have imported a file, you should see the mesh in the viewport.
| You can select the ``TBB_preview`` object and hit ``.`` on your numpad to center the view on it.

.. image:: /images/OpenFOAM/preview_panel.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Reload**: reloads the selected file (`when something went wrong or temporary data is not available anymore`)
* **Time step**: time step to preview
* **Points**: point data to preview as vertex colors (`switch to material preview to see it`)
* **Preview**: preview the mesh with the selected parameters

Clip
----

.. important:: 
    Once you have set a clip, you have to click on the `preview` button to update the mesh.

| You can clip a mesh as you would do in ParaView.

.. image:: /images/OpenFOAM/clip_panel.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Type**: clipping method (Scalars, box, etc)

    * **Scalars clipping method**
        * **Scalars**: name of scalar to clip on
        * **Value**: set the clipping value
        * **Invert**: flag on whether to flip/invert the clip. When True, only the mesh below 'value' will be kept. When False, only values above 'value' will be kept

.. _openfoam_create_sequence:

Create a sequence
#################

| You can create sequences to automatically switch between time steps using the timeline.

Mesh sequence
-------------

| This type of sequence holds every time step in memory (a mesh is built for each time step).
| That is why it is not recommended to use this sequence for large meshes.
| It is built using the `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/releases>`_. Thus you can use the features associated for this sequence.

.. image:: /images/OpenFOAM/create_mesh_sequence.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Start**: starting point of the sequence (time step)
* **End**: ending point of the sequence (time step)
* **Import point data**: flag to indicate that it must import some point data as vertex colors
* **List**: list of point data to import (separate each with a ``;``)
* **Name**: name of the sequence

Streaming sequence
------------------

| This type of sequence holds only one mesh in memory. It is recommended to use for large meshes.
| The mesh automatically updates when the frame changes.

.. image:: /images/OpenFOAM/create_streaming_sequence.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Frame start**: starting point of the sequence (frame)
* **Length**: length of the animation (time steps)
* **Import point data**: flag to indicate that it must import some point data as vertex colors
* **List**: list of point data to import (separate each with a ``;``)
* **Name**: name of the sequence