# <pep8 compliant>
from bpy.types import Context

from tbb.panels.utils import get_selected_object
from tbb.panels.openfoam.utils import draw_clip_settings
from tbb.panels.shared.streaming_sequence_settings import TBB_StreamingSequenceSettingsPanel


class TBB_PT_OpenfoamStreamingSequence(TBB_StreamingSequenceSettingsPanel):
    """Main panel of the OpenFOAM 'streaming sequence' settings."""

    register_cls = True
    is_custom_base_cls = False

    bl_label = "OpenFOAM Streaming sequence"
    bl_idname = "TBB_PT_OpenfoamStreamingSequence"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context: Context) -> bool:
        """
        If false, hides the panel.

        Args:
            context (Context): context

        Returns:
            bool: state
        """

        return super().poll(context, 'OpenFOAM')

    def draw(self, context: Context) -> None:
        """
        Layout of the panel.

        Args:
            context (Context): context
        """

        obj = get_selected_object(context)
        sequence = obj.tbb.settings.openfoam.s_sequence

        # Display file_path information
        box = self.layout.box()
        row = box.row()
        row.label(text=f"File: {obj.tbb.settings.file_path}")
        row.operator("tbb.edit_file_path", text="", icon="GREASEPENCIL")

        file_data = context.scene.tbb.file_data.get(obj.tbb.uid, None)

        # Check file data
        if file_data is None or not file_data.is_ok():
            row = self.layout.row()
            row.label(text="Reload data: ", icon='ERROR')
            row.operator("tbb.reload_openfoam_file", text="Reload", icon='FILE_REFRESH')
            return

        row = self.layout.row()
        row.prop(sequence, "update", text="Update")

        if sequence.update:
            # Import settings
            import_settings = obj.tbb.settings.openfoam.import_settings

            box = self.layout.box()
            row = box.row()
            row.label(text="Import")

            row = box.row()
            row.prop(import_settings, "decompose_polyhedra", text="Decompose polyhedra")
            row = box.row()
            row.prop(import_settings, "skip_zero_time", text="Skip zero time")
            row = box.row()
            row.prop(import_settings, "triangulate", text="Triangulate")
            row = box.row()
            row.prop(import_settings, "case_type", text="Case")

            # Clip settings
            draw_clip_settings(self.layout, obj.tbb.settings.openfoam.clip)

            # Point data and sequence settings
            super().draw(context, obj, sequence)