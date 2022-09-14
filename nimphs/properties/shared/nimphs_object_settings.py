# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, EnumProperty, IntProperty

from nimphs.properties.shared.point_data_settings import NIMPHS_PointDataSettings
from nimphs.properties.telemac.telemac_object_settings import NIMPHS_TelemacObjectSettings
from nimphs.properties.openfoam.openfoam_object_settings import NIMPHS_OpenfoamObjectSettings
from nimphs.properties.utils.properties import update_preview_time_point, available_point_data


class NIMPHS_ObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for all modules."""

    register_cls = True
    is_custom_base_cls = False

    #: bpy.props.EnumProperty: Time step to preview.
    preview_time_point: IntProperty(
        name="Preview time point",
        description="Time step to preview",
        default=0,
        soft_min=0,
        soft_max=1000,
        update=update_preview_time_point,
    )

    #: bpy.props.EnumProperty: Name of point data to preview.
    preview_point_data: EnumProperty(
        items=available_point_data,
        name="Point data",
        description="Name of point data to preview",
    )

    #: bpy.props.StringProperty: File to read to access data.
    file_path: StringProperty(
        name="File path",
        description="File to read to access data",
        default="",
    )

    #: NIMPHS_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=NIMPHS_PointDataSettings)

    #: NIMPHS_OpenfoamObjectSettings: OpenFOAM object properties
    openfoam: PointerProperty(type=NIMPHS_OpenfoamObjectSettings)

    #: NIMPHS_TelemacObjectSettings: TELEMAC object properties
    telemac: PointerProperty(type=NIMPHS_TelemacObjectSettings)
