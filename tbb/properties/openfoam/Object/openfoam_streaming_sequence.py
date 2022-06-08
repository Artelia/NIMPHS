# <pep8 compliant>
from bpy.props import PointerProperty, BoolProperty, EnumProperty

from tbb.properties.openfoam.openfoam_clip import TBB_OpenfoamClipProperty
from tbb.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings


class TBB_OpenfoamStreamingSequenceProperty(TBB_ModuleStreamingSequenceSettings):
    """'Streaming sequence' settings for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.types.BoolProperty: If `True`, decompose polyhedra into tetrahedra and pyramids
    decompose_polyhedra: BoolProperty(
        name="Decompose polyhedra",
        description="Whether polyhedra are to be decomposed when read. If True,\
                     decompose polyhedra into tetrahedra and pyramids",
        default=False
    )

    #: bpy.types.BoolProperty: If `True`, more complex polygons will be broken down into triangles
    triangulate: BoolProperty(
        name="Triangulate",  # noqa: F821
        description="More complex polygons will be broken down into triangles",
        default=True
    )

    #: bpy.types.EnumProperty: The property indicates whether decomposed mesh or reconstructed mesh should be read
    case_type: EnumProperty(
        name="Case type",
        description="The property indicates whether decomposed mesh or reconstructed mesh should be read",
        items=[
            ("reconstructed", "Reconstructed", "Reconstructed mesh should be read"),  # noqa: F821
            ("decomposed", "Decomposed", "Decomposed mesh should be read"),  # noqa: F821
        ]
    )

    #: TBB_OpenfoamClipProperty: Clip settings of the sequence.
    clip: PointerProperty(type=TBB_OpenfoamClipProperty)
