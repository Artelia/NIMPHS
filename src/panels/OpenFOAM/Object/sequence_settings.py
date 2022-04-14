# <pep8 compliant>
from bpy.types import Panel


class TBB_PT_OpenFOAMSequenceSettings(Panel):
    bl_label = "OpenFOAM sequence settings"
    bl_idname = "TBB_PT_OpenFOAMSequenceSettings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(self, context):
        obj = context.active_object
        return obj.tbb_openfoam_sequence.is_on_frame_change_sequence

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        tbb_openfoam_sequence = obj.tbb_openfoam_sequence

        row = layout.row()
        row.prop(tbb_openfoam_sequence, "update_on_frame_change", text="Update")
        if tbb_openfoam_sequence.update_on_frame_change:
            row = layout.row()
            row.prop(tbb_openfoam_sequence, "frame_start", text="Frame start")
            row = layout.row()
            row.prop(tbb_openfoam_sequence, "anim_length", text="Length")

            row = layout.row()
            row.prop(tbb_openfoam_sequence, "import_point_data", text="Import point data")

            if tbb_openfoam_sequence.import_point_data:
                row = layout.row()
                row.prop(tbb_openfoam_sequence, "list_point_data", text="List")
