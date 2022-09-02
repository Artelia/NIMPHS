.. _telemac-point-data:

Point data
==========

Here is the list of operations related to point data.


.. _telemac-compute-ranges-point-data-values:

Compute ranges point data values
--------------------------------

|   For several tasks you may want to know the range of some variables.
|   This operator lets you compute this information. It computes the range of point data values for all time steps.

.. image:: /images/telemac/telemac_compute_ranges_point_data_values.png
    :width: 60%
    :alt: Compute ranges point data values operator
    :align: center
    :class: rounded-corners

|


.. _telemac-compute-ranges-point-data-values-variables-properties:

Variables
*********

* **Add**: add point data to do the computation.

Example of ranges computed for several variables:

.. image:: /images/telemac/telemac_ranges_point_data_values.png
    :width: 60%
    :alt: Computed ranges
    :align: center
    :class: rounded-corners

|


.. _telemac-extract-point-data:

Extract point data
------------------

|   You can extract point data of a vertex of the mesh as a time series.
|   Extracted data will be stored in a custom property of the targeted object.

.. image:: /images/telemac/telemac_extract_point_data.png
    :width: 60%
    :alt: Extract point data operator
    :align: center
    :class: rounded-corners

|


.. _telemac-extract-point-data-extract-properties:

Extract
*******

* **Vertex id**: index of the vertex from which extract data (indices start at 0).
* **Point data**: name of point data to extract.
* **Target**: target object which will store extracted point data.


.. _telemac-extract-point-data-time-properties:

Time
*******

* **Start**: starting point of the sequence of data to export.
* **Point data**: ending point of the sequence of data to export.

Example of extracted data visualized in the graph editor:

.. image:: /images/telemac/telemac_extracted_point_data.png
    :width: 60%
    :alt: Extracted point data
    :align: center
    :class: rounded-corners

|
