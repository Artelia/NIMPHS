# <pep8 compliant>
from bpy.props import BoolProperty, IntProperty
from bpy.types import Event, Context, Object, RenderSettings

import logging
log = logging.getLogger(__name__)

from nimphs.operators.shared.create_sequence import NIMPHS_CreateSequence


class NIMPHS_CreateStreamingSequence(NIMPHS_CreateSequence):
    """Operator to create 'streaming sequence' objects."""

    register_cls = False
    is_custom_base_cls = True

    def update_length(self, _context: Context) -> None:  # noqa: D417
        """
        Make sure the user can't select a wrong value.

        Args:
            _context (Context): context
        """

        if self.length > self.max:
            self.length = self.max
        elif self.length < 0:
            self.length = 0

    #: bpy.props.IntProperty: Length of the sequence.
    length: IntProperty(
        name="End",  # noqa: F821
        description="Length of the sequence",
        default=1,
        update=update_length,
        soft_min=0,
        min=0
    )

    #: bpy.props.BoolProperty: Whether to use smooth shading or flat shading
    shade_smooth: BoolProperty(
        name="Shade smooth",
        description="Indicate whether to use smooth shading or flat shading",
        default=False
    )

    def invoke(self, _context: Context, _event: Event) -> set:
        """
        Prepare operators settings. Function triggered before the user can edit settings.

        Args:
            _context (Context): context
            _event (Event): event

        Returns:
            set: state of the operator
        """

        return {'RUNNING_MODAL'}

    def draw(self, _context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            _context (Context): context
        """

        # Disable point data
        # super().draw(context)

        # Sequence settings
        box = self.layout.box()
        box.label(text="Sequence")
        row = box.row()
        row.prop(self, "start", text="Start")
        row = box.row()
        row.prop(self, "length", text="Length")
        row = box.row()
        row.prop(self, "shade_smooth", text="Shade smooth")
        row = box.row()
        row.prop(self, "name", text="Name")

    def execute(self, context: Context, obj: Object, selected: Object) -> set:
        """
        Create the 'streaming sequence' object.

        Args:
            context (Context): context
            obj (Object): sequence object
            selected (Object): selected object

        Returns:
            set: state of the operator
        """

        from nimphs.operators.utils.object import ObjectUtils

        # Setup streaming sequence object
        ObjectUtils.setup_streaming_sequence(obj, self, selected.nimphs.settings.file_path)
        context.collection.objects.link(obj)

        # As mentioned here, lock the interface because the custom handler will alter data on frame change
        # https://docs.blender.org/api/current/bpy.app.handlers.html?highlight=app%20handlers#module-bpy.app.handlers
        RenderSettings.use_lock_interface = True

        # Reset operator variables information
        context.scene.nimphs.op_vars.clear()

        self.report({'INFO'}, "Sequence successfully created")
        return {'FINISHED'}
