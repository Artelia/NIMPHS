.. _telemac-create-sequence:

Create a sequence
=================

| You can create sequences to automatically switch between time steps using the timeline.


.. _telemac-create-mesh-sequence:

Mesh sequence
-------------

| This type of sequence uses shape keys to update the mesh. So it holds every time steps in memory.
| That is why it is not recommended to use this sequence for long sequences.

.. image:: /images/telemac/create_mesh_sequence.png
    :width: 60%
    :alt: Create mesh sequence button
    :align: center
    :class: rounded-corners

|

.. image:: /images/telemac/create_mesh_sequence_operator.png
    :width: 60%
    :alt: Create mesh sequence operator
    :align: center
    :class: rounded-corners

|


.. _telemac-point-data-properties:

Point data
**********

* **Method**: remapping method for point data ('LOCAL' or 'GLOBAL').
* **Add**: select a new point data to import as vertex colors.


.. _telemac-mesh-sequence-properties:

Sequence
********

* **Start**: starting point of the sequence (time step).
* **End**: ending point of the sequence (time step).
* **Name**: name to give to the sequence object.


.. _telemac-mesh-sequence-object-properties:

Mesh sequence object
********************

| You can edit mesh sequences settings in the `Object properties` panel.

.. image:: /images/telemac/mesh_sequence_properties.png
    :width: 60%
    :alt: Preview panel
    :align: center
    :class: rounded-corners

|


.. _telemac-create-streaming-sequence:

Streaming sequence
------------------

| This type of sequence holds only one time step in memory. It is recommended to use for long sequences.
| The mesh automatically updates when the frame changes.

.. image:: /images/telemac/create_streaming_sequence.png
    :width: 60%
    :alt: Create streaming sequence button
    :align: center
    :class: rounded-corners

|

.. image:: /images/telemac/create_streaming_sequence_operator.png
    :width: 60%
    :alt: Create streaming sequence operator
    :align: center
    :class: rounded-corners

|


.. _telemac-streaming-sequence-properties:

Sequence
********

* **Start**: starting point of the sequence (time step).
* **Length**: length of the animation (time steps).
* **Shade smooth**: indicate whether to use smooth shading or flat shading.
* **Name**: name to give to the sequence object.


.. _telemac-streaming-sequence-object-properties:

Streaming sequence object
*************************

| You can edit streaming sequence settings in the `Object properties` panel.

.. image:: /images/telemac/streaming_sequence_properties.png
    :width: 60%
    :alt: Preview panel
    :align: center
    :class: rounded-corners

|
