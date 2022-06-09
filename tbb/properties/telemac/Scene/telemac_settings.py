# <pep8 compliant>
from bpy.props import BoolProperty, EnumProperty, FloatVectorProperty

from tbb.properties.telemac.utils import update_var_names
from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from tbb.properties.shared.module_scene_settings import TBB_ModuleSceneSettings


class TBB_TelemacSettings(TBB_ModuleSceneSettings):
    """TELEMAC module settings."""

    register_cls = True
    is_custom_base_cls = False

    #: TBB_TelemacTemporaryData: temporary data
    tmp_data = TBB_TelemacTemporaryData()

    #: bpy.types.EnumProperty: Name of point data to preview
    preview_point_data: EnumProperty(
        items=update_var_names,
        name="Point data",
        description="Name of point data to preview",
    )

    #: bpy.types.EnumProperty: Select a sequence type
    sequence_type: EnumProperty(
        items=[
            ("mesh_sequence", "Mesh sequence", "Make a sequence by adding shape keys for each time step\
             (good option for small meshes)"),  # noqa: F821
            ("streaming_sequence", "Streaming sequence", "TODO (good option for large meshes)"),  # noqa: F821
        ],
        name="Sequence type",
        description="Select a sequence type",
    )

    #: bpy.types.FloatVectorProperty: Hold original dimensions of the mesh
    preview_obj_dimensions: FloatVectorProperty(
        name="Preview object dimensions",
        description="Dimensions of the preview object",
        default=(1.0, 1.0, 1.0),
    )

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize_preview_obj: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize_sequence_obj: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )