# <pep8 compliant>
from bpy.types import Event, Context, Object, RenderSettings
from bpy.props import StringProperty, IntProperty, EnumProperty

import logging

from tbb.properties.openfoam.temporary_data import TBB_OpenfoamTemporaryData
from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData

log = logging.getLogger(__name__)

from tbb.operators.shared.create_sequence import TBB_CreateSequence


class TBB_CreateStreamingSequence(TBB_CreateSequence):
    """Operator to create 'streaming sequences'."""

    register_cls = False
    is_custom_base_cls = True

    #: bpy.props.IntProperty: Starting point of the sequence.
    start: IntProperty(
        name="Start",  # noqa F821
        description="Starting point of the sequence",
        default=0,
    )

    #: bpy.props.IntProperty: Length of the sequence.
    length: IntProperty(
        name="End",  # noqa F821
        description="Length of the sequence",
        default=1,
    )

    #: bpy.props.IntProperty: Maximum length of the sequence.
    max_length: IntProperty(
        name="Max length",  # noqa F821
        description="Maximum length of the sequence",
        default=1,
        options={'HIDDEN'},  # noqa F821
    )

    #: bpy.props.StringProperty: Name to give to the generated sequence object.
    name: StringProperty(
        name="Name",  # noqa F821
        description="Name to give to the generated sequence object",
        default="Mesh",  # noqa F821
    )

    #: bpy.props.EnumProperty: Indicates which module to use. Enum in ['OpenFOAM', 'TELEMAC'].
    module: EnumProperty(
        name="Mode",  # noqa: F821
        description="Indicates whether the operator should run modal or not. Enum in ['OpenFOAM', 'TELEMAC']",
        items=[
            ('OpenFOAM', "OpenFOAM", "Use OpenFOAM module"),  # noqa: F821
            ('TELEMAC', "TELEMAC", "Use TELEMAC module"),  # noqa: F821
        ],
        options={'HIDDEN'},  # noqa F821
    )

    def invoke(self, context: Context, event: Event) -> set:
        """
        Prepare operators settings. Function triggered before the user can edit settings.

        Args:
            context (Context): context
            event (Event): event

        Returns:
            set: state of the operator
        """

        return {'RUNNING_MODAL'}

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            context (Context): context
        """

        # Disable point data
        # super().draw(context)

        layout = self.layout

        # Sequence settings
        box = layout.box()
        box.label(text="Sequence")
        row = box.row()
        row.prop(self, "start", text="Start")
        row = box.row()
        row.prop(self, "length", text="Length")
        row = box.row()
        row.prop(self, "name", text="Name")

    def execute(self, context: Context, obj: Object) -> set:
        """
        Create the 'streaming sequence' object.

        Args:
            context (Context): context
            obj (Object): sequence object

        Returns:
            set: state of the operator
        """
        from tbb.operators.utils import setup_streaming_sequence_object
        from tbb.operators.openfoam.utils import load_openfoam_file

        # Setup streaming sequence object
        setup_streaming_sequence_object(obj, self, self.obj.tbb.settings.file_path)
        context.scene.collection.objects.link(obj)

        # Create temporary data
        if self.module == 'OpenFOAM':
            success, file_reader = load_openfoam_file(obj.tbb.settings.file_path)
            if not success:
                log.error(f"Unable to open file {obj.tbb.settings.file_path}", exc_info=1)
                return {'CANCELLED'}
            context.scene.tbb.tmp_data[obj.tbb.uid] = TBB_OpenfoamTemporaryData(file_reader)
        if self.module == 'TELEMAC':
            context.scene.tbb.tmp_data[obj.tbb.uid] = TBB_TelemacTemporaryData()

        # As mentioned here, lock the interface because the custom handler will alter data on frame change
        # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
        RenderSettings.use_lock_interface = True

        self.report({'INFO'}, "Sequence successfully created")
        return {'FINISHED'}
