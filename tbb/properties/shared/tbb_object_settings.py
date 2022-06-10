# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, BoolProperty, EnumProperty

import json

from tbb.properties.telemac.Object.telemac_object_settings import TBB_TelemacObjectSettings
from tbb.properties.openfoam.Object.openfoam_object_settings import TBB_OpenfoamObjectSettings


class TBB_ObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for all the modules."""

    register_cls = True
    is_custom_base_cls = False

    #: TBB_OpenfoamObjectSettings: OpenFOAM object properties
    openfoam: PointerProperty(type=TBB_OpenfoamObjectSettings)

    #: TBB_TelemacObjectSettings: TELEMAC object properties
    telemac: PointerProperty(type=TBB_TelemacObjectSettings)

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

    #: bpy.props.EnumProperty: Indicate whether point data should be remapped using local or global value ranges.
    remap_method: EnumProperty(
        name="Remap method",
        description="Remapping method for point data",
        items=[
            ("LOCAL", "Local", "Remap point data using a local value range"),  # noqa F821
            ("GLOBAL", "Global", "Remap point data using a global value range (can take several seconds to compute)"),  # noqa F821
        ]
    )
