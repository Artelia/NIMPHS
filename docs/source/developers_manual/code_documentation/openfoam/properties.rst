Properties
==========

* :ref:`openfoam_properties_other`
* :ref:`openfoam_properties_scene`
* :ref:`openfoam_properties_object`
* :ref:`openfoam_properties_utils`

.. _openfoam_properties_other:

Other
#####

Temporary data
--------------

.. autoclass:: src.properties.openfoam.temporary_data.TBB_OpenfoamTemporaryData
   :members:
   :show-inheritance:

Clip
----

.. autoclass:: src.properties.openfoam.clip.TBB_OpenfoamClipProperty
   :members:
   :show-inheritance:

.. autoclass:: src.properties.openfoam.clip.TBB_OpenfoamClipScalarProperty
   :members:
   :show-inheritance:

| More information on TBB_OpenfoamClipProperty members:

* **value_ranges**

    .. code-block:: text
        
        Value ranges are stored as follows:
        "name_of_scalar@value/min/max;name_of_other_scalar@vector_value_dimension/min.x/max.x/min.y/max.y/min.z/min.z/etc..."
        Example:
        "U@vector_value_3/0.0/1.0/-1.0/2.0/2.5/3.5;alpha.water@value/0.0/1.0"

* **list**

    .. code-block:: text
        
        List of point data are stored as follows:
        "name_of_scalar@value;name_of_other_scalar@vector_value;etc..."
        Example:
        "U@vector_value;alpha.water@value"

.. _openfoam_properties_scene:

Scene
#####

.. autoclass:: src.properties.openfoam.Scene.openfoam_settings.TBB_OpenfoamSettings
   :members:
   :show-inheritance:

.. _openfoam_properties_object:

Object
######

.. autoclass:: src.properties.openfoam.Object.openfoam_streaming_sequence.TBB_OpenfoamStreamingSequenceProperty
   :members:
   :show-inheritance:

.. _openfoam_properties_utils:

Utils
#####

.. automodule:: src.properties.openfoam.utils
   :members: