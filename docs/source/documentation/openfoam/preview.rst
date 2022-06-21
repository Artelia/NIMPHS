.. _openfoam_previewing_tools:

Previewing tools
================

| Once you have imported a file, you should see the mesh in the viewport.
  You can select the imported object and hit ``.`` on your numpad to center the view on it.

.. note:: 
    Hit ``n`` to open the sidebar if you do not find it (with mouse focus in the 3D viewport).

.. image:: /images/openfoam/preview.png
    :width: 75%
    :alt: Preview panel
    :align: center

|

.. important:: 
    If you change a parameter, you have to click on the `preview` button to update the mesh.

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

Preview
*******

* **Points**: point data to preview as vertex colors (`switch to material preview to see it`).
* **Time step**: time step to preview.
* **Preview**: preview the mesh with the selected parameters.