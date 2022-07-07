.. _telemac_interpolation:

Interpolation
=============

Mesh sequence
-------------

| The use of shape keys lets you to interpolate the animation of the mesh.

.. important::
    Vertex colors are linearly interpolated using the defined shape keys.

| Here is how you can do it:

    * Select meshes you want to interpolate in the sequence object

        .. image:: /images/telemac/interpolation/tuto_interpolate_1.png
            :width: 85%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * Place the time cursor where you want to "center" the Interpolation

        .. image:: /images/telemac/interpolation/tuto_interpolate_2.png
            :width: 85%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * Then, hit ``s`` and scale the interpolation moving the mouse

        .. image:: /images/telemac/interpolation/tuto_interpolate_3.png
            :width: 85%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * Once you are satisfied, press the ``left mouse button``

| You can change the type of the interpolation in the ``Graph editor``:

    * With meshes selected, open the graph editor

        .. image:: /images/telemac/interpolation/tuto_interpolate_4.png
            :width: 85%
            :alt: Preview panel
            :align: center
            :class: rounded-corners


    * Select the keyframes you want to edit
    * Press the ``right mouse button`` in the editor and choose a new interpolation mode

        .. image:: /images/telemac/interpolation/tuto_interpolate_5.png
            :width: 85%
            :alt: Preview panel
            :align: center
            :class: rounded-corners


    * It's done!

        .. image:: /images/telemac/interpolation/tuto_interpolate_6.png
            :width: 85%
            :alt: Preview panel
            :align: center
            :class: rounded-corners


Streaming sequence
------------------

| A streaming sequence does not use shape keys, so we can't use the same method as for mesh sequences.
  However, you can still interpolate the animation of the mesh using our custom tool:

    .. important::
        Vertex colors are interpolated using the same settings.


    * In the streaming sequence settings panel, select an interpolation method.

        .. image:: /images/telemac/interpolation/tuto_interpolate_streaming_1.png
            :width: 60%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * Then, indicate the number of time steps to add between each time point.

        .. image:: /images/telemac/interpolation/tuto_interpolate_streaming_2.png
            :width: 60%
            :alt: Preview panel
            :align: center
            :class: rounded-corners

    * You're done! Interpolated points should now be generated on the fly, when changing frame in the timeline.