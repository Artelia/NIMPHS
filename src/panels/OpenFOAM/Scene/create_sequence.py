# <pep8 compliant>
from bpy.types import Panel

from ..utils import sequence_name_already_exist


class TBB_PT_OpenFOAMCreateSequence(Panel):
    bl_label = "Create sequence"
    bl_idname = "TBB_PT_OpenFOAMCreateSequence"
    bl_parent_id = "TBB_PT_OpenFOAMMainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        # Even if no objects are selected, the last selected object remains in the active_objects variable
        if len(context.selected_objects) == 0:
            obj = None

        if obj is None:
            return context.scene.tbb_tmp_data.is_ok()
        else:
            return context.scene.tbb_tmp_data.is_ok() and not obj.tbb_openfoam_sequence.is_on_frame_change_sequence

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tbb_openfoam_settings

        # Check if we need to lock the ui
        enable_rows = not settings.create_sequence_is_running
        snae = sequence_name_already_exist(settings.sequence_name)  # snae = sequence_name_already_exist

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_name", text="Name")
        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "sequence_type", text="Type")

        if settings.sequence_type == "mesh_sequence":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["start_time"]', text="Start")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["end_time"]', text="End")
        elif settings.sequence_type == "on_frame_change":
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["frame_start"]', text="Frame start")
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, '["anim_length"]', text="Length")
        else:
            row = layout.row()
            row.label(text="Error: unknown sequence type...", icon="ERROR")

        row = layout.row()
        row.enabled = enable_rows
        row.prop(settings, "import_point_data")

        if settings.import_point_data:
            row = layout.row()
            row.enabled = enable_rows
            row.prop(settings, "list_point_data", text="List")

        row = layout.row()
        row.enabled = not snae
        row.operator("tbb.create_sequence", text="Create sequence", icon="RENDER_ANIMATION")

        # Lock the create_sequence operator if the sequence name is already taken
        if snae:
            row = layout.row()
            row.label(text="Sequence name already taken.", icon="ERROR")
