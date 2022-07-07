.. _openfoam_create_sequence:

Create a sequence
=================

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
    :class: rounded-corners

|

.. image:: /images/openfoam/create_mesh_sequence_operator.png
    :width: 60%
    :alt: Create mesh sequence operator
    :align: center
    :class: rounded-corners

|

Import settings
***************

* **Decompose polyhedra**: indicate whether polyhedra are to be decomposed when read. If True, decompose polyhedra into tetrahedra and pyramids.
* **Triangulate**: more complex polygons will be broken down into triangles.
* **Case**: indicate whether decomposed mesh or reconstructed mesh should be read.

Clip
****

| You can clip a mesh as you would do in ParaView.

* **Type**: clipping method (Scalars, box, etc)

    * **Scalars clipping method**
        * **Scalars**: name of scalar to clip on.
        * **Value**: set the clipping value.
        * **Invert**: flag on whether to flip/invert the clip. When True, only the mesh below 'value' will be kept. When False, only values above 'value' will be kept.

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
    :class: rounded-corners

|

.. image:: /images/openfoam/create_streaming_sequence_operator.png
    :width: 60%
    :alt: Create streaming sequence operator
    :align: center
    :class: rounded-corners

|

Sequence
********

* **Start**: starting point of the sequence (time step).
* **Length**: length of the animation (time steps).
* **Shade smooth**: indicate whether to use smooth shading or flat shading.
* **Name**: name to give to the sequence object.

Streaming sequence object
*************************

| You can edit streaming sequence settings in the `Object properties` panel.

.. image:: /images/openfoam/streaming_sequence_properties.png
    :width: 60%
    :alt: Streaming sequence properties panel
    :align: center
    :class: rounded-corners

|