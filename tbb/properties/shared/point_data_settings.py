# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty

from tbb.properties.utils import VariablesInformation


class TBB_PointDataSettings(PropertyGroup):
    """Holds data for point data management in all modules."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.BoolProperty: Import point data as vertex color groups.
    import_data: BoolProperty(
        name="Import point data",
        description="Import point data as vertex color groups",
        default=False,
    )

    #: bpy.props.StringProperty: List of point data to import as vertex color groups.
    list: StringProperty(
        name="Point data",
        description="List of point data to import as vertex color groups.",
        default=VariablesInformation().dumps(),  # noqa F821
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
