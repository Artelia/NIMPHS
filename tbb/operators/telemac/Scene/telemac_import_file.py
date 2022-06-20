# <pep8 compliant>
import bpy
from bpy.props import StringProperty, PointerProperty
from bpy.types import Operator, Context
from bpy_extras.io_utils import ImportHelper

import time
import logging
from pathlib import Path

from tbb.properties.telemac.temporary_data import TBB_TelemacTemporaryData
from tbb.properties.telemac.import_settings import TBB_TelemacImportSettings
log = logging.getLogger(__name__)

from tbb.operators.telemac.utils import generate_base_objects


def import_telemac_menu_draw(self, context: Context):  # noqa D417
    """
    Draw function which displays the import button in File > Import.

    Args:
        context (Context): context
    """

    prefs = context.preferences.addons["tbb"].preferences.settings
    extensions = prefs.telemac_extensions.replace("*", "")
    self.layout.operator(TBB_OT_TelemacImportFile.bl_idname, text=f"TELEMAC ({extensions})")


class TBB_OT_TelemacImportFile(Operator, ImportHelper):
    """Import a TELEMAC file. This operator manages the file browser and its filtering options."""

    register_cls = True
    is_custom_base_cls = False

    bl_idname = "tbb.import_telemac_file"
    bl_label = "Import"
    bl_description = "Import a TELEMAC file"

    #: bpy.props.StringProperty: List of allowed file extensions.
    filter_glob: StringProperty(
        default="*.slf",  # multiple allowed types: "*.slf;*.[];*.[]" etc ...
        options={"HIDDEN"}  # noqa: F821
    )

    #: bpy.props.StringProperty: Name to give to the imported object.
    name: StringProperty(
        name="Name",  # noqa F821
        description="Name to give to the imported object",
        default="TBB_TELEMAC_preview",  # noqa F821
    )

    #: TBB_TelemacImportSettings: Import settings.
    import_settings: PointerProperty(type=TBB_TelemacImportSettings)

    def execute(self, context: Context) -> set:
        """
        Import the selected file.

        It also generates the preview object, updates temporary data and 'dynamic' scene settings.

        Args:
            context (Context): context

        Returns:
            set: state of the operator
        """

        start = time.time()

        if not Path(self.filepath).exists() or Path(self.filepath).is_dir():
            self.report({'WARNING'}, "The chosen file can't be read")
            return {'CANCELLED'}

        # Generate parent object
        obj = bpy.data.objects.new(self.name, object_data=None)
        context.scene.collection.objects.link(obj)
        # Setup common settings
        obj.tbb.module = 'TELEMAC'
        obj.tbb.uid = str(time.time())
        obj.tbb.settings.file_path = self.filepath
        # Load temporary data
        context.scene.tbb.tmp_data[obj.tbb.uid] = TBB_TelemacTemporaryData(self.filepath,
                                                                           self.import_settings.compute_value_ranges)
        tmp_data = context.scene.tbb.tmp_data.get(obj.tbb.uid, None)
        obj.tbb.settings.telemac.is_3d_simulation = tmp_data.is_3d

        # Generate objects
        children = generate_base_objects(tmp_data, 0, self.name)
        # Link generated objects to main 'Null' object
        for child in children:
            context.scene.collection.objects.link(child)
            child.parent = obj

        log.info("{:.4f}".format(time.time() - start) + "s")
        self.report({'INFO'}, "File successfully imported")

        return {'FINISHED'}

    def draw(self, context: Context) -> None:
        """
        UI layout of the operator.

        Args:
            context (Context): context
        """

        # Import settings
        box = self.layout.box()
        row = box.row()
        row.label(text="Import")

        row = box.row()
        row.prop(self.import_settings, "compute_value_ranges", text="Compute value ranges")

        # Others
        box = self.layout.box()
        row = box.row()
        row.label(text="Others")

        row = box.row()
        row.prop(self, "name", text="Name")
