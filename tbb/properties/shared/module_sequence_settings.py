# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, StringProperty

import json


class TBB_ModuleSequenceSettings(PropertyGroup):
    """
    Module sequence properties.

    This data structure holds common data used in both OpenFOAM and TELEMAC modules.
    """

    register_cls = True
    is_custom_base_cls = True

    #: bpy.props.StringProperty: Name of the sequence.
    name: StringProperty(
        name="Name",  # noqa: F821
        description="Name of the sequence",
        default="",
    )

    #: bpy.props.StringProperty: File to read when updating the sequence.
    file_path: StringProperty(
        name="File path",
        description="File to read when updating the sequence",
        default="",
    )

    #: bpy.props.BoolProperty: Import point data as vertex color groups.
    import_point_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False,
    )

    #: bpy.props.StringProperty: List of point data to import as vertex color groups. Separate each with a semicolon.
    point_data: StringProperty(
        name="Point data",
        description="List of point data to import as vertex color groups. Separate each with a semicolon",
        default=json.dumps({"names": [], "units": [], "ranges": [], "types": [], "dimensions": []}),  # noqa F821
    )
