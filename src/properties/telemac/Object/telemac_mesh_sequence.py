# <pep8 compliant>
from bpy.props import StringProperty, BoolProperty
from bpy.types import PropertyGroup

from src.properties.telemac.temporary_data import TBB_TelemacTemporaryData


class TBB_TelemacMeshSequenceProperty(PropertyGroup):
    """
    'Mesh sequence' settings for the TELEMAC module.
    """
    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.StringProperty: File to read when updating the sequence.
    file_path: StringProperty(
        name="File path",
        description="File to read when updating the sequence",
        default="",
    )

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

    #: bpy.props.BoolProperty: Indicate whether this mesh sequence is from a 3D simulation or not.
    is_3d_simulation: BoolProperty(
        name="Is 3D simulation",
        description="Indicate whether this mesh sequence is from a 3D simulation or not",
        default=False
    )

    tmp_data = TBB_TelemacTemporaryData()
