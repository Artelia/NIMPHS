# <pep8 compliant>
from bpy.props import EnumProperty
from bpy.types import Context, Event, Operator

import time

from tbb.operators.shared.create_sequence import TBB_CreateSequence
from tbb.operators.openfoam.utils import run_one_step_create_mesh_sequence_openfoam


class TBB_OT_OpenfoamCreateStreamingSequence(TBB_CreateSequence):
    """Create an OpenFOAM sequence using the settings defined in the\
    main panel of the module and the 'create sequence' panel."""

    register_cls = False
    is_custom_base_cls = False

    bl_idname = "tbb.openfoam_create_sequence"
    bl_label = "Create sequence"
    bl_description = "Create a sequence using the selected parameters. Press 'esc' to cancel"

    sequence_type: EnumProperty(
        name="Sequence type",
        description="Select a sequence type",
        items=[
            ("mesh_sequence", "Mesh sequence", "Make a sequence by creating a mesh for each time step\
             (good option for small meshes)"),  # noqa: F821
            ("streaming_sequence", "Streaming sequence", "Make a sequence by changing the mesh on each\
             frame change (it only keeps the last created mesh, good option for large meshes)"),  # noqa: F821
        ],
    )

    def invoke(self, context: Context, event: Event) -> set:
        pass
