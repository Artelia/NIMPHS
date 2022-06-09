TELEMAC
=======

* :ref:`telemac_import_file`
* :ref:`telemac_previewing_tools`
* :ref:`telemac_create_sequence`

.. important::
    Useful information are printed in the console (times, errors, warnings, etc).
    Do not hesitate to open it. On Windows, ``Window ‣ Toggle System Console``.


.. _telemac_import_file:

Import a file
#############

| You will find the main panel in the 3D viewport, under the panels section (on the right).
| Hit ``n`` to open this section if you do not find it (with the mouse in the 3D viewport).
| Then simply use the ``import`` button as shown here:

.. important:: 
    For large meshes (> 100k vertices) or results from 3D simulations, this operation can take several seconds to complete.

.. image:: /images/telemac/import_file.png
    :width: 45%
    :alt: Import an TELEMAC file (button)
    :align: center

|

.. _telemac_previewing_tools:

Previewing tools
################

| Once you have imported a file, you should see the mesh in the viewport.
  You can select the ``TBB_TELEMAC_preview_...`` object and hit ``.`` on your numpad to center the view on it.

.. image:: /images/telemac/preview_panel.png
    :width: 45%
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

| This type of sequence uses shape keys to update the mesh. So it holds every time steps in memory.
| That is why it is not recommended to use this sequence for long sequences.

.. image:: /images/telemac/create_mesh_sequence.png
    :width: 45%
    :alt: Preview panel
    :align: center

|

* **Start**: starting point of the sequence (time step)
* **End**: ending point of the sequence (time step)
* **Import point data**: flag to indicate that it must import some point data as vertex colors
* **List**: list of point data to import (separate each with a ``;``)
* **Normalize**: option to normalize vertices coordinates (remap values in [-1;1])
* **Name**: name of the sequence

Interpolation
*************

| The use of shape keys lets you to interpolate the animation of the mesh.

.. important::
    Vertex colors are linearly interpolated using the defined shape keys.

| Here is how you can do it:

    * Select meshes you want to interpolate in the sequence object

        .. image:: /images/telemac/tuto_interpolate_1.png
            :width: 85%
            :alt: Preview panel
            :align: center

    * Place the time cursor where you want to "center" the Interpolation

        .. image:: /images/telemac/tuto_interpolate_2.png
            :width: 85%
            :alt: Preview panel
            :align: center

    * Then, hit `s` and scale the interpolation moving the mouse

        .. image:: /images/telemac/tuto_interpolate_3.png
            :width: 85%
            :alt: Preview panel
            :align: center

    * Once you are satisfied, press the `left mouse button`

| You can change the type of the interpolation in the `Graph editor`:

    * With meshes selected, open the graph editor

        .. image:: /images/telemac/tuto_interpolate_4.png
            :width: 85%
            :alt: Preview panel
            :align: center


    * Select the keyframes you want to edit
    * Press the `right mouse button` in the editor and choose a new interpolation mode

        .. image:: /images/telemac/tuto_interpolate_5.png
            :width: 85%
            :alt: Preview panel
            :align: center


    * It's done!

        .. image:: /images/telemac/tuto_interpolate_6.png
            :width: 85%
            :alt: Preview panel
            :align: center

Edit mesh sequences settings
****************************

| You can edit mesh sequences settings in the `Object properties` panel.

.. image:: /images/telemac/edit_mesh_sequence.png
    :width: 45%
    :alt: Preview panel
    :align: center

|

* **Import point data**: flag to indicate that it must import some point data as vertex colors.
* **List**: list of point data to import (separate each with a ``;``).


Streaming sequence
------------------

| This type of sequence holds only one time step in memory. It is recommended to use for long sequences.
| The mesh automatically updates when the frame changes.

.. image:: /images/telemac/create_streaming_sequence.png
    :width: 45%
    :alt: Preview panel
    :align: center

|

* **Frame start**: starting point of the sequence (frame).
* **Length**: length of the animation (time steps).
* **Import point data**: flag to indicate that it must import some point data as vertex colors.
* **List**: list of point data to import (separate each with a ``;``).
* **Normalize**: option to normalize vertices coordinates (remap values in [-1;1]).
* **Name**: name of the sequence.

.. _telemac_streaming_sequence_interpolation:

Interpolation
*************

| A streaming sequence does not use shape keys, so we can't use the same method as for mesh sequences.
| However, you can still interpolate the animation of the mesh using our custom tool:

    .. important::
        Vertex colors are interpolated using the same settings.


    * In the streaming sequence settings panel, select an interpolation method.

        .. image:: /images/telemac/tuto_interpolate_streaming_1.png
            :width: 45%
            :alt: Preview panel
            :align: center

    * Then, indicate the number of time steps to add between each time point.

        .. image:: /images/telemac/tuto_interpolate_streaming_2.png
            :width: 45%
            :alt: Preview panel
            :align: center


Edit streaming sequences settings
*********************************

| You can edit streaming sequences settings in the `Object properties` panel.

.. image:: /images/telemac/edit_streaming_sequence.png
    :width: 45%
    :alt: Preview panel
    :align: center

|

* **Update**: update this sequence whenever the frame changes.
* **Frame start**: starting point of the sequence (frame).
* **Length**: length of the animation (time steps).
* **Shade smooth**: whether to use smooth shading or not (flat shading).
* **Import point data**: import point data as vertex color groups.
* **List**: list of point data to import (separate each with a ``;``).
* **Normalize**: option to normalize vertices coordinates (remap values in [-1;1]).
* **Interpolate**: see :ref:`telemac_streaming_sequence_interpolation`