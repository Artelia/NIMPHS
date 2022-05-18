# <pep8 compliant>
from bpy.props import BoolProperty, PointerProperty

from src.properties.shared.module_streaming_sequence_settings import TBB_ModuleStreamingSequenceSettings
from src.properties.telemac.telemac_interpolate import TBB_TelemacInterpolateProperty


class TBB_TelemacStreamingSequenceProperty(TBB_ModuleStreamingSequenceSettings):
    """
    'Streaming sequence' settings for the TELEMAC module.
    """
    register_cls = True
    is_custom_base_cls = False

    #: bpy.types.BoolProperty: Option to normalize vertices coordinates (remap values in [-1;1])
    normalize: BoolProperty(
        name="Normalize coordinates",
        description="Option to normalize vertices coordinates (remap values in [-1;1])",
        default=False
    )

    #: bpy.types.TBB_TelemacInterpolateProperty: Interpolation settings
    interpolate: PointerProperty(type=TBB_TelemacInterpolateProperty)