import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

class TBB_OT_ImportFoamFile(Operator, ImportHelper):
    bl_idname="tbb.import_foam_file"
    bl_label="Import"
    bl_description="Import the selected .foam file"

    filter_glob: StringProperty(
        default="*.foam", # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context):
        # If the settings properties have not been created yet
        if len(context.scene.tbb_settings) <= 0:
            context.scene.tbb_settings.add()
        settings = context.scene.tbb_settings[0]
        
        settings.file_path = self.filepath
        bpy.types.TBB_PT_MainPanel.file_name = self.filepath

        # Forces to redraw the view (magic trick)
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        return {"FINISHED"}