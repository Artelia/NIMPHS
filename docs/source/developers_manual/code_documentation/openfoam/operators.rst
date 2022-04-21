Operators
=========

* :ref:`openfoam_operators_scene`
* :ref:`openfoam_operators_utils`

.. _openfoam_operators_scene:

Scene
#####

.. autoclass:: src.operators.openfoam.Scene.create_sequence.TBB_OT_OpenfoamCreateSequence
   :members:
   :show-inheritance:

.. autoclass:: src.operators.openfoam.Scene.import_file.TBB_OT_OpenfoamImportFile
   :members:
   :show-inheritance:

.. autoclass:: src.operators.openfoam.Scene.preview.TBB_OT_OpenfoamPreview
   :members:
   :show-inheritance:

.. autoclass:: src.operators.openfoam.Scene.reload_file.TBB_OT_OpenfoamReloadFile
   :members:
   :show-inheritance:

.. _openfoam_operators_utils:

Utils
#####

.. currentmodule:: src.operators.openfoam.utils

.. autofunction:: load_openfoam_file

.. autofunction:: generate_sequence_object

.. autofunction:: generate_mesh

.. autofunction:: generate_preview_object

.. autofunction:: generate_preview_material

.. autofunction:: generate_mesh_for_sequence

.. autofunction:: generate_vertex_colors

.. autofunction:: add_mesh_to_sequence

.. autofunction:: update_streaming_sequence

.. autofunction:: update_sequence_mesh

.. autofunction:: update_settings_dynamic_props

.. autofunction:: remap_array