OpenFOAM
========

* :ref:`openfoam_import_file`
* :ref:`openfoam_previewing_tools`
* :ref:`openfoam_create_sequence`

.. important::
    Useful information are printed in the console (times, errors, warnings, etc).
    Do not hesitate to open it. On Windows, ``Window ‣ Toggle System Console``.


.. _openfoam_import_file:

Import a file
#############

| Import a file under ``File > Import > OpenFOAM``.

.. important:: 
    For large meshes (> 100k vertices), this operation can take several seconds to complete.

.. image:: /images/openfoam/import.png
    :width: 60%
    :alt: Import OpenFOAM file
    :align: center

|

.. _openfoam_previewing_tools:

Previewing tools
################

| Once you have imported a file, you should see the mesh in the viewport.
  You can select the ``TBB_OpenFOAM_preview`` object and hit ``.`` on your numpad to center the view on it.

| Hit ``n`` to open the sidebar if you do not find it (with mouse focus in the 3D viewport).

.. image:: /images/openfoam/preview.png
    :width: 60%
    :alt: Preview panel
    :align: center

|

.. important:: 
    If you change a parameter, you have to click on the `preview` button to update the mesh.

.. _openfoam_import_settings:

Import settings
---------------

* **Decompose polyhedra**: indicate whether polyhedra are to be decomposed when read. If True, decompose polyhedra into tetrahedra and pyramids.
* **Triangulate**: more complex polygons will be broken down into triangles.
* **Case**: indicate whether decomposed mesh or reconstructed mesh should be read.

.. _openfoam_clip:

Clip
----

| You can clip a mesh as you would do in ParaView.

* **Type**: clipping method (Scalars, box, etc)

    * **Scalars clipping method**
        * **Scalars**: name of scalar to clip on.
        * **Value**: set the clipping value.
        * **Invert**: flag on whether to flip/invert the clip. When True, only the mesh below 'value' will be kept. When False, only values above 'value' will be kept.

Preview
-------

* **Points**: point data to preview as vertex colors (`switch to material preview to see it`).
* **Time step**: time step to preview.
* **Preview**: preview the mesh with the selected parameters.

.. _openfoam_create_sequence:

Create a sequence
#################

| You can create sequences to automatically switch between time steps using the timeline.

Mesh sequence
-------------

| This type of sequence holds every time step in memory (a mesh is built for each time step).
| That is why it is not recommended to use this sequence for large meshes.
| It is built using the `Stop-motion-OBJ <https://github.com/neverhood311/Stop-motion-OBJ/wiki>`_.
  Thus you can use the features associated for this sequence.

.. image:: /images/openfoam/create_mesh_sequence.png
    :width: 60%
    :alt: Create mesh sequence button
    :align: center

|

.. image:: /images/openfoam/create_mesh_sequence_operator.png
    :width: 60%
    :alt: Create mesh sequence operator
    :align: center

|

:ref:`openfoam_import_settings`
*******************************

:ref:`openfoam_clip`
********************

Point data
**********

* **Method**: remapping method for point data ('LOCAL' or 'GLOBAL').
* **Add**: select a new point data to import as vertex colors.

Sequence
********

* **Start**: starting point of the sequence (time step).
* **End**: ending point of the sequence (time step).
* **Name**: name to give to the sequence object.

Streaming sequence
------------------

| This type of sequence holds only one mesh in memory. It is recommended to use for large meshes.
| The mesh automatically updates when the frame changes.

.. image:: /images/openfoam/create_streaming_sequence.png
    :width: 60%
    :alt: Create streaming sequence button
    :align: center

|

.. image:: /images/openfoam/create_streaming_sequence_operator.png
    :width: 60%
    :alt: Create streaming sequence operator
    :align: center

|

Sequence
********

* **Start**: starting point of the sequence (time step).
* **Length**: length of the animation (time steps).
* **Shade smooth**: indicate whether to use smooth shading or flat shading.
* **Name**: name to give to the sequence object.

Streaming sequence settings
---------------------------

| You can edit streaming sequences settings in the `Object properties` panel.

.. image:: /images/openfoam/streaming_sequence_properties.png
    :width: 60%
    :alt: Streaming sequence properties panel
    :align: center

|