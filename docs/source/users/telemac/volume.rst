.. _telemac-volume:

Volume
======

.. important::
    You must have installed pyopenvdb to use this feature.

|   It is possible to generate volume sequences for TELEMAC-3D files.
|   These volume sequences are exported as .vdb file sequences.
|   The VDB format is a common file format used for volumes in computer graphics.


.. _telemac-generate-volume-sequence:

Generate volume sequence
------------------------

|   This operator lets you generate volume sequences from TELEMAC-3D files.
|   Point data are exported "raw" (without any remapping). Thus, you can use the 'Map Range' node to do so.


.. image:: /images/telemac/telemac_3d_generate_volume_sequence.png
    :width: 60%
    :alt: Generate volume sequence operator
    :align: center
    :class: rounded-corners

|


.. _telemac-generate-volume-sequence-hardware-properties:

Hardware
********

* **Mode**: computation mode, select one from:

    * **Default**: can be very slow for large dimensions.
    * **Multiprocessing**: multi-threading computation mode, can speed up a lot the computation.
    * **CUDA**: make use of CUDA capable device (*if numba is installed*), can **dramatically** improve the computation speed.


.. _telemac-generate-volume-sequence-volume-properties:

Volume
******

Size
####

* **Volume definition**: define the volume dimensions either by providing dimensions or a voxel size.

    * **Dimensions**: define the volume by giving custom dimensions (L x W x H).
    * **Voxel size**: define the volume using a voxel size.

Density
#######

* **Add**: add a point data to export in voxels. For now, it is limited to only one point data exported at a time.


.. _telemac-generate-volume-sequence-interpolation-properties:

Interpolation
*************

Space
#####

* **Type**: type of interpolation.
* **Steps**: number of planes to interpolated between each known plane.

Time
####

* **Type**: type of interpolation.
* **Steps**: number of time points to interpolate between each known time point.


.. _telemac-generate-volume-sequence-sequence-properties:

Sequence
********

* **Output directory**: path to the directory where to place generated .vdb files.
* **File name**: name to give to the generated files.
* **Start**: starting point of the sequence to export (time point).
* **End**: ending point of the sequence to export (time point).

Example of generated volume sequence:

.. image:: /images/telemac/telemac_3d_generated_volume_sequence.png
    :width: 60%
    :alt: Generated volume sequence
    :align: center
    :class: rounded-corners

|


.. _telemac-set-volmume-origin:

Set volume origin
-----------------

|   This operator lets you align (in the 3D space) a generated volume sequence to your TELEMAC-3D file.
|   The volume will also be resized to match the dimensions of the model.

.. image:: /images/telemac/telemac_3d_set_volume_origin.png
    :width: 60%
    :alt: Extract point data operator
    :align: center
    :class: rounded-corners

|


.. _telemac-set-volmume-origin-selection-properties:

Selection
*********

* **Target**: target model to fit dimensions and origin.

Before:

.. image:: /images/telemac/telemac_3d_volume_origin_before.png
    :width: 60%
    :alt: Before set origin operator
    :align: center
    :class: rounded-corners

|

After:

.. image:: /images/telemac/telemac_3d_volume_origin_after.png
    :width: 60%
    :alt: After set origin operator
    :align: center
    :class: rounded-corners

|
