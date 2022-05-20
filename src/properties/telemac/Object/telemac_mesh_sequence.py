# <pep8 compliant>
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup


class TBB_TelemacMeshSequenceProperty(PropertyGroup):
    """
    'Mesh sequence' settings for the TELEMAC module.
    """
    register_cls = True
    is_custom_base_cls = False

    #: bpy.types.BoolProperty: Import point data as vertex color groups
    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False,
    )

    #: bpy.props.StringProperty: List of point data to import as vertex color groups. Separate each with a semicolon.
    list_point_data: StringProperty(
        name="Point data list",
        description="List of point data to import as vertex color groups. Separate each with a semicolon",
        default="",
    )

    is_3d_simulation: BoolProperty(
        name="Is 3D simulation",
        description="Indicate whether this mesh sequence is from a 3D simulation or not",
        default=False
    )
