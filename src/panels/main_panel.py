from bpy.types import Panel, Scene
from bpy.props import PointerProperty
from ..properties.settings import TBB_settings
from bpy.props import StringProperty, FloatProperty, BoolProperty

class TBB_PT_MainPanel(Panel):
    bl_label = "Toolsbox blender"
    bl_idname = "TBB_PT_MainPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toolsbox blender"

    file_name = ""

    def draw(self, context):
        layout = self.layout
        # settings = context.scene.tbb_settings[0]

        row = layout.row()
        row.label(text="Import")
        
        # Import section
        row = layout.row()
        if self.file_name != "":
            box = row.box()
            box.label(text="File: " + self.file_name)
            row.operator("tbb.import_foam_file", text="", icon="IMPORT")
        else:
            row.operator("tbb.import_foam_file", text="Import OpenFoam file", icon="IMPORT")
            

