# <pep8 compliant>
from bpy.types import Panel


class TBB_PT_OpenfoamSequenceSettings(Panel):
    bl_label = "OpenFOAM Streaming sequence"
    bl_idname = "TBB_PT_OpenfoamSequenceSettings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj.tbb_openfoam_sequence.is_streaming_sequence

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        settings = obj.tbb_openfoam_sequence

        row = layout.row()
        row.prop(settings, "update", text="Update")
        if settings.update:
            row = layout.row()
            row.prop(settings, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(settings, "anim_length", text="Length")

            row = layout.row()
            row.prop(settings, "import_point_data", text="Import point data")

            if settings.import_point_data:
                row = layout.row()
                row.prop(settings, "list_point_data", text="List")
