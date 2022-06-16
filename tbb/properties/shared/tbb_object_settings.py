# <pep8 compliant>
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, EnumProperty, IntProperty

from tbb.properties.shared.point_data_settings import TBB_PointDataSettings

from tbb.properties.telemac.Object.telemac_object_settings import TBB_TelemacObjectSettings
from tbb.properties.openfoam.Object.openfoam_object_settings import TBB_OpenfoamObjectSettings
from tbb.properties.utils import update_preview_time_point, available_point_data


class TBB_ObjectSettings(PropertyGroup):
    """Data structure which holds object related settings for all the modules."""

    register_cls = True
    is_custom_base_cls = False

    #: TBB_OpenfoamObjectSettings: OpenFOAM object properties
    openfoam: PointerProperty(type=TBB_OpenfoamObjectSettings)

    #: TBB_TelemacObjectSettings: TELEMAC object properties
    telemac: PointerProperty(type=TBB_TelemacObjectSettings)

    #: bpy.props.StringProperty: Name of the object.
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

    #: TBB_PointDataSettings: Point data settings.
    point_data: PointerProperty(type=TBB_PointDataSettings)

    #: bpy.props.EnumProperty: Name of point data to preview.
    preview_point_data: EnumProperty(
        items=available_point_data,
        name="Point data",
        description="Name of point data to preview",
    )

    #: bpy.props.EnumProperty: Time step to preview.
    preview_time_point: IntProperty(
        name="Preview time point",
        description="Time point to preview",
        default=0,
        soft_min=0,
        soft_max=1000,
        update=update_preview_time_point,
    )
