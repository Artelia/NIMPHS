# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, EnumProperty


class NIMPHS_OpenfoamImportSettings(PropertyGroup):
    """Import settings for the OpenFOAM module."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.BoolProperty: If `True`, decompose polyhedra into tetrahedra and pyramids
    decompose_polyhedra: BoolProperty(
        name="Decompose polyhedra",
        description="Indicate whether polyhedra are to be decomposed when read. If True, \
decompose polyhedra into tetrahedra and pyramids",
        default=True
    )

    #: bpy.props.EnumProperty: Indicate whether decomposed mesh or reconstructed mesh should be read
    case_type: EnumProperty(
        name="Case type",
        description="Indicate whether decomposed mesh or reconstructed mesh should be read",
        items=[
            ("reconstructed", "Reconstructed", "Reconstructed mesh should be read"),  # noqa: F821
            ("decomposed", "Decomposed", "Decomposed mesh should be read"),  # noqa: F821
        ]
    )

    #: bpy.props.BoolProperty: If `True`, skip the '/0' time folder.
    skip_zero_time: BoolProperty(
        name="Skip zero time",  # noqa: F821
        description="If True, skip the '/0' time folder",
        default=True
    )

    #: bpy.props.BoolProperty: If `True`, more complex polygons will be broken down into triangles
    triangulate: BoolProperty(
        name="Triangulate",  # noqa: F821
        description="More complex polygons will be broken down into triangles",
        default=True
    )
