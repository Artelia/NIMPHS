TELEMAC
=======

* :ref:`telemac_import_file`
* :ref:`telemac_previewing_tools`
* :ref:`telemac_create_sequence`

.. important::
    Useful information are printed in the console (times, errors, warnings, etc). Do not hesitate to open it. On Windows, ``Window ‣ Toggle System Console``


.. _telemac_import_file:

Import a file
#############

| You will find the main panel in the 3D viewport, under the panels section (on the right).
| Hit ``n`` to open this section if you do not find it (with the mouse in the 3D viewport).
| Then simply use the ``import`` button as shown here:

.. important:: 
    For large meshes (> 100k vertices) or results from 3D simulations, this operation can take several seconds to complete.

.. image:: /images/telemac/import_file.png
    :width: 35%
    :alt: Import an TELEMAC file (button)
    :align: center

|

.. _telemac_previewing_tools:

Previewing tools
################

| Once you have imported a file, you should see the mesh in the viewport.
  You can select the ``TBB_TELEMAC_preview_...`` object and hit ``.`` on your numpad to center the view on it.

.. image:: /images/telemac/preview_panel.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Reload**: reloads the selected file (`when something went wrong or temporary data is not available anymore`)
* **Time step**: time step to preview
* **Points**: point data to preview as vertex colors (`switch to material preview to see it`)
* **Normalize**: option to normalize vertices coordinates (remap values in [-1;1])
* **Preview**: preview the mesh with the selected parameters

.. _telemac_create_sequence:

Create a sequence
#################

| You can create sequences to automatically switch between time steps using the timeline.

Mesh sequence
-------------

| TODO

.. image:: /images/telemac/create_mesh_sequence.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Start**: starting point of the sequence (time step)
* **End**: ending point of the sequence (time step)
* **Import point data**: flag to indicate that it must import some point data as vertex colors
* **List**: list of point data to import (separate each with a ``;``)
* **Normalize**: option to normalize vertices coordinates (remap values in [-1;1])
* **Name**: name of the sequence

Streaming sequence
------------------

| TODO

.. image:: /images/telemac/create_streaming_sequence.png
    :width: 35%
    :alt: Preview panel
    :align: center

|

* **Frame start**: starting point of the sequence (frame)
* **Length**: length of the animation (time steps)
* **Import point data**: flag to indicate that it must import some point data as vertex colors
* **List**: list of point data to import (separate each with a ``;``)
* **Normalize**: option to normalize vertices coordinates (remap values in [-1;1])
* **Name**: name of the sequence