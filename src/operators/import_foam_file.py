import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty

from pyvista import OpenFOAMReader
from pathlib import Path

class TBB_OT_ImportFoamFile(Operator, ImportHelper):
    bl_idname="tbb.import_foam_file"
    bl_label="Import"
    bl_description="Import an OpenFoam file"

    filter_glob: StringProperty(
        default="*.foam", # multiple allowed types: "*.foam;*.[];*.[]" etc ...
        options={"HIDDEN"}
    )

    def execute(self, context):
        # If the settings properties have not been created yet
        settings = None
        try:
            settings = context.scene.tbb_settings[0]
        except IndexError as error:
            settings = context.scene.tbb_settings.add()

        file_path = Path(self.filepath)
        if not file_path.exists():
            self.report({"ERROR"}, "The choosen file does not exist")
            return {"FINISHED"}

        settings.file_path = self.filepath
        
        # TODO: does this line can throw an exception?
        bpy.types.TBB_PT_MainPanel.file_reader = OpenFOAMReader(self.filepath)

        # Forces to redraw the view (magic trick)
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        return {"FINISHED"}

class TBB_OT_ReloadFoamFile(Operator):
    bl_idname="tbb.reload_foam_file"
    bl_label="Reload"
    bl_description="Reload the selected file"

    def execute(self, context):
        settings = None
        try:
            settings = context.scene.tbb_settings[0]
        except IndexError as error:
            # This error means that the settings have not been created yet.
            # It can be resolved by importing a new file.
            self.report({"ERROR"}, "Please import a file first")
            return {"FINISHED"}

        # TODO: does this line can throw an exception?
        bpy.types.TBB_PT_MainPanel.file_reader = OpenFOAMReader(settings.file_path)

        return {"FINISHED"}